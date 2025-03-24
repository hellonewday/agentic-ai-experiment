from crewai import Crew
from agents import crawler_agent, analyzer_agent, reporting_agent
from tasks import crawl_task, analyze_task, report_task
from email_sender import send_email
from datetime import datetime

def run_analysis():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    analyze_task.output_file = f"reports/competitor_analysis_{timestamp}.md"

    crew = Crew(
        agents=[crawler_agent, analyzer_agent, reporting_agent],
        tasks=[crawl_task, analyze_task, report_task],
        verbose=True,
    )

    result = crew.kickoff()

    with open(analyze_task.output_file, "r") as f:
        full_analysis = f.read()

    sender = "Levis Data Team <hungnq.11198@gmail.com>"
    receiver = "Levis Staff <staff@levis.co.kr>"
    subject = "Levi’s Promotion Campaign Insights - Weekly Report"
    smtp_user = "07e58258e03ad3"
    smtp_password = "28bb032eaf39f5"
    send_email(sender, receiver, subject, full_analysis, smtp_user, smtp_password)

    return analyze_task.output_file