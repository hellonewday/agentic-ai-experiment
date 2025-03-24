from crewai import Agent, Task, Crew
from crewai_tools import FileReadTool
import os

# Thay data.json bằng filtered_user_behavior_profiles.json
file_reader_tool = FileReadTool(file_path='data.json')

os.environ["OPENAI_API_KEY"] = ""

data_analyst = Agent(
    role="Senior Data Analyst",
    backstory="Senior Data Analyst designed to help the team with data analyis work.",
    goal="Read the clickstream dataset and summarize key findings.",
    tools=[file_reader_tool],
    description=(
        "An intelligent assistant specializing in analyzing funnel drop-off "
        "and extracting key insights for the data analyst team."
    ),
    llm="gpt-3.5-turbo"
)

# Thay data.json bằng filtered_user_behavior_profiles.json 
analyze_task = Task(
    description="Read the clickstream sessions `data.json` and analyze funnel drop-off of Nike Singapore",
    expected_output="A summary of the key findings and insights from the clickstream sessions.",
    agent=research_assistant,
    tools=[file_reader_tool],
)

crew = Crew(agents=[data_analyst], tasks=[analyze_task])
result = crew.kickoff()

print("\n**Summary: **\n", result)
###### ISSUE: The code is not working as expected. The file is too large.. ######
# The file is too large to be processed in a single step. We can split the file into smaller chunks and process them separately.
