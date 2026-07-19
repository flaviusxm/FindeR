from abc import ABC,abstractmethod
from models.job import Job
class AbstractScraper(ABC):

    def __init__(self,source):
        self.source=source

    @abstractmethod
    def get_jobs(self,category)->list:
        pass

    def create_job(self,title,company,location,date_posted,job_url,category):
        return Job(title=title,company=company,location=location,date_posted=date_posted,job_url=job_url,source=self.source,category=category)
