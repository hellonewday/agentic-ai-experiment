import logging
from datetime import datetime
from dotenv import load_dotenv
import os
import pdfkit

load_dotenv()

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="competitor_crawler.log"
)

# Constants
REPORT_DIR = "reports"
if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)

EMAIL_SENDER = "Levis Data Team <hungnq.11198@gmail.com>"
EMAIL_RECEIVER = "Levis Staff <staff@levis.co.kr>"
EMAIL_SUBJECT = "Levi’s Promotion Campaign Insights - Weekly Report"
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# wkhtmltopdf configuration for Windows - Comment this when running on Ubuntu
# path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
# CONFIG = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

def get_unique_report_filename():
    return f"{REPORT_DIR}/competitor_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"