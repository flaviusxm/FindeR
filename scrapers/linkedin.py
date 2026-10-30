import urllib.parse
import requests
from bs4 import BeautifulSoup
from scrapers.abstract_scraper import AbstractScraper
from models.job import Job

class LinkedinScraper(AbstractScraper):
    def __init__(self):
        super().__init__("LinkedIn")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

    def _scrape_page(self, url: str, query: str, seen_urls: set, limit: int) -> list[Job]:
        results = []
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code != 200:
                return results

            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.find_all("li")

            for c in cards:
                title_elem = c.find("h3", class_="base-search-card__title")
                comp_elem = c.find("h4", class_="base-search-card__subtitle")
                loc_elem = c.find("span", class_="job-search-card__location")
                link_elem = c.find("a", class_="base-card__full-link")
                date_elem = c.find("time")

                title = title_elem.text.strip() if title_elem else ""
                if not title:
                    continue

                raw_dt = date_elem.get("datetime") if date_elem else ""
                datetime_attr = raw_dt if isinstance(raw_dt, str) else ""
                date_text = date_elem.text.strip() if date_elem else ""
                date_posted = datetime_attr or date_text or "Astăzi"

                date_lower = date_posted.lower() + " " + date_text.lower()
                if any(w in date_lower for w in ["month", "months", "year", "years", "luni", "an "]):
                    continue

                raw_href = link_elem.get("href") if link_elem else ""
                job_url = raw_href if isinstance(raw_href, str) else ""
                if "?" in job_url:
                    job_url = job_url.split("?")[0]

                if not job_url or job_url in seen_urls:
                    continue

                seen_urls.add(job_url)
                company = comp_elem.text.strip() if comp_elem else "Companie Confidențială"
                job_loc = loc_elem.text.strip() if loc_elem else "România"

                results.append(
                    self.create_job(
                        title=title,
                        company=company,
                        location=job_loc,
                        date_posted=date_posted,
                        job_url=job_url,
                        category=query or "IT & Inginerie"
                    )
                )

                if len(results) >= limit:
                    break
        except Exception as e:
            print(f"Eroare pagină LinkedIn: {e}")

        return results

    def get_jobs(self, query: str = "", location: str = "Romania", limit: int = 25) -> list[Job]:
        jobs_list: list[Job] = []
        seen_urls = set()
        q = urllib.parse.quote_plus(query.strip()) if query else "software"
        loc = urllib.parse.quote_plus(location.strip()) if location and location.lower() != "toată românia" else "Romania"

        url_today = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={q}&location={loc}&f_TPR=r86400&sortBy=DD&start=0"
        jobs_today = self._scrape_page(url_today, query, seen_urls, limit)
        jobs_list.extend(jobs_today)

        if len(jobs_list) < limit:
            remaining = limit - len(jobs_list)
            url_week = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={q}&location={loc}&f_TPR=r604800&sortBy=DD&start=0"
            jobs_week = self._scrape_page(url_week, query, seen_urls, remaining)
            jobs_list.extend(jobs_week)

        return jobs_list
