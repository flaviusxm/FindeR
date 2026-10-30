import urllib.parse
import requests
from bs4 import BeautifulSoup
from scrapers.abstract_scraper import AbstractScraper
from models.job import Job

class JuniorsScraper(AbstractScraper):
    def __init__(self):
        super().__init__("Juniors.ro")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }

    def _extract_jobs_from_soup(self, soup: BeautifulSoup, seen_urls: set, limit: int, query: str = "") -> list[Job]:
        results = []
        job_items = soup.find_all("li", class_="job")

        for j in job_items:
            title_elem = j.find("h3")
            title = title_elem.text.strip() if title_elem else "Junior Position"

            link = j.find("a", class_="btn-url")
            if not link:
                for a in j.find_all("a"):
                    h_val = a.get("href")
                    if isinstance(h_val, str) and "/jobs/" in h_val and "q=" not in h_val:
                        link = a
                        break

            raw_href = link.get("href") if link else ""
            job_url = raw_href if isinstance(raw_href, str) else ""
            if job_url and not job_url.startswith("http"):
                job_url = f"https://juniors.ro{job_url}"

            if not job_url or job_url in seen_urls:
                continue

            info_elem = j.find("strong")
            loc, date_posted = "România", "Astăzi"
            if info_elem:
                parts = info_elem.text.strip().split("|")
                if len(parts) > 0 and parts[0].strip():
                    loc = parts[0].strip()
                if len(parts) > 1 and parts[1].strip():
                    raw_d = parts[1].strip()
                    if "ast" in raw_d.lower():
                        date_posted = "Astăzi"
                    elif "1 zi" in raw_d.lower() or "ieri" in raw_d.lower():
                        date_posted = "1 zi în urmă"
                    else:
                        date_posted = raw_d.replace("ã", "ă").replace("\n", " ").strip()

            company = "Companie Confidențială"
            for li_sub in j.find_all("li"):
                txt = li_sub.text.strip()
                if "Companie:" in txt:
                    company = txt.replace("Companie:", "").strip()

            tags: list[str] = []
            for a in j.find_all("a"):
                h_val = a.get("href")
                if isinstance(h_val, str) and "?q=" in h_val:
                    tags.append(a.text.strip())
            category_display = ", ".join(tags) if tags else (query or "Junior IT & Engineering")

            seen_urls.add(job_url)
            job = self.create_job(
                title=title,
                company=company,
                location=loc,
                date_posted=date_posted,
                job_url=job_url,
                category=category_display
            )
            results.append(job)

            if len(results) >= limit:
                break

        return results

    def get_jobs(self, query: str = "", location: str = "Romania", limit: int = 15) -> list[Job]:
        jobs_list: list[Job] = []
        seen_urls = set()
        clean_q = query.strip()

        if clean_q:
            encoded = urllib.parse.quote_plus(clean_q)
            url_query = f"https://juniors.ro/jobs?q={encoded}"
            try:
                resp = requests.get(url_query, headers=self.headers, timeout=10)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    jobs_list.extend(self._extract_jobs_from_soup(soup, seen_urls, limit, clean_q))
            except Exception as e:
                print(f"Eroare căutare Juniors: {e}")

        if len(jobs_list) < limit:
            try:
                resp_home = requests.get("https://juniors.ro/jobs", headers=self.headers, timeout=10)
                if resp_home.status_code == 200:
                    soup_home = BeautifulSoup(resp_home.text, "html.parser")
                    remaining = limit - len(jobs_list)
                    home_jobs = self._extract_jobs_from_soup(soup_home, seen_urls, remaining, clean_q)
                    
                    if clean_q:
                        q_words = [w.lower() for w in clean_q.split() if len(w) > 2]
                        for hj in home_jobs:
                            txt_check = (hj.title + " " + hj.category).lower()
                            if any(w in txt_check for w in q_words) or hj.date_posted == "Astăzi":
                                jobs_list.append(hj)
                    else:
                        jobs_list.extend(home_jobs)
            except Exception as e:
                print(f"Eroare home Juniors: {e}")

        return jobs_list
