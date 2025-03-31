# flow.py
from crewai import Agent, Task, Crew, Process
from crewai.flow.flow import Flow, listen, start
from crewai_tools import FileReadTool, FileWriterTool
from transform import transform_clickstream
from filter import filter_sessions
from funnel import analyze_funnel
from anomaly import detect_anomalies
from visualize import generate_visuals
from report import generate_report
import json
import uuid

# Agents (unchanged)
data_transformer = Agent(
    role="Data Transformer",
    goal="Transform raw clickstream into sessions",
    backstory="A seasoned data engineer with years of experience wrangling massive datasets, I excel at turning raw clickstream logs into structured, actionable sessions. My knack for parallelism ensures efficiency even with millions of records.",
    tools=[FileReadTool()],
    memory=True,
    verbose=True
)
session_filter = Agent(
    role="Session Filter",
    goal="Filter meaningful sessions",
    backstory="As a meticulous data curator, I’ve honed my skills in identifying high-value user interactions. I filter out the noise, keeping only sessions that reveal true engagement patterns, based on event counts and durations.",
    memory=True,
    verbose=True
)
funnel_analyst = Agent(
    role="Funnel Analyst",
    goal="Analyze funnel drop-offs with LLM",
    backstory="With a background in user journey mapping and behavioral analytics, I use my LLM-powered insight to craft logical funnel stages from event data. I don’t just count—I observe and interpret to uncover the story behind the numbers.",
    memory=True,
    verbose=True
)
anomaly_investigator = Agent(
    role="Anomaly Investigator",
    goal="Detect and analyze funnel anomalies",
    backstory="A detective of data oddities, I’ve spent years spotting and diagnosing anomalies in user flows. I dig into session metadata to pinpoint why drop-offs spike, offering clues to fix the cracks in the funnel.",
    memory=True,
    verbose=True
)
visualization_agent = Agent(
    role="Visualization Agent",
    goal="Create funnel visuals",
    backstory="An artist of data storytelling, I transform raw numbers into compelling charts and tables. My visualizations make funnel insights leap off the page, ready for any report or presentation.",
    verbose=True
)
report_generator = Agent(
    role="Report Generator",
    goal="Generate a customized 3-5 page PDF report",
    backstory="A veteran report writer with a flair for tailoring narratives, I weave funnel data, visuals, and anomalies into detailed, manager-ready PDFs. My LLM skills ensure every report is clear, customized, and impactful.",
    tools=[FileWriterTool()],
    memory=True,
    verbose=True
)

