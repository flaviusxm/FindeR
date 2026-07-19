from scrapers.juniors import JuniorsScraper

scraper = JuniorsScraper()

jobs = scraper.get_jobs("Python Developer")

print(jobs)
