from jobspy import scrape_jobs
from scrapers.abstract_scraper import AbstractScraper
from models.job import Job

class JobSpyScraper(AbstractScraper):
    def __init__(self, platform: str):
        display_name = "LinkedIn" if platform.lower() == "linkedin" else "Indeed"
        super().__init__(display_name)
        self.platform = platform.lower()

    def get_jobs(self, query: str = "", location: str = "Romania", limit: int = 15) -> list[Job]:
        jobs_list: list[Job] = []
        search_query = query.strip() if query else "Software Engineer"
        loc = location.strip() if location and location.lower() != "toată românia" else "Romania"

        try:
            df = scrape_jobs(
                site_name=[self.platform],
                search_term=search_query,
                location=loc,
                results_wanted=min(limit, 25),
                country_indeed="Romania" if self.platform == "indeed" else None,
                is_remote=(True if "remote" in loc.lower() else False)
            )

            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    title = str(row.get("title", "")).strip()
                    company = str(row.get("company", "")).strip()
                    job_location = str(row.get("location", "")).strip() or "România"
                    date_posted = str(row.get("date_posted", "Recent")).strip()
                    job_url = str(row.get("job_url", "")).strip()
                    salary = ""
                    min_amt = row.get("min_amount")
                    max_amt = row.get("max_amount")
                    curr = row.get("currency", "EUR")
                    if min_amt and max_amt:
                        salary = f"{min_amt} - {max_amt} {curr}"
                    elif min_amt:
                        salary = f"De la {min_amt} {curr}"

                    if title and job_url:
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
            print(f"Error scraping {self.source} via JobSpy: {e}")

        return jobs_list
