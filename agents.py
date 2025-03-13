from crewai import Agent
from crawler import CompetitorCrawler
import os
from dotenv import load_dotenv
from config import MODEL

load_dotenv()

crawler_agent = Agent(
    role="Web Crawler",
    goal="Extract and clean product information from Levi's Korea, Lee Korea, and Calvin Klein Korea websites",
    backstory="Expert web crawler specializing in e-commerce competitor analysis with integrated data cleaning",
    verbose=True,
    llm=MODEL,
    tools=[CompetitorCrawler()]
)

analyzer_agent = Agent(
    role="Data Analyst",
    goal="Analyze Levi's denim promotion campaigns against competitors using crawled data to deliver actionable insights",
    backstory="Insightful data analyst skilled at dissecting data to craft compelling, actionable narratives for sales and strategy teams",
    verbose=True,
    llm=MODEL,
)

reporting_agent = Agent(
    role="Reporting Specialist",
    goal="Craft a compelling and professionally polished email that presents the key findings of our analysis in a clear, impactful, and engaging manner. The email should be tailored for the Levi’s data analyst team and key stakeholders, highlighting critical insights, actionable recommendations, and data-driven conclusions in a way that captures attention and drives informed decision-making.",
    backstory="Efficient communicator who transforms complex insights into clear, visually appealing updates for team action",
    verbose=True,
    llm=MODEL,
)