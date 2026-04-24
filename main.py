import streamlit as st
import pandas as pd
import config 
import manage_data
import time

st.set_page_config(page_title="FindeR", layout="wide")
st.title("FindeR")

if 'job_data' not in st.session_state:
    st.session_state.job_data = pd.DataFrame()

def show_data(df, placeholder):
    if df.empty:
        return
    placeholder.dataframe(
        df[config.DISPLAY_COLUMNS],
        column_config={
            "job_url": st.column_config.LinkColumn("Apply Link"),
            "date_posted": st.column_config.DateColumn("Posted"),
        },
        use_container_width=True,
        hide_index=True
    )
table_placeholder = st.empty()
if st.session_state.job_data.empty:
    status = st.empty()
    all_found_jobs = []
    
    for i, cat in enumerate(config.CATEGORIES):
        status.text(f"Scanning: {cat} ({i+1}/{len(config.CATEGORIES)})")

        df = manage_data.get_tech_jobs(cat)
        if not df.empty:
            all_found_jobs.append(df)
            st.session_state.job_data = pd.concat(all_found_jobs).drop_duplicates(subset=['job_url'])
            show_data(st.session_state.job_data, table_placeholder)
        
        time.sleep(1)
    
    status.empty()
    st.rerun()

if st.button("Refresh"):
    st.session_state.job_data = pd.DataFrame()
    st.rerun()


st.write(f"**{len(st.session_state.job_data)}** jobs found")
show_data(st.session_state.job_data, table_placeholder)
