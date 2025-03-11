## For experimental purpose
import logging
from crewai import Crew
from agents import crawler_agent, analyzer_agent, reporting_agent
from tasks import crawl_task, analyze_task, report_task
from email_sender import send_email
from config import SMTP_USER, SMTP_PASSWORD
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="competitor_crawler.log"
)

def run_competitor_analysis():
    crew = Crew(
        agents=[crawler_agent, analyzer_agent, reporting_agent],
        tasks=[crawl_task, analyze_task, report_task],
        verbose=True
    )
    result = crew.kickoff()

    try:
        with open(analyze_task.output_file, "r") as f:
            full_analysis = f.read()

        sender = "Levis Data Team <hungnq.11198@gmail.com>"
        receiver = "Levis Staff <staff@levis.co.kr>"
        subject = "Levi’s Promotion Campaign Insights - Weekly Report"

        send_email(sender, receiver, subject, full_analysis, SMTP_USER, SMTP_PASSWORD)
    except Exception as e:
        logging.error(f"Error processing results or sending email: {str(e)}")
        print(f"Error processing results or sending email: {e}")

if __name__ == "__main__":
    print("Starting competitor product analysis...")
    logging.info("Starting new competitor analysis run")
    run_competitor_analysis()
    print("✅ Analysis complete!")