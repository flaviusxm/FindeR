from abc import ABC, abstractmethod
from models.job import Job

class AbstractScraper(ABC):
    def __init__(self, source: str):
        self.source = source

    @abstractmethod
    def get_jobs(self, query: str, location: str = "Romania", limit: int = 15) -> list[Job]:
        pass

    def create_job(
        self,
        title: str,
        company: str,
        location: str,
        date_posted: str,
        job_url: str,
        category: str = "IT & Inginerie",
        salary: str = "",
        description: str = ""
    ) -> Job:
        return Job(
            title=title.strip() if title else "Titlu necunoscut",
            company=company.strip() if company else "Companie Confidențială",
            location=location.strip() if location else "România",
            date_posted=str(date_posted).strip() if date_posted else "Recent",
            job_url=job_url.strip() if job_url else "",
            source=self.source,
            category=category.strip() if category else "IT & Inginerie",
            salary=salary.strip() if salary else "",
            description=description.strip() if description else ""
        )
