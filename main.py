import schedule
import time
from crewai import Crew
from tasks import crawl_task, analyze_task, report_task
from agents import orchestrator_agent, crawl_agent, analyze_agent, report_agent

# Initialize Crew with orchestrator_agent as the process manager
crew = Crew(
    agents=[crawl_agent, analyze_agent, report_agent],
    tasks=[crawl_task, analyze_task, report_task],
    verbose=True,
    process='hierarchical',
    manager_agent=orchestrator_agent
)

# Function to run the workflow
def run_workflow():
    print("Starting workflow...")
    result = crew.kickoff()
    print("Workflow completed:", result)
    return result

# Simulate Cron Job with scheduler
if __name__ == "__main__":
    # schedule.every().day.at("09:00").do(run_workflow)
    print("Running workflow immediately for PoC...")
    result = run_workflow()