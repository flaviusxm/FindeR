import urllib.parse
import json
from curl_cffi import requests
from bs4 import BeautifulSoup
from scrapers.abstract_scraper import AbstractScraper
from models.job import Job

class BestjobsScraper(AbstractScraper):
    def __init__(self):
        super().__init__("BestJobs")

    def get_jobs(self, query: str = "", location: str = "Romania", limit: int = 25) -> list[Job]:
        jobs_list: list[Job] = []
        raw_query = query.strip()
        slug = urllib.parse.quote_plus(raw_query) if raw_query else "it"

        url = f"https://www.bestjobs.eu/locuri-de-munca/{slug}?sort=recent"

        try:
            resp = requests.get(url, impersonate="chrome120", timeout=12)
            if resp.status_code != 200:
                return jobs_list

            soup = BeautifulSoup(resp.text, "html.parser")
            seen_urls = set()

            nd = soup.find("script", id="__NEXT_DATA__")
            if nd and nd.string:
                try:
                    data = json.loads(nd.string)
                    items = data.get("props", {}).get("pageProps", {}).get("jobListCardsFromServer", {}).get("items", [])
                    for it in items:
                        title = it.get("title") or it.get("name")
                        slug_val = it.get("slug")
                        if not title or not slug_val:
                            continue

                        company = it.get("companyName") or "Companie Confidențială"
                        locs = it.get("locations") or []
                        loc = locs[0].get("name") if locs and isinstance(locs[0], dict) else "România"

                        salary_info = it.get("salary")
                        salary = ""
                        if salary_info and isinstance(salary_info, dict):
                            salary = salary_info.get("formatted", "")

                        job_url = f"https://www.bestjobs.eu/loc-de-munca/{slug_val}"
                        if job_url in seen_urls:
                            continue
                        seen_urls.add(job_url)

                        jobs_list.append(
                            self.create_job(
                                title=str(title).strip(),
                                company=str(company).strip(),
                                location=str(loc).strip(),
                                date_posted="Activat recent",
                                job_url=job_url,
                                category=query or "IT & Inginerie",
                                salary=str(salary).strip()
                            )
                        )
                        if len(jobs_list) >= limit:
                            return jobs_list
                except Exception as ex_nd:
                    print(f"Eroare procesare NEXT_DATA BestJobs: {ex_nd}")

            if not jobs_list:
                anchors = [a for a in soup.find_all("a") if isinstance(a.get("href"), str) and "/loc-de-munca/" in str(a.get("href"))]
                for a in anchors:
                    raw_href = a.get("href")
                    href = raw_href if isinstance(raw_href, str) else ""
                    if not href:
                        continue
                    if not href.startswith("http"):
                        href = f"https://www.bestjobs.eu{href}"

                    if href in seen_urls:
                        continue
                    seen_urls.add(href)

                    parent = a.parent
                    lines = list(parent.stripped_strings) if parent else []
                    raw_aria = a.get("aria-label")
                    aria_str = raw_aria if isinstance(raw_aria, str) else ""
                    title = aria_str or (lines[0] if lines else "Job Nou")
                    company = lines[2] if len(lines) > 2 else "Companie Parteneră"
                    loc = lines[3] if len(lines) > 3 else "România"

                    jobs_list.append(
                        self.create_job(
                            title=title,
                            company=company,
                            location=loc,
                            date_posted="Activat recent",
                            job_url=href,
                            category=query or "IT & Inginerie"
                        )
                    )
                    if len(jobs_list) >= limit:
                        break

        except Exception as e:
            print(f"Eroare scraping BestJobs: {e}")

        return jobs_list
