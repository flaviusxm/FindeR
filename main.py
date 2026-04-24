import streamlit as st
import pandas as pd
import config 
import manage_data
from datetime import datetime

st.set_page_config(page_title="FindeR", layout="wide")


if 'job_data' not in st.session_state:
    st.session_state.job_data = pd.DataFrame()

st.title("FindeR")

table_placeholder = st.empty()

if st.session_state.job_data.empty:
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total = len(config.CATEGORIES)
    all_found_jobs = []
    
    for i, cat in enumerate(config.CATEGORIES):
        percent = int(((i + 1) / total) * 100)
        progress_bar.progress(percent)
        status_text.text(f"Scanning: {cat} ({i+1}/{total})")

        df = manage_data.get_tech_jobs(cat)
        if not df.empty:
            all_found_jobs.append(df)
            current_combined = pd.concat(all_found_jobs).drop_duplicates(subset=['job_url'])
            st.session_state.job_data = current_combined

            table_placeholder.dataframe(
                current_combined[config.DISPLAY_COLUMNS + ['source_cat']],
                column_config={
                    "job_url": st.column_config.LinkColumn("Apply Link"),
                    "date_posted": st.column_config.DateColumn("Posted"),
                    "source_cat": "Category"
                },
                use_container_width=True,
                hide_index=True
            )
        
        import time
        time.sleep(1)
    st.rerun()

if st.button("Refresh"):
    st.session_state.job_data = pd.DataFrame()
    st.rerun()



    
st.write(f"**{len(df)}** jobs")
    
table_placeholder.dataframe(
        df[config.DISPLAY_COLUMNS + ['source_cat']],
        column_config={
            "job_url": st.column_config.LinkColumn("Apply Link"),
            "date_posted": st.column_config.DateColumn("Posted"),
            "source_cat": "Category"
        },
        use_container_width=True,
        hide_index=True
    )