# Tasks (updated descriptions with embedded prompts)
transform_task = Task(
    description="Transform 'data.csv' into sessions",
    agent=data_transformer,
    function=transform_clickstream,
    inputs={"file_path": "data.csv"},
    expected_output="A list of session dictionaries containing user interactions from the clickstream data"
)
filter_task = Task(
    description="Filter the provided sessions to retain only those with above-median event counts and durations",
    agent=session_filter,
    function=filter_sessions,
    context=[transform_task],
    expected_output="A filtered list of session dictionaries with above-median event counts and durations"
)
funnel_task = Task(
    description="""
    Analyze the provided sessions to identify a logical sequence of 4 funnel stages representing a typical user journey (e.g., browsing to purchase).
    Given the event counts from the sessions, consider the meaning of each event name and infer a likely order based on observation, not just frequency.
    Return the stages as a list of 4 event names in sequence. If fewer than 4 stages make sense, pad with placeholders like 'unknown'.
    """,
    agent=funnel_analyst,
    function=lambda x: analyze_funnel(x["sessions"], funnel_analyst),
    context=[filter_task],
    expected_output="A dictionary with funnel stages, user counts per stage, and drop-off percentages"
)
anomaly_task = Task(
    description="Detect anomalies in the funnel data by identifying drop-offs exceeding 70%, analyzing session metadata for insights, and suggesting possible causes",
    agent=anomaly_investigator,
    function=lambda x: detect_anomalies(x["funnel_data"], x["sessions"]),
    context=[funnel_task, filter_task],
    conditional=True,
    expected_output="A string detailing any high drop-off anomalies with metadata insights, or 'No significant anomalies detected'"
)
viz_task = Task(
    description="Generate a bar chart and table from the funnel data to visualize user counts and drop-offs",
    agent=visualization_agent,
    function=generate_visuals,
    context=[funnel_task],
    expected_output="A dictionary with a bar chart file path and table data as a list of lists"
)
report_task = Task(
    description="""
    Generate a customized 3-5 page PDF report summarizing the clickstream funnel analysis.
    Use the provided funnel data, visuals, and anomaly findings.
    Prompt the user for tone (e.g., 'formal', 'concise', 'engaging') and focus (e.g., 'anomalies', 'recommendations', 'all'), emphasizing the chosen focus.
    Include: Executive Summary (1/2 page), Methodology (1/2 page), Funnel Analysis (1-2 pages with table and chart), Anomaly Insights (1 page), Recommendations (1 page).
    """,
    agent=report_generator,
    function=lambda x: generate_report(x["funnel_data"], x["visuals"], x["anomaly"], report_generator),
    context=[funnel_task, viz_task, anomaly_task],
    expected_output="A file path to a 3-5 page PDF report summarizing funnel analysis, visuals, and anomalies"
)

# Flow (unchanged except for minor logging tweak)
class ClickstreamFlow(Flow):
    state = {
        "file": "data.csv",
        "sessions": None,
        "filtered_sessions": None,
        "funnel_data": None,
        "visuals": None,
        "anomaly": None,
        "report": None,
        "execution_id": str(uuid.uuid4())
    }

    @start()
    def begin(self):
        print(f"Starting flow with execution ID: {self.state['execution_id']}")
        self.state["sessions"] = transform_clickstream(self.state["file"])
        return self.state["sessions"]

    @listen("begin")
    def process_sessions(self, sessions):
        self.state["filtered_sessions"] = filter_sessions(sessions)
        return self.state["filtered_sessions"]

    @listen("process_sessions")
    def analyze_funnel(self, filtered_sessions):
        self.state["funnel_data"] = analyze_funnel(filtered_sessions, funnel_analyst)
        return self.state["funnel_data"]

    @listen("analyze_funnel")
    def decide_anomaly_path(self, funnel_data):
        max_dropoff = max(funnel_data["dropoffs"], default=0)
        if max_dropoff > 70:
            print(f"High drop-off ({max_dropoff:.1f}%) detected, analyzing anomaly...")
            self.state["anomaly"] = detect_anomalies(funnel_data, self.state["filtered_sessions"])
        else:
            print("No high drop-off detected, proceeding without anomaly analysis")
            self.state["anomaly"] = "No significant anomalies detected"
        return self.state["funnel_data"]

    @listen("decide_anomaly_path")
    def create_visuals(self, funnel_data):
        self.state["visuals"] = generate_visuals(funnel_data)
        return self.state["visuals"]

    @listen("create_visuals")
    def generate_final_report(self, visuals):
        self.state["report"] = generate_report(self.state["funnel_data"], visuals, self.state["anomaly"], report_generator)
        with open(f"final_state_{self.state['execution_id']}.json", "w") as f:
            json.dump(self.state, f, indent=4)
        print(f"Saved final state to final_state_{self.state['execution_id']}.json")
        return "Analysis complete"

    @listen(lambda: True)
    def log_progress(self, event):
        print(f"Progress: {event}")

# Crew (unchanged)
clickstream_crew = Crew(
    agents=[data_transformer, session_filter, funnel_analyst, anomaly_investigator, visualization_agent, report_generator],
    tasks=[transform_task, filter_task, funnel_task, anomaly_task, viz_task, report_task],
    process=Process.sequential,
    verbose=True
)