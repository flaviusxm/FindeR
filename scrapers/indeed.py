from jobspy import scrape_jobs
from scrapers.abstract_scraper import AbstractScraper
from models.job import Job

class IndeedScraper(AbstractScraper):
    def __init__(self):
        super().__init__("Indeed")

    def get_jobs(self, query: str = "", location: str = "Romania", limit: int = 25) -> list[Job]:
        jobs_list: list[Job] = []
        search_query = query.strip() if query else "Software Engineer"
        loc = location.strip() if location and location.lower() != "toată românia" else "Romania"

        for hours in [48, 168]:
            if len(jobs_list) >= limit:
                break
            try:
                df = scrape_jobs(
                    site_name=["indeed"],
                    search_term=search_query,
                    location=loc,
                    results_wanted=min(limit, 30),
                    country_indeed="Romania",
                    is_remote=(True if "remote" in loc.lower() else False),
                    hours_old=hours
                )

                if df is not None and not df.empty:
                    seen_urls = {j.job_url for j in jobs_list}
                    for _, row in df.iterrows():
                        job_url = str(row.get("job_url", "")).strip()
                        if not job_url or job_url in seen_urls:
                            continue

                        title = str(row.get("title", "")).strip()
                        company = str(row.get("company", "")).strip()
                        job_location = str(row.get("location", "")).strip() or "România"
                        raw_date = row.get("date_posted")
                        date_posted = str(raw_date).strip() if raw_date is not None else "Astăzi"

                        salary = ""
                        min_amt = row.get("min_amount")
                        max_amt = row.get("max_amount")
                        curr = row.get("currency", "EUR")
                        if min_amt and max_amt:
                            salary = f"{min_amt} - {max_amt} {curr}"
                        elif min_amt:
                            salary = f"De la {min_amt} {curr}"

                        if title:
                            seen_urls.add(job_url)
                            jobs_list.append(
                                self.create_job(
                                    title=title,
                                    company=company or "Companie Confidențială",
                                    location=job_location,
                                    date_posted=date_posted,
                                    job_url=job_url,
                                    category=query or "IT & Inginerie",
                                    salary=salary
                                )
                            )
                            if len(jobs_list) >= limit:
                                break

            except Exception as e:
                print(f"Eroare scraping Indeed: {e}")
                break

        return jobs_list
