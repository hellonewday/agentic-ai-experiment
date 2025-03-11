import streamlit as st
import os
from config import logging, REPORT_DIR, CONFIG
from crawler_handler import run_analysis
from utils import StreamlitLogHandler, show_confetti, markdown_to_pdf, get_pdf_download_link
from datetime import datetime
import time

# Streamlit app layout
st.set_page_config(page_title="Competitor Analysis Dashboard", layout="wide", initial_sidebar_state="expanded")

# Sidebar: Report list with date filter
st.sidebar.title("Reports")
if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)

report_files = [f for f in os.listdir(REPORT_DIR) if f.endswith(".md")]
report_dates = [datetime.strptime(f.split("_")[2] + "_" + f.split("_")[3].replace(".md", ""), "%Y%m%d_%H%M%S") for f in report_files]

# Date filter
min_date = min(report_dates) if report_dates else datetime.now()
max_date = max(report_dates) if report_dates else datetime.now()
date_range = st.sidebar.date_input("Filter by Date", [min_date, max_date], min_value=min_date, max_value=max_date)

filtered_reports = [
    f for f, d in zip(report_files, report_dates)
    if date_range[0] <= d.date() <= date_range[1]
]
selected_report = st.sidebar.selectbox("Select a Report", filtered_reports)

# Main panel
st.title("Competitor Analysis Dashboard")
st.markdown("Analyze competitor pricing and promotions with a single click!")

# Run analysis button at the top
if st.button("Run Competitor Analysis"):
    # Clear the selected report content
    st.empty()
    log_container = st.empty()
    handler = StreamlitLogHandler(log_container)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logging.getLogger().addHandler(handler)

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        status_text.text("Starting competitor analysis...")
        progress_bar.progress(10)
        time.sleep(0.5)

        new_report_file = run_analysis()

        status_text.text("Analysis complete! 🎉")
        progress_bar.progress(100)
        time.sleep(0.5)
        show_confetti()
        st.success("Analysis complete! Check your Mailtrap inbox and the reports list.")
        if new_report_file:
            st.rerun()

    except Exception as e:
        logging.error(f"Error during analysis: {str(e)}")
        st.error(f"Error: {e}")
        progress_bar.progress(0)
    finally:
        logging.getLogger().removeHandler(handler)

# Display selected report
if selected_report:
    with open(os.path.join(REPORT_DIR, selected_report), "r") as f:
        report_content = f.read()
    st.markdown(report_content, unsafe_allow_html=True)

    # Generate and offer PDF download
    pdf_path = os.path.join(REPORT_DIR, selected_report.replace(".md", ".pdf"))
    markdown_to_pdf(report_content, pdf_path)
    st.markdown(get_pdf_download_link(pdf_path, selected_report.replace(".md", ".pdf")), unsafe_allow_html=True)

# Styling with white hover
st.markdown(
    """
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #ffffff; /* White on hover */
        color: #4CAF50; /* Green text to contrast white background */
        border: 1px solid #4CAF50; /* Green border for visibility */
    }
    .stSidebar {
        background-color: #f8f9fa;
    }
    .stProgress .st-bo {
        background-color: #4CAF50;
    }
    body {
        font-family: 'Arial', sans-serif;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    </style>
    """,
    unsafe_allow_html=True
)