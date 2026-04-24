import pandas as pd
from jobspy import scrape_jobs
import config
import time

def get_tech_jobs(category):
  
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
            jobs['source_cat'] = category
            return jobs[config.DISPLAY_COLUMNS + ['source_cat']]
    except Exception as e:
        print(f"Scraping error for {category}: {e}")
    return pd.DataFrame()

def fetch_all_categories(progress_callback=None):
    """
    Parcurge toate categoriile și cumulează rezultatele.
    """
    all_jobs = []
    total = len(config.CATEGORIES)
    
    for i, cat in enumerate(config.CATEGORIES):
        if progress_callback:
            progress_callback(i + 1, total, cat)
        
        df = get_tech_jobs(cat)
        if not df.empty:
            all_jobs.append(df)

        time.sleep(1)
    if all_jobs:
        combined_df = pd.concat(all_jobs).drop_duplicates(subset=['job_url'])
        return combined_df
    return pd.DataFrame()