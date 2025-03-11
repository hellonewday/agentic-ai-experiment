import logging
import streamlit as st
from streamlit.components.v1 import html
import pdfkit
from config import CONFIG
import base64
import markdown

class StreamlitLogHandler(logging.Handler):
    """Custom handler to stream logs to Streamlit."""
    def __init__(self, streamlit_container):
        super().__init__()
        self.container = streamlit_container
        self.logs = []

    def emit(self, record):
        log_entry = self.format(record)
        self.logs.append(log_entry)
        self.container.text_area("CrewAI Reasoning", "\n".join(self.logs), height=300)

def show_confetti():
    """Display confetti animation on success."""
    confetti_code = """
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
    <script>
        setTimeout(() => {
            confetti({
                particleCount: 100,
                spread: 70,
                origin: { y: 0.6 }
            });
        }, 500);
    </script>
    """
    html(confetti_code)

def markdown_to_pdf(markdown_content, output_path):
    """Convert Markdown to PDF."""
    pdfkit.from_string(markdown.markdown(markdown_content, extensions=['markdown.extensions.tables']), output_path, configuration=CONFIG)

def get_pdf_download_link(file_path, filename):
    """Generate a downloadable PDF link."""
    with open(file_path, "rb") as f:
        pdf_data = f.read()
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Download PDF</a>'
    return href