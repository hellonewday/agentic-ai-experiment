from crewai import Agent
from crawler import CompetitorCrawler
import os
from dotenv import load_dotenv

load_dotenv()

crawler_agent = Agent(
    role="Web Crawler",
    goal="Extract and clean product information from Levi's Korea, Lee Korea, and Calvin Klein Korea websites",
    backstory="Expert web crawler specializing in e-commerce competitor analysis with integrated data cleaning",
    verbose=True,
    llm="gpt-3.5-turbo",
    tools=[CompetitorCrawler()]
)

analyzer_agent = Agent(
    role="Data Analyst",
    goal="Analyze Levi's denim promotion campaigns against competitors using crawled data to deliver actionable insights",
    backstory="Insightful analyst skilled at dissecting data to craft compelling, actionable narratives for sales and strategy teams",
    verbose=True,
    llm="gpt-3.5-turbo",
)

reporting_agent = Agent(
    role="Reporting Specialist",
    goal="Compile analysis findings into a polished, professional email report and send it to Levi's staff",
    backstory="Efficient communicator who transforms complex insights into clear, visually appealing updates for team action",
    verbose=True,
    llm="gpt-3.5-turbo",
)