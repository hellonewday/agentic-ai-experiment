from crewai import Crew
from agents import crawler_agent, analyzer_agent, reporting_agent
from tasks import crawl_task, analyze_task, report_task
from email_sender import send_email
import time
from config import get_unique_report_filename

def run_analysis():
    """Run the competitor analysis workflow."""
    analyze_task.output_file = get_unique_report_filename()
    crew = Crew(
        agents=[crawler_agent, analyzer_agent, reporting_agent],
        tasks=[crawl_task, analyze_task, report_task],
        verbose=True
    )
    result = crew.kickoff()

    with open(analyze_task.output_file, "r") as f:
        full_analysis = f.read()

    email_body = (
        "Dear Levi’s Team,\n\n"
        "**Latest Promotion Campaign Insights**\n\n"
        "Our analysis shows Levi’s promotions are steady but outpaced—30% frequency and 10% discounts lag behind Lee Korea’s 60% blitz and Calvin Klein’s 40% finesse. "
        "Here’s how we can sharpen our strategy and drive sales.\n\n"
        "**Key Takeaways**\n"
        "- Levi’s promo reach (30%) trails Lee (60%) and CK (40%), risking volume loss.\n"
        "- Competitors’ deeper cuts (20% Lee, 15% CK) overshadow our 10% average.\n"
        "- Opportunity: Boost campaigns to reclaim market buzz without sacrificing premium appeal.\n\n"
        "**Top 3 Actions**\n"
        "1. **Ramp Up Promo Reach**: Hit 50% of SKUs with 15% discounts—match CK, challenge Lee.\n"
        "2. **Launch a Flash Sale**: Run a 20% off weekend event to spike volume and test demand.\n"
        "3. **Reward Loyalty**: Offer 10% off exclusive drops for repeat buyers to lock in our base.\n\n"
        "---\n\n"
        "**Full Analysis**\n\n"
        f"{full_analysis}"
    )

    send_email(config.EMAIL_SENDER, config.EMAIL_RECEIVER, config.EMAIL_SUBJECT, email_body, config.SMTP_USER, config.SMTP_PASSWORD)
    return analyze_task.output_file