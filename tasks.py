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
        "Analyze the cleaned product data from Levi's Korea, Lee Korea, and Calvin Klein Korea to evaluate Levi’s denim promotion campaigns against competitors, delivering a compelling, data-driven narrative for sales managers and data analyst leads:\n"
        "1. Compute the following metrics for each brand (Levi’s, Lee, Calvin Klein):\n"
        "   - Average price of products.\n"
        "   - Price range (minimum and maximum prices).\n"
        "   - Promotion frequency (percentage of products with any promotion).\n"
        "   - Average discount depth (average percentage discount for promoted products).\n"
        "2. Present these metrics in a clear Markdown table (no code block wrapping).\n"
        "3. Uncover pricing trends—assess where Levi’s sits (premium, mid-tier, budget) relative to Lee and Calvin Klein, using the table data to highlight competitive gaps.\n"
        "4. Evaluate promotion effectiveness—analyze the frequency, depth, and spread of promotions across each brand’s catalog, using the table to gauge impact on sales potential.\n"
        "5. Reveal campaign strengths—identify what Levi’s is doing right in its promotions and where it lags behind competitors, grounded in the data.\n"
        "6. Expose vulnerabilities—pinpoint where Lee and Calvin Klein’s promotion strategies threaten Levi’s market share, backed by the table metrics.\n"
        "7. Propose 5-7 precise, data-backed recommendations to optimize Levi’s promotion campaigns, formatted as a numbered list in Markdown.\n"
        "8. Weave these findings into a smooth, engaging narrative that flows logically, blending the table data with actionable insights in a way that resonates with sales and analytics teams.\n"
        "Write in a polished, persuasive tone—analytical yet accessible, like a seasoned analyst briefing the team. Ground every insight in the table data (e.g., ‘Levi’s 20% promo frequency vs. Lee’s 60%’), ensuring the story is credible and compelling.\n"
        "Ensure all output is raw Markdown (no ```markdown code blocks) and ready for direct rendering in a Markdown viewer."
    ),
    agent=analyzer_agent,
    expected_output=(
        f"A Markdown file ('{analysis_output_file}') with:\n"
        "   - Executive Summary: 3-4 sentences framing Levi’s promotion landscape with urgency, grounded in the data.\n"
        "   - Summary Table: A table summarizing average price, price range, promotion frequency, and average discount depth for Levi’s, Lee, and Calvin Klein.\n"
        "   - Pricing Trends: A section analyzing Levi’s price positioning relative to competitors, using the table data.\n"
        "   - Promotion Effectiveness: A section evaluating the impact of promotions, using the table metrics.\n"
        "   - Competitive Edge: A section on Levi’s strengths and weaknesses vs. rivals, backed by data.\n"
        "   - Risks Ahead: A section on where competitors are outshining Levi’s, with data support.\n"
        "   - Action Plan: 5-7 specific recommendations to enhance Levi’s promotions, formatted as a numbered list.\n"
        "   Ensure the output is raw Markdown, suitable for direct rendering, with no introductory narrative or code block formatting."
    ),
    output_file=analysis_output_file
)

report_task = Task(
    description=(
        f"Take the analysis from '{analysis_output_file}' and craft a concise, professional email body for Levi's data analysts and staff:\n"
        "1. Extract the summary table (average price, price range, promotion frequency, average discount depth) and include it in the email body as a Markdown table.\n"
        "2. Highlight the top 3 recommendations from the analysis, formatted as a numbered list in Markdown (e.g., '1. Recommendation text'). Ensure there is a space after the number and period (e.g., '1. ').\n"
        "3. Append the entire Markdown content from '{analysis_output_file}' below a separator (e.g., '--- Full Analysis ---').\n"
        "4. Add inline CSS styling to ensure the email looks polished:\n"
        "   - Wrap the content in a `<div>` with a max-width of 600px, centered, and a clean font (e.g., Arial).\n"
        "   - Style the table with borders, padding, and alternating row colors for readability (e.g., light gray for odd rows).\n"
        "   - Use a `<style>` tag at the top of the content to define these styles.\n"
        "Write in a concise, professional tone, focusing on the data and actionable steps. Send the email via Mailtrap SMTP using provided credentials, and log the action in 'email_report.log'."
    ),
    agent=reporting_agent,
    expected_output=(
        "A professional email sent to sales_team@levi.kr, analytics_team@levi.kr, marketing_team@levi.kr with subject 'Levi’s Promotion Campaign Insights - Weekly Report', containing:\n"
        "   - A `<style>` tag with CSS for the table (borders, padding, alternating rows), text (Arial font), and layout (centered, max-width 600px).\n"
        "   - A brief introduction (1-2 sentences) stating the purpose of the report.\n"
        "   - A Markdown table summarizing the key metrics (average price, price range, promotion frequency, average discount depth) for Levi’s, Lee, and Calvin Klein.\n"
        "   - A numbered list of the top 3 recommendations, properly formatted for Markdown-to-HTML conversion.\n"
        "   - The full analysis appended below a separator."
    )
)