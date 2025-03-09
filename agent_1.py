from crewai import Agent, Task, Crew, LLM
import crawl_levis
import crawl_ck
import crawl_lee
import clean_data
import save_faiss
import os

os.environ["OPENAI_API_KEY"] = ""

data_processing_agent = Agent(
    role="Data Processing Agent",
    goal="Crawl, clean, and embed product data from Levi's, Lee, and Calvin Klein.",
    backstory="An expert in data extraction, preprocessing, and vector embedding.",
    verbose=True
)

data_processing_task = Task(
    description="Crawl data from Levi's, Lee, and Calvin Klein, clean it, and generate embeddings.",
    agent=data_processing_agent,
    expected_output="FAISS index stored with clean and vectorized product data.",
    run=lambda: [
        crawl_levis.run(),
        crawl_lee.run(),
        crawl_ck.run(),
        clean_data.run(),
        save_faiss.run()
    ]
)

crew = Crew(
    agents=[data_processing_agent],
    tasks=[data_processing_task],
    verbose=True
)

if __name__ == "__main__":
    crew.kickoff()
    print("\n✅ Data Processing Completed Successfully!")