from crewai import Agent, Task, Crew
from crewai_tools import FileReadTool  # Import the CrewAI tool for file reading
from langchain_openai import ChatOpenAI
import os

file_reader_tool = FileReadTool(file_path="event_names.txt")

file_reader = Agent(
    role="File Reader",
    goal="Read and extract content from the provided text file",
    backstory="You are an expert at processing and extracting data from text files efficiently.",
    tools=[file_reader_tool],
    verbose=True,
    llm="gpt-4o-mini"
)

funnel_analyzer = Agent(
    role="Funnel Stage Analyst",
    goal="Analyze text data and categorize events into sales funnel stages.",
    backstory="You are a marketing expert skilled at identifying customer behavior and mapping it to sales funnel stages.",
    verbose=True,
    llm="gpt-4"
)

# Define Tasks
read_file_task = Task(
    description="Read the content of the text file 'event_names.txt' using the provided tool and provide the raw text.",
    expected_output="Raw text content extracted from the file.",
    agent=file_reader,
    tools=[file_reader_tool] 
)

analyze_funnel_task = Task(
    description="""
        Analyze the provided list of event names in the clickstream logs and categorize funnel-related events into one of these funnel stages: Browsing, Adding to Cart, Checkout, Purchase.
    """,
    expected_output="Funnel stage classification in json format (without markdown code notation) with clearly matched events only.",
    agent=funnel_analyzer,
    output_file="funnel_events.json"
)

crew = Crew(
    agents=[file_reader, funnel_analyzer],
    tasks=[read_file_task, analyze_funnel_task],
    verbose=True
)


result = crew.kickoff()

