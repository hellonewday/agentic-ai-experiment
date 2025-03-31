from crewai import Agent, Task, Crew, Process
import os

# Define the Researcher agent
researcher = Agent(
    role="Tech Researcher",
    goal="Discover and summarize the latest AI trends.",
    backstory="An AI expert who keeps up with the latest innovations.",
    verbose=True,
    llm="gpt-3.5-turbo"
)

# Define the Writer agent
writer = Agent(
    role="Content Writer",
    goal="Write a blog post based on research findings.",
    backstory="A writer passionate about making AI accessible to everyone.",
    verbose=True,
    llm="gpt-3.5-turbo"
)

# Research Task
research_task = Task(
    description="Find the latest AI trends and provide a structured summary.",
    expected_output="A structured summary of 3 AI trends.",
    agent=researcher
)

# Writing Task
write_task = Task(
    description="Write a blog post based on the AI research findings.",
    expected_output="A well-structured blog post display as markdown code.",
    agent=writer,
    output_file="blog_post.md"
)

# Define the Crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential  # Ensures research is done before writing
)

# Execute
result = crew.kickoff()
print(result)