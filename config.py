import logging
from datetime import datetime
import os
import pdfkit

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
SMTP_USER = "07e58258e03ad3"
SMTP_PASSWORD = "28bb032eaf39f5"

# wkhtmltopdf configuration for Windows - Comment this when running on Ubuntu
# path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
# CONFIG = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

def get_unique_report_filename():
    return f"{REPORT_DIR}/competitor_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"