from dataclasses import dataclass

@dataclass
class Job:
    title:str
    company:str
    location:str
    date_posted:str
    job_url:str
    source:str
    category:str
