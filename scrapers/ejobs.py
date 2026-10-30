import urllib.parse
import json
from curl_cffi import requests
from bs4 import BeautifulSoup
from scrapers.abstract_scraper import AbstractScraper
from models.job import Job

class EjobsScraper(AbstractScraper):
    def __init__(self):
        super().__init__("eJobs")

    def get_jobs(self, query: str = "", location: str = "Romania", limit: int = 30) -> list[Job]:
        jobs_list: list[Job] = []
        raw_query = query.strip()

        if not raw_query or raw_query.lower() in ["it", "software", "software engineer"]:
            slug = "it-software"
        elif raw_query.lower() in ["inginerie", "engineering", "mecanic"]:
            slug = "inginerie"
        else:
            slug = urllib.parse.quote_plus(raw_query)

        url = f"https://www.ejobs.ro/locuri-de-munca/{slug}/?criteriu=data_adaugarii"

        try:
            resp = requests.get(url, impersonate="chrome120", timeout=12)
            if resp.status_code != 200:
                url_fallback = f"https://www.ejobs.ro/locuri-de-munca/{slug}/"
                resp = requests.get(url_fallback, impersonate="chrome120", timeout=12)
                if resp.status_code != 200:
                    return jobs_list

            soup = BeautifulSoup(resp.text, "html.parser")
            seen_urls = set()

            s_nuxt = soup.find("script", id="__NUXT_DATA__")
            if s_nuxt and s_nuxt.string:
                try:
                    data = json.loads(s_nuxt.string)
                    for item in data:
                        if isinstance(item, dict) and "title" in item and "slug" in item and "creationDate" in item:
                            t_idx = item["title"]
                            title = data[t_idx] if isinstance(t_idx, int) and t_idx < len(data) else t_idx
                            if not title:
                                continue

                            c_idx = item.get("company")
                            comp_obj = data[c_idx] if isinstance(c_idx, int) and c_idx < len(data) else c_idx
                            comp_name = "Companie Parteneră"
                            if isinstance(comp_obj, dict) and "name" in comp_obj:
                                n_idx = comp_obj["name"]
                                comp_name = data[n_idx] if isinstance(n_idx, int) and n_idx < len(data) else n_idx

                            d_idx = item.get("creationDate")
                            date_val = data[d_idx] if isinstance(d_idx, int) and d_idx < len(data) else d_idx

                            slug_idx = item.get("slug")
                            slug_val = data[slug_idx] if isinstance(slug_idx, int) and slug_idx < len(data) else slug_idx

                            id_idx = item.get("id")
                            id_val = data[id_idx] if isinstance(id_idx, int) and id_idx < len(data) else id_idx

                            job_url = f"https://www.ejobs.ro/user/locuri-de-munca/{slug_val}/{id_val}"
                            if job_url in seen_urls:
                                continue
                            seen_urls.add(job_url)

                            jobs_list.append(
                                self.create_job(
                                    title=str(title).strip(),
                                    company=str(comp_name).strip(),
                                    location="România",
                                    date_posted=str(date_val).strip() if date_val else "Astăzi",
                                    job_url=job_url,
                                    category=query or "IT & Inginerie"
                                )
                            )
                            if len(jobs_list) >= limit:
                                return jobs_list
                except Exception as ex_nuxt:
                    print(f"Eroare procesare Nuxt eJobs: {ex_nuxt}")

            if not jobs_list:
                for card in soup.select(".job-card"):
                    title_el = card.select_one('a[data-testid="b2c-job-card-title-link"], h2 a')
                    comp_el = card.select_one("h3 a, h3")
                    loc_el = card.select_one(".job-card-content-middle__info:not(h3)")
                    date_el = card.select_one(".job-card-content-top__date")

                    title = title_el.text.strip() if title_el else ""
                    raw_href = title_el.get("href") if title_el else ""
                    href = raw_href if isinstance(raw_href, str) else ""
                    if href and not href.startswith("http"):
                        href = f"https://www.ejobs.ro{href}"
                    company = comp_el.text.strip() if comp_el else "Companie Parteneră"
                    loc = loc_el.text.strip() if loc_el else "România"
                    date_posted = date_el.text.strip() if date_el else "Astăzi"

                    if href and href not in seen_urls and title:
                        seen_urls.add(href)
                        jobs_list.append(
                            self.create_job(
                                title=title,
                                company=company,
                                location=loc,
                                date_posted=date_posted,
                                job_url=href,
                                category=query or "IT & Inginerie"
                            )
                        )
                        if len(jobs_list) >= limit:
                            break

        except Exception as e:
            print(f"Eroare scraping eJobs: {e}")

        return jobs_list
