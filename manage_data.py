import pandas as pd
from jobspy import scrape_jobs
import config

def get_tech_jobs(index):
    """
    Extrage joburile pentru o anumită categorie bazată pe index.
    """
    category = config.CATEGORIES[index]
    try:
        jobs = scrape_jobs(
            site_name=config.SITES,
            search_term=category,
            location=config.LOCATION,
            results_wanted=config.RESULTS_PER_PAGE,
            country_indeed=config.LOCATION,
            hours_old=config.HOURS_OLD
        )
        if not jobs.empty:
            # Adăugăm sursa pentru a putea filtra ulterior în UI
            jobs['source_cat'] = category
            # Returnăm doar coloanele de interes definite în config
            return jobs[config.DISPLAY_COLUMNS + ['source_cat']]
    except Exception as e:
        print(f"Scraping error for {category}: {e}")
    return pd.DataFrame()