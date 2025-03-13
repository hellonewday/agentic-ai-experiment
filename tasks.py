from crewai import Task
from agents import crawler_agent, analyzer_agent, reporting_agent
from datetime import datetime
import os

if not os.path.exists("reports"):
    os.makedirs("reports")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
analysis_output_file = f"reports/competitor_analysis_{timestamp}.md"

crawl_task = Task(
    description="Crawl Levi's Korea, Lee Korea, and Calvin Klein Korea websites to extract and clean product information including names, prices, and promotions",
    agent=crawler_agent,
    expected_output="A list of dictionaries containing cleaned product information from all three sources"
)

analyze_task = Task(
    description=(
        "Analyze the cleaned product data from Levi's Korea, Lee Korea, and Calvin Klein Korea to evaluate Levi’s denim promotion campaigns against competitors, focusing on data-driven insights:\n"
        "1. Compute the following metrics for each brand (Levi’s, Lee, Calvin Klein):\n"
        "   - Average price of products.\n"
        "   - Price range (minimum and maximum prices).\n"
        "   - Promotion frequency (percentage of products with any promotion).\n"
        "   - Average discount depth (average percentage discount for promoted products).\n"
        "2. Present these metrics in a clear Markdown table for each brand.\n"
        "3. Provide data-driven insights by comparing Levi’s metrics to Lee and Calvin Klein, focusing on:\n"
        "   - Price positioning (e.g., is Levi’s premium, mid-tier, or budget compared to competitors?).\n"
        "   - Promotion aggressiveness (e.g., does Levi’s offer more or fewer promotions, and are discounts deeper or shallower?).\n"
        "   - Competitive gaps (e.g., where does Levi’s lag or lead in pricing or promotions?).\n"
        "4. Propose 3-5 concise, data-backed recommendations to improve Levi’s promotion campaigns, directly tied to the metrics (e.g., 'Increase promotion frequency to match Lee’s 60% to capture more budget-conscious customers').\n"
        "Write in a concise, analytical tone, prioritizing clarity and precision over narrative flair. Ensure all insights and recommendations are grounded in the computed metrics."
    ),
    agent=analyzer_agent,
    expected_output=(
        f"A Markdown file ('{analysis_output_file}') with:\n"
        "   - **Summary Table**: A table showing average price, price range, promotion frequency, and average discount depth for Levi’s, Lee, and Calvin Klein.\n"
        "   - **Insights**: 3-4 sentences comparing Levi’s metrics to competitors, focusing on price positioning, promotion aggressiveness, and competitive gaps.\n"
        "   - **Recommendations**: 3-5 numbered recommendations to improve Levi’s promotion campaigns, each backed by specific data from the table.\n"
        "   - Ensure all insights and recommendations are directly tied to the data in the table, avoiding vague or speculative statements."
    ),
    output_file=analysis_output_file
)

report_task = Task(
    description=(
        f"Take the analysis from '{analysis_output_file}' and craft a concise, professional email body for Levi's data analysts and staff:\n"
        "1. Extract the summary table (average price, price range, promotion frequency, average discount depth) and include it in the email body as a Markdown table.\n"
        "2. Highlight the top 3 recommendations from the analysis, formatted as a numbered list.\n"
        "3. Append the entire Markdown content from '{analysis_output_file}' below a separator (e.g., '--- Full Analysis ---').\n"
        "Write in a concise, professional tone, focusing on the data and actionable steps. Send the email via Mailtrap SMTP using provided credentials, and log the action in 'email_report.log'."
    ),
    agent=reporting_agent,
    expected_output=(
        "A professional email sent to sales_team@levi.kr, analytics_team@levi.kr, marketing_team@levi.kr with subject 'Levi’s Promotion Campaign Insights - Weekly Report', containing:\n"
        "   - A brief introduction (1-2 sentences) stating the purpose of the report.\n"
        "   - A Markdown table summarizing the key metrics (average price, price range, promotion frequency, average discount depth) for Levi’s, Lee, and Calvin Klein.\n"
        "   - A numbered list of the top 3 recommendations.\n"
        "   - The full analysis appended below a separator."
    )
)