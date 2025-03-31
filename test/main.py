# main.py
from flow import ClickstreamFlow, clickstream_crew

def run_analysis():
    flow = ClickstreamFlow()
    flow.kickoff()

if __name__ == "__main__":
    run_analysis()