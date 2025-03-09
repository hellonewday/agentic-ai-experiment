from crewai import Agent, Task, Crew
import crawl_levis
import crawl_ck
import crawl_lee
import clean_data
import save_faiss
import os

os.environ["OPENAI_API_KEY"] = ""


# 1️⃣ Crawling Agent
crawler_agent = Agent(
    role="Web Crawler",
    goal="Scrape product data from Levi's, Lee, and Calvin Klein websites.",
    backstory="An expert web scraper specializing in fashion e-commerce.",
    verbose=True,
    llm="gpt-3.5-turbo"
)

crawl_task = Task(
    description="Crawl product data from Levi's, Lee, and Calvin Klein.",
    agent=crawler_agent,
    expected_output="Raw CSV files with product, price, and promotion details.",
    run=lambda: (crawl_levis.run(), crawl_ck.run(), crawl_lee.run())
)

# 2️⃣ Cleaning Agent
cleaning_agent = Agent(
    role="Data Cleaner",
    goal="Process raw scraped data into a clean format.",
    backstory="A data scientist ensuring data is structured and ready for analysis.",
    verbose=True,
    llm="gpt-3.5-turbo"
)

clean_task = Task(
    description="Clean the crawled product data and store it in cleaned_products.csv.",
    agent=cleaning_agent,
    expected_output="A cleaned CSV file.",
    run=lambda: clean_data.run(),
    depends_on=[crawl_task]
)

embedding_agent = Agent(
    role="Vector Embedding Generator",
    goal="Generate vector embeddings and store them in FAISS.",
    backstory="An AI-powered assistant for converting product data into embeddings.",
    verbose=True,
    llm="gpt-3.5-turbo"
)

embed_task = Task(
    description="Generate embeddings using sentence transformers and store them in FAISS.",
    agent=embedding_agent,
    expected_output="FAISS index stored with vectorized product data.",
    run=lambda: save_faiss.run(),
    depends_on=[clean_task]
)

analysis_agent = Agent(
    role="Data Analyst",
    goal="Analyze cleaned product data to identify trends and price differences.",
    backstory="A market researcher analyzing competitor pricing strategies.",
    verbose=True,
    llm="gpt-3.5-turbo"
)

analyze_task = Task(
    description="Analyze the cleaned product data to identify price changes among competitors.",
    agent=analysis_agent,
    expected_output="A report detailing competitor pricing trends.",
    depends_on=[embed_task]
)

crew = Crew(
    agents=[crawler_agent, cleaning_agent, embedding_agent, analysis_agent],
    tasks=[crawl_task, clean_task, embed_task, analyze_task],
    verbose=True
)

if __name__ == "__main__":
    crew.kickoff()
    print("\n✅ All agents completed successfully!")
