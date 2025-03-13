import streamlit as st
import sys
from utils import StreamToExpander, show_confetti, markdown_to_pdf, get_pdf_download_link
from crawler_handler import run_analysis
from config import REPORT_DIR
from datetime import datetime
import os

st.set_page_config(page_title="Competitor Analysis Dashboard", layout="wide", initial_sidebar_state="expanded")

st.sidebar.title("Reports")
if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)

report_files = [f for f in os.listdir(REPORT_DIR) if f.endswith(".md")]
report_dates = [datetime.strptime(f.split("_")[2] + "_" + f.split("_")[3].replace(".md", ""), "%Y%m%d_%H%M%S") for f in report_files]


min_date = min(report_dates) if report_dates else datetime.now()
max_date = max(report_dates) if report_dates else datetime.now()
date_range = st.sidebar.date_input("Filter by Date", [min_date, max_date], min_value=min_date, max_value=max_date)

if len(date_range) < 2 or date_range[1] is None:
    date_range = [date_range[0], date_range[0]]

filtered_reports = [
    f for f, d in zip(report_files, report_dates)
    if date_range[0] <= d.date() <= date_range[1]
]
selected_report = st.sidebar.selectbox("Select a Report", filtered_reports)

st.title("Competitor Analysis Dashboard")
st.markdown("Analyze competitor pricing and promotions with a single click!")

if st.button("Run Competitor Analysis"):
    st.empty()
    expander = st.expander("Processing Log", expanded=True)
    with st.spinner("Running analysis..."):
        original_stdout = sys.stdout
        stream_to_expander = StreamToExpander(expander, st)
        sys.stdout = stream_to_expander
        try:
            new_report_file = run_analysis()
            if new_report_file:
                logs = stream_to_expander.get_logs()
                report_files.append(os.path.basename(new_report_file))
                expander_expanded = False
                st.success("Analysis complete! Check your Mailtrap inbox and the reports list.")
                show_confetti()

                with open("temp_logs.txt", "w", encoding="utf-8") as f:
                    f.write(logs)
                st.rerun()
        except Exception as e:
            st.error(f"Error during analysis: {e}")
        finally:
            sys.stdout = original_stdout

if os.path.exists("temp_logs.txt"):
    with open("temp_logs.txt", "r", encoding="utf-8") as f:
        logs_content = f.read()
    if logs_content:
        expander = st.expander("Processing Log", expanded=False)
        expander.markdown(logs_content, unsafe_allow_html=True)

    os.remove("temp_logs.txt")

if selected_report:
    with open(os.path.join(REPORT_DIR, selected_report), "r") as f:
        report_content = f.read()
    st.markdown("### Selected Report")
    st.markdown(report_content, unsafe_allow_html=True)

    pdf_path = os.path.join(REPORT_DIR, selected_report.replace(".md", ".pdf"))
    markdown_to_pdf(report_content, pdf_path)
    st.markdown(get_pdf_download_link(pdf_path, selected_report.replace(".md", ".pdf")), unsafe_allow_html=True)

st.markdown(
    """
    <style>
    /* Existing styles */
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #ffffff;
        color: #4CAF50;
        border: 1px solid #4CAF50;
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

    /* Log container styling */
    .log-container {
        width: 100%; /* Fill the full width of the expander */
        padding: 10px;
        background-color: #fff;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    /* Log entry styling */
    .log-entry {
        margin-bottom: 8px;
        padding: 8px 12px;
        border-left: 4px solid;
        border-radius: 4px;
        animation: fadeIn 0.3s ease-in;
        word-break: break-word;
    }

    /* Fade-in animation */
    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
    </style>
    """,
    unsafe_allow_html=True
)