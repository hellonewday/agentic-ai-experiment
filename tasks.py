from crewai import Task
from agents import crawler_agent, analyzer_agent, reporting_agent

crawl_task = Task(
    description="Crawl Levi's Korea, Lee Korea, and Calvin Klein Korea websites to extract and clean product information including names, prices, and promotions",
    agent=crawler_agent,
    expected_output="A list of dictionaries containing cleaned product information from all three sources"
)

analyze_task = Task(
    description=(
        "Analyze the cleaned product data from Levi's Korea, Lee Korea, and Calvin Klein Korea to evaluate Levi’s denim promotion campaigns against competitors, delivering a compelling narrative for sales managers and data analyst leads:\n"
        "1. Crunch the numbers—compute average prices, price ranges, and promotion frequencies (percentage of products discounted) per brand to benchmark Levi’s position.\n"
        "2. Uncover pricing trends—assess where Levi’s sits (premium, mid-tier, budget) relative to Lee and Calvin Klein, highlighting competitive gaps.\n"
        "3. Evaluate promotion effectiveness—analyze the frequency, depth (average discount percentage), and spread of promotions across each brand’s catalog to gauge impact on sales potential.\n"
        "4. Reveal campaign strengths—identify what Levi’s is doing right in its promotions and where it lags behind competitors.\n"
        "5. Expose vulnerabilities—pinpoint where Lee and Calvin Klein’s promotion strategies threaten Levi’s market share, backed by data.\n"
        "6. Tell a story—weave these findings into a smooth, engaging narrative that flows logically, blending hard data with actionable insights in a way that resonates with sales and analytics teams.\n"
        "7. Propose strategies—offer 5-7 precise, data-backed recommendations to optimize Levi’s promotion campaigns and boost sales performance.\n"
        "Write in a polished, persuasive tone—analytical yet accessible, like a seasoned analyst briefing the team. Ground every insight in the data (e.g., ‘Levi’s 30% promo frequency vs. Lee’s 60%’), making the story both credible and compelling."
    ),
    agent=analyzer_agent,
    expected_output=(
        "A Markdown file ('competitor_analysis.md') with:\n"
        "   - Executive Summary: 3-4 sentences framing Levi’s promotion landscape with urgency.\n"
        "   - Pricing Snapshot: Data-driven overview of price positioning.\n"
        "   - Promotion Breakdown: Detailed analysis of campaign frequency and depth.\n"
        "   - Competitive Edge: Levi’s strengths and weaknesses vs. rivals.\n"
        "   - Risks Ahead: Where competitors are outshining us.\n"
        "   - Action Plan: 5-7 specific recommendations to enhance Levi’s promotions.\n"
        "   - Key Metrics: Core data points (avg prices, promo freqs, discount depths) woven into the narrative."
    ),
    output_file="competitor_analysis.md"
)

report_task = Task(
    description=(
        "Take the analysis from 'competitor_analysis.md' and craft a polished, professional email body that will be sent to Levi's data analysts and staff:\n"
        "1. Summarize key findings—distill Levi’s promotion performance, competitor threats, and top opportunities into a concise 2-3 sentence overview.\n"
        "2. Highlight top 3 actions—pull the most impactful recommendations from the analysis, formatted as clear, numbered steps.\n"
        "3. Include the full analysis—append the entire Markdown content below a separator for reference.\n"
        "Write in a clean, action-oriented tone with a professional yet engaging layout (e.g., bold headers, bullet points). Send the email via Mailtrap SMTP using provided credentials, and log the action in 'email_report.log'."
    ),
    agent=reporting_agent,
    expected_output=(
        "A nice-looking email that shows formatted summary, top 3 actions, and full analysis to sales_team@levi.kr, analytics_team@levi.kr, marketing_team@levi.kr with subject 'Levi’s Promotion Campaign Insights - Weekly Report'"
    )
)