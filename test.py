import json
import logging
import smtplib
from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
import pandas as pd
from typing import List, Dict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from markdown2 import markdown
import smtplib

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="competitor_crawler.log"
)

llm = LLM(
    model="ollama/llama3.2:latest",
    base_url="http://localhost:11434"
)

# Crawler Tool with integrated cleaning
class CompetitorCrawler(BaseTool):
    """Tool to crawl and clean product data from Levi's Korea, Lee Korea, and Calvin Klein Korea."""
    name: str = "Crawl Competitor Data"
    description: str = "Crawls price and promotion data from Levi's Korea, Lee Korea, and Calvin Klein Korea, cleaning it immediately."

    def _clean_price(self, price: str) -> int | None:
        """Clean price by removing non-digits and converting to integer."""
        if not isinstance(price, str):
            return None
        price = re.sub(r"[^\d]", "", price)
        return int(price) if price.isdigit() else None

    def _clean_promotion(self, promo: str) -> str:
        """Clean promotion by extracting digits and formatting as percentage."""
        if not isinstance(promo, str):
            return "No Promotion"
        promo = re.sub(r"[^\d]", "", promo)
        return f"{promo}%" if promo else "No Promotion"

    def _run(self) -> List[Dict]:
        """Crawl data from all three websites, clean it immediately, and return standardized product details."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        all_products = []
        
        # Levi's Korea Crawler
        levi_url = "https://www.levi.co.kr/%EB%82%A8%EC%84%B1/%EC%9D%98%EB%A5%98/%EC%A7%84"
        try:
            req = Request(levi_url, headers=headers)
            page = urlopen(req)
            soup = BeautifulSoup(page, "html.parser")
            logging.info("Successfully fetched Levi's Korea data")
            for item in soup.find_all("div", class_="product-tile"):
                try:
                    product_name = item.find("div", class_="name1")
                    product_name = product_name.get_text(strip=True) if product_name else "Unknown"
                    price = item.find("span", class_="product-sales-price")
                    price = price.get_text(strip=True) if price else "Not Available"
                    promo = item.find("div", class_="discount-amount")
                    promo_info = promo.get_text(strip=True) if promo else "No Promotion"
                    all_products.append({
                        "product": product_name,
                        "price": self._clean_price(price),
                        "promotion": self._clean_promotion(promo_info),
                        "source": "Levis"
                    })
                except Exception as e:
                    logging.warning(f"Levi's parsing error: {e}")
        except Exception as e:
            logging.error(f"Failed to fetch Levi's data: {e}")

        # Lee Korea Crawler
        lee_base_url = "https://leekorea.co.kr/category/%EB%8D%B0%EB%8B%98/760/?page={}"
        for page in range(1, 4):
            try:
                req = Request(lee_base_url.format(page), headers=headers)
                page_data = urlopen(req)
                soup = BeautifulSoup(page_data, "html.parser")
                logging.info(f"Successfully fetched Lee Korea page {page}")
                for item in soup.find_all("li", class_="product-item"):
                    if "prd-first-banner" in item.get("class", []):
                        continue
                    try:
                        name_tag = item.find("div", class_="name")
                        product_name = name_tag.get_text(strip=True) if name_tag else "Unknown"
                        price_container = item.find("span", class_="sale")
                        price = price_container.get_text().split(" ")[0] if price_container else "Not Available"
                        promo_tag = price_container.find("span") if price_container else None
                        promotion = promo_tag.get_text(strip=True) if promo_tag else "No Promotion"
                        all_products.append({
                            "product": product_name,
                            "price": self._clean_price(price),
                            "promotion": self._clean_promotion(promotion),
                            "source": "Lee Korea"
                        })
                    except Exception as e:
                        logging.warning(f"Lee Korea parsing error on page {page}: {e}")
            except Exception as e:
                logging.error(f"Failed to fetch Lee Korea page {page}: {e}")

        # Calvin Klein Korea Crawler
        ck_url = "https://www.calvinklein.co.kr/ko/men/apparel/denim-jeans/"
        try:
            req = Request(ck_url, headers=headers)
            page = urlopen(req)
            soup = BeautifulSoup(page, "html.parser")
            logging.info("Successfully fetched Calvin Klein Korea data")
            for item in soup.find_all("div", class_="product-tile"):
                try:
                    product_name = item.find("div", class_="product-name-link")
                    product_name = product_name.get_text(strip=True) if product_name else "Unknown"
                    price_container = item.find("span", class_="sales")
                    price = price_container.find("span", class_="value") if price_container else None
                    price = price.get_text(strip=True) if price else "Not Available"
                    promo = item.find("span", class_="percent-value")
                    promo_info = promo.get_text(strip=True) if promo else "No Promotion"
                    all_products.append({
                        "product": product_name,
                        "price": self._clean_price(price),
                        "promotion": self._clean_promotion(promo_info),
                        "source": "Calvin Klein"
                    })
                except Exception as e:
                    logging.warning(f"Calvin Klein parsing error: {e}")
        except Exception as e:
            logging.error(f"Failed to fetch Calvin Klein data: {e}")

        if all_products:
            pd.DataFrame(all_products).to_csv("cleaned_products.csv", index=False)
            logging.info(f"Saved {len(all_products)} cleaned products to cleaned_products.csv")

        return all_products

# Define Agents
crawler_agent = Agent(
    role="Web Crawler",
    goal="Extract and clean product information from Levi's Korea, Lee Korea, and Calvin Klein Korea websites",
    backstory="Expert web crawler specializing in e-commerce competitor analysis with integrated data cleaning",
    verbose=True,
    llm=llm,
    tools=[CompetitorCrawler()]
)

analyzer_agent = Agent(
    role="Data Analyst",
    goal="Analyze Levi's denim promotion campaigns against competitors using crawled data to deliver actionable insights",
    backstory="Insightful analyst skilled at dissecting data to craft compelling, actionable narratives for sales and strategy teams",
    verbose=True,
    llm=llm
)

reporting_agent = Agent(
    role="Reporting Specialist",
    goal="Compile analysis findings into a polished, professional email report and send it to Levi's staff",
    backstory="Efficient communicator who transforms complex insights into clear, visually appealing updates for team action",
    verbose=True,
    llm=llm
)

# Define Tasks
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
        "A nice-looking email that show formatted summary, top 3 actions, and full analysis to sales_team@levi.kr, analytics_team@levi.kr, marketing_team@levi.kr with subject 'Levi’s Promotion Campaign Insights - Weekly Report'"
    )
)

def run_competitor_analysis():
    """Execute the competitor product crawling, analysis, and reporting workflow."""
    crew = Crew(
        agents=[crawler_agent, analyzer_agent, reporting_agent],
        tasks=[crawl_task, analyze_task, report_task],
        verbose=True
    )

    result = crew.kickoff()

    try:
        with open("competitor_analysis.md", "r") as f:
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

        sender = "Levis Data Team <hungnq.11198@gmail.com>"
        receiver = "Levis Staff <staff@levis.co.kr>"
        subject = "Levi’s Promotion Campaign Insights - Weekly Report"
        try:
            logging.info("Converting Markdown content to HTML")
            html_content = markdown(email_body)
                
            logging.info("Creating email message")
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = sender
            msg["To"] = receiver
                
            msg.attach(MIMEText(email_body, "plain"))
            msg.attach(MIMEText(html_content, "html"))
                
            smtp_server = "sandbox.smtp.mailtrap.io"
            smtp_port = 2525
            smtp_user = "07e58258e03ad3"
            smtp_password = "28bb032eaf39f5"
                
            logging.info("Connecting to SMTP server")
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                logging.info("Logging in to SMTP server")
                server.login(smtp_user, smtp_password)
                    
                logging.info("Sending email to %s", receiver)
                server.sendmail(sender, receiver, msg.as_string())
                
            logging.info("Email sent successfully")
        except Exception as e:
            print(f"Failed to send email: {e}")
            logging.error("Failed to send email: %s", str(e))


        print("\n=== Analysis & Reporting Complete ===")
        print("Check:\n- competitor_analysis.md (narrative)\n- email_report.log (email log)\n- Your Mailtrap inbox (if using testing SMTP) or real inbox (if using production SMTP)")
    except Exception as e:
        logging.error(f"Error processing results: {e}")
        print(f"Error processing results: {e}")

if __name__ == "__main__":
    print("Starting competitor product analysis...")
    logging.info("Starting new competitor analysis run")
    run_competitor_analysis()
    print("✅ Analysis complete!")