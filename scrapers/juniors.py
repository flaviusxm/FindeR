from scrapers.abstract_scraper import AbstractScraper

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


class JuniorsScraper(AbstractScraper):

    def __init__(self):
        super().__init__("Juniors.ro")


    def get_jobs(self, category):

        jobs_list = []

        with sync_playwright() as pw:

            browser = pw.chromium.launch()

            page = browser.new_page()

            page.goto(
                "https://juniors.ro/jobs"
            )

            html = page.content()

            browser.close()


        soup = BeautifulSoup(
            html,
            "html.parser"
        )


        jobs = soup.find_all(
            "li",
            class_="job"
        )


        for j in jobs:

            title = j.find("h3").text.strip()


            info = j.find("strong").text.strip()

            location = info.split("|")[0].strip()

            date_posted = info.split("|")[1].strip()


            company = ""

            for li in j.find_all("li"):

                if "Companie:" in li.text:
                    company = li.text.replace(
                        "Companie:",
                        ""
                    ).strip()


            link = j.find(
                "a",
                class_="btn-url"
            )

            if link:
                url = link.get("href")
            else:
                url = ""


            jobs_list.append(
                self.create_job(
                    title,
                    company,
                    location,
                    date_posted,
                    url,
                    category
                )
            )


        return jobs_list
