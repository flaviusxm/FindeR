import streamlit as st
import pandas as pd
from jobspy import scrape_jobs
import config 

st.set_page_config(page_title="FindeR", layout="wide")

if 'page_index' not in st.session_state: st.session_state.page_index = 0
if 'job_data' not in st.session_state: st.session_state.job_data = pd.DataFrame()

def fetch_data(index):
    cat = config.CATEGORIES[index]
    try:
        jobs = scrape_jobs(
            site_name=config.SITES,
            search_term=cat,
            location=config.LOCATION,
            results_wanted=config.RESULTS_PER_PAGE,
            country_indeed=config.LOCATION,
            hours_old=config.HOURS_OLD
        )
        if not jobs.empty:
            jobs['source_cat'] = cat
            return jobs[config.DISPLAY_COLUMNS + ['source_cat']]
    except Exception as e:
        st.error(f"Error {cat}: {e}")
    return pd.DataFrame()


if st.button("Refresh"):
    st.session_state.update(page_index=0, job_data=pd.DataFrame())
    st.rerun()


current_cat = config.CATEGORIES[st.session_state.page_index]

loaded_cats = st.session_state.job_data.get('source_cat', pd.Series()).values
if current_cat not in loaded_cats:
    with st.spinner("Fetching..."):
        new_data = fetch_data(st.session_state.page_index)
        st.session_state.job_data = pd.concat([st.session_state.job_data, new_data]).drop_duplicates(subset=['job_url'])


df = st.session_state.job_data[st.session_state.job_data['source_cat'] == current_cat]

if not df.empty:
    st.dataframe(df[config.DISPLAY_COLUMNS],column_config={"job_url": st.column_config.LinkColumn("Apply")},use_container_width=True, hide_index=True)
else:
    st.warning("No jobs found!")

st.markdown(f"<p style='text-align: center;'>Page {st.session_state.page_index + 1} / {len(config.CATEGORIES)}</p>", unsafe_allow_html=True)


_, col_prev, col_next, _ = st.columns([4, 1, 1, 4])

with col_prev:
    if st.button("Prev", disabled=st.session_state.page_index==0, use_container_width=True):
        st.session_state.page_index -= 1
        st.rerun()

with col_next:
    if st.button("Next", disabled=st.session_state.page_index==len(config.CATEGORIES)-1, use_container_width=True):
        st.session_state.page_index += 1
        st.rerun()