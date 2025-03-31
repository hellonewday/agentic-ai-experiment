import pandas as pd
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet

def llm_analyze_events(event_names, llm_agent=None):
    prompt = f"""
    You are an expert in user behavior analysis. Given this list of event names from clickstream data:
    {json.dumps(event_names, indent=2)}
    
    Identify a logical sequence of 4 funnel stages that represent a typical user journey (e.g., browsing to purchase).
    Consider the meaning of each event name and infer a likely order based on observation, not just frequency.
    Return the stages as a list of 4 event names in sequence.
    If fewer than 4 stages make sense, pad with placeholders like 'unknown'.
    """
    
    if llm_agent:
        response = llm_agent.execute_task(prompt=prompt)
        try:
            stages = json.loads(response)
            return stages[:4] if len(stages) >= 4 else stages + ["unknown"] * (4 - len(stages))
        except Exception as e:
            print(f"LLM response parsing error: {str(e)}")
            return ["Product List Viewed", "Product Viewed", "Experiment Activated", "In Wall Content Shown"]
    else:
        print("No LLM provided, using simulated stages for: ", list(event_names.keys()))
        return ["Product List Viewed", "Product Viewed", "Experiment Activated", "In Wall Content Shown"]

# Simulated LLM function (for report generation)
def llm_generate_report(funnel_data, visuals, anomaly, tone, focus, llm_agent=None):
    prompt = f"""
    You are an expert analyst crafting a 3-5 page report for a manager based on clickstream funnel analysis. Use this data:
    - Funnel Stages: {json.dumps(funnel_data, indent=2)}
    - Anomaly Findings: {anomaly}
    - Visuals: Bar chart available, table data: {json.dumps(visuals['table'], indent=2)}

    Customize the report:
    - Tone: {tone} (e.g., formal, concise, engaging)
    - Focus: {focus} (e.g., anomalies, recommendations, all - emphasize this section, but include all)

    Create a detailed report with:
    1. Executive Summary (1/2 page)
    2. Methodology (1/2 page)
    3. Funnel Analysis (1-2 pages, include table and chart placeholders)
    4. Anomaly Insights (1 page)
    5. Recommendations (1 page)
    Use {tone} language to impress the manager. Return as markdown.
    """
    
    if llm_agent:
        response = llm_agent.execute_task(prompt=prompt)
        return response
    else:
        # Simulated LLM response (customized based on tone and focus)
        print(f"No LLM provided, simulating report with tone: {tone}, focus: {focus}")
        max_dropoff = max(funnel_data["dropoffs"], default=0)
        max_drop_stage = funnel_data["stages"][funnel_data["dropoffs"].index(max_dropoff)] if max_dropoff > 0 else "N/A"
        
        if tone == "formal":
            summary = f"We respectfully present an analysis of clickstream data, identifying a {max_dropoff:.1f}% drop-off at {max_drop_stage}."
            methodology = "The data was systematically transformed into sessions, filtered for engagement, and analyzed for funnel performance."
        elif tone == "concise":
            summary = f"Key finding: {max_dropoff:.1f}% drop-off at {max_drop_stage}."
            methodology = "Transformed, filtered, analyzed funnel."
        else:  # engaging
            summary = f"Diving into over a million clickstream records, we’ve uncovered a striking {max_dropoff:.1f}% drop-off at {max_drop_stage}—a chance to turn the tide!"
            methodology = "We embarked on a journey: transforming raw logs into sessions, sifting for the gold of high engagement, and charting the funnel’s twists and turns."
        
        report = f"""
            # Funnel Drop-off Analysis Report

            ## Executive Summary
            {summary}

            ## Methodology
            {methodology}

            ## Funnel Analysis
            Here’s the user journey in numbers:
            [Insert Table Here]
            [Insert Chart Here]
            The flow from {funnel_data['stages'][0]} to {funnel_data['stages'][-1]} reveals key drop-off points.

            ## Anomaly Insights
            {anomaly}

            ## Recommendations
            - Optimize {max_drop_stage} to address drop-off causes.
            - Test UI changes at high drop-off stages.
            - Gather user feedback for deeper insights.
            """
        if focus == "anomalies":
            report += "\n### Extended Anomaly Insights\n" + anomaly.replace(".", ". Additional analysis could explore...")
        elif focus == "recommendations":
            report += "\n### Extended Recommendations\n- Prioritize A/B testing.\n- Enhance page load speed.\n- Refine content strategy."
        return report

def process_chunk(chunk, chunk_idx):
    try:
        print(f"Processing chunk {chunk_idx + 1}")
        chunk["timestamp"] = pd.to_datetime(chunk["timestamp"])
        grouped = chunk.groupby(["upm_id", "session_id"])
        sessions = []
        
        for (upm_id, session_id), group in grouped:
            group = group.sort_values(by="timestamp")
            session_data = {
                "session_id": session_id,
                "upm_id": upm_id,
                "age": int(group["age"].iloc[0]) if not pd.isna(group["age"].iloc[0]) else None,
                "gender": group["available_gender"].iloc[0],
                "country": group["country"].iloc[0],
                "start_session": group["timestamp"].iloc[0].isoformat(),
                "end_session": group["timestamp"].iloc[-1].isoformat(),
                "events": [
                    {
                        "event_name": row["event_name"],
                        "search_keyword": row["search_keyword"] if pd.notna(row["search_keyword"]) else "",
                        "event_products": json.loads(row["products"]) if pd.notna(row["products"]) else [],
                        "filters": json.loads(row["filters"]) if pd.notna(row["filters"]) else [],
                        "cart_value": row["cart_value"] if pd.notna(row["cart_value"]) else "",
                        "click_activity": row["click_activity"] if pd.notna(row["click_activity"]) else "",
                        "page_url": row["page_url"],
                        "product_name": row["product_name"] if pd.notna(row["product_name"]) else "",
                        "total": row["total"] if pd.notna(row["total"]) else "",
                        "product_inventory_status": row["product_inventory_status"] if pd.notna(row["product_inventory_status"]) else "",
                        "timestamp": row["timestamp"].isoformat()
                    }
                    for _, row in group.iterrows()
                ]
            }
            sessions.append(session_data)
        print(f"Chunk {chunk_idx + 1} completed: {len(sessions)} sessions")
        return sessions
    except Exception as e:
        print(f"Error in chunk {chunk_idx + 1}: {str(e)}")
        return []

def transform_clickstream(file_path):
    try:
        chunks = list(pd.read_csv(file_path, chunksize=100000))
        print(f"Total chunks to process: {len(chunks)}")
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            chunk_results = list(executor.map(lambda x: process_chunk(x[1], x[0]), enumerate(chunks)))
        
        sessions = [session for chunk_sessions in chunk_results for session in chunk_sessions if chunk_sessions]
        print(f"Transformed {len(sessions)} sessions in total")
        return sessions
    except Exception as e:
        print(f"Failed to transform data: {str(e)}")
        return None

def filter_sessions(sessions):
    try:
        if not sessions:
            raise ValueError("No sessions provided for filtering")
        
        event_counts = [len(session["events"]) for session in sessions]
        if not event_counts:
            raise ValueError("No events found in sessions")
        
        median_event_count = sorted(event_counts)[len(event_counts) // 2]
        print(f"Median event count: {median_event_count}")
        
        session_durations = []
        for session in sessions:
            try:
                start_time = datetime.fromisoformat(session["start_session"])
                end_time = datetime.fromisoformat(session["end_session"])
                duration = (end_time - start_time).total_seconds()
                session_durations.append(duration)
            except Exception as e:
                print(f"Error calculating duration for session {session['session_id']}: {str(e)}")
                session_durations.append(0)
        
        median_duration = sorted(session_durations)[len(session_durations) // 2]
        print(f"Median duration: {median_duration} seconds")
        
        filtered_sessions = [
            session for session in sessions
            if len(session["events"]) > median_event_count and
            (datetime.fromisoformat(session["end_session"]) - datetime.fromisoformat(session["start_session"])).total_seconds() > median_duration
        ]
        
        print(f"Filtered to {len(filtered_sessions)} sessions (from {len(sessions)})")
        return filtered_sessions
    except Exception as e:
        print(f"Failed to filter sessions: {str(e)}")
        return None

def analyze_funnel(sessions, llm_agent=None):
    try:
        if not sessions:
            raise ValueError("No sessions provided for funnel analysis")
        
        event_counts = {}
        for session in sessions:
            for event in session["events"]:
                event_name = event["event_name"]
                event_counts[event_name] = event_counts.get(event_name, 0) + 1
        
        if not event_counts:
            raise ValueError("No events found for funnel detection")
        
        stages = llm_analyze_events(event_counts, llm_agent)
        print(f"LLM-detected funnel stages: {stages}")
        
        counts = []
        for stage in stages:
            if stage == "unknown":
                counts.append(0)
            else:
                stage_count = len([s for s in sessions if any(e["event_name"] == stage for e in s["events"])])
                counts.append(stage_count)
        
        dropoffs = []
        for i in range(len(counts) - 1):
            if counts[i] > 0:
                dropoff = 100 * (counts[i] - counts[i + 1]) / counts[i]
            else:
                dropoff = 0
            dropoffs.append(dropoff)
        
        funnel_data = {"stages": stages, "counts": counts, "dropoffs": dropoffs}
        print(f"Funnel analysis: {json.dumps(funnel_data, indent=2)}")
        return funnel_data
    except Exception as e:
        print(f"Failed to analyze funnel: {str(e)}")
        return None

# Step 5: Anomaly Detection (unchanged)
def detect_anomalies(funnel_data, sessions):
    try:
        if not funnel_data or "dropoffs" not in funnel_data:
            raise ValueError("Invalid funnel data for anomaly detection")
        
        max_dropoff = max(funnel_data["dropoffs"], default=0)
        if max_dropoff > 70:
            stage_idx = funnel_data["dropoffs"].index(max_dropoff)
            from_stage = funnel_data["stages"][stage_idx]
            to_stage = funnel_data["stages"][stage_idx + 1]
            
            relevant_sessions = [s for s in sessions if any(e["event_name"] == from_stage for e in s["events"])]
            common_urls = pd.Series([e["page_url"] for s in relevant_sessions for e in s["events"] if e["event_name"] == from_stage]).value_counts().head(1)
            common_keywords = pd.Series([e["search_keyword"] for s in relevant_sessions for e in s["events"] if e["event_name"] == from_stage and e["search_keyword"]]).value_counts().head(1)
            
            anomaly_insight = f"High drop-off ({max_dropoff:.1f}%) from {from_stage} to {to_stage}. "
            if not common_urls.empty:
                anomaly_insight += f"Most common URL: {common_urls.index[0]} (seen {common_urls.iloc[0]} times). "
            if not common_keywords.empty:
                anomaly_insight += f"Top search keyword: {common_keywords.index[0]} (seen {common_keywords.iloc[0]} times). "
            anomaly_insight += "Possible causes: UI friction, slow load times, or insufficient info."
            
            print(f"Anomaly detected: {anomaly_insight}")
            return anomaly_insight
        else:
            print("No significant anomalies detected")
            return "No significant anomalies detected"
    except Exception as e:
        print(f"Failed to detect anomalies: {str(e)}")
        return None

def generate_visuals(funnel_data):
    try:
        if not funnel_data or "stages" not in funnel_data or "counts" not in funnel_data:
            raise ValueError("Invalid funnel data for visualization")
        
        plt.figure(figsize=(10, 6))
        plt.bar(funnel_data["stages"], funnel_data["counts"], color="skyblue")
        plt.title("Funnel Drop-off Analysis")
        plt.xlabel("Stages")
        plt.ylabel("User Count")
        plt.xticks(rotation=45)
        chart_path = "funnel_chart.png"
        plt.savefig(chart_path, bbox_inches="tight")
        plt.close()
        print(f"Saved bar chart to {chart_path}")
        
        table_data = [["Stage", "Count", "Drop-off %"]] + [
            [stage, count, f"{dropoff:.1f}" if i < len(funnel_data["dropoffs"]) else "N/A"]
            for i, (stage, count, dropoff) in enumerate(zip(funnel_data["stages"], funnel_data["counts"], funnel_data["dropoffs"] + [0]))
        ]
        with open("funnel_table.json", "w") as f:
            json.dump(table_data, f, indent=4)
        print("Saved table data to funnel_table.json")
        
        return {"chart": chart_path, "table": table_data}
    except Exception as e:
        print(f"Failed to generate visuals: {str(e)}")
        return None

# Step 7: Customized Report
def generate_report(funnel_data, visuals, anomaly, llm_agent=None):
    try:
        if not funnel_data or not visuals or not anomaly:
            raise ValueError("Missing data for report generation")
        
        # User customization
        tone = input("Report tone (e.g., 'formal', 'concise', 'engaging') [default: engaging]: ") or "engaging"
        focus = input("Report focus (e.g., 'anomalies', 'recommendations', 'all') [default: all]: ") or "all"
        
        # Generate report content
        report_content = llm_generate_report(funnel_data, visuals, anomaly, tone, focus, llm_agent)
        
        # Convert to PDF
        pdf = SimpleDocTemplate("funnel_report.pdf", pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        for section in report_content.split("\n\n"):
            if section.startswith("# "):
                elements.append(Paragraph(section[2:], styles["Title"]))
            elif section.startswith("## "):
                elements.append(Paragraph(section[3:], styles["Heading2"]))
            elif "[Insert Table Here]" in section:
                table = Table(visuals["table"])
                elements.append(table)
            elif "[Insert Chart Here]" in section:
                elements.append(Image(visuals["chart"], width=400, height=200))
            else:
                elements.append(Paragraph(section, styles["BodyText"]))
            elements.append(Spacer(1, 12))
        
        pdf.build(elements)
        print("Saved report to funnel_report.pdf")
        return "funnel_report.pdf"
    
    except Exception as e:
        print(f"Failed to generate report: {str(e)}")
        return None

# Test the pipeline
if __name__ == "__main__":
    file_path = "data.csv"  # Replace with your file
    print("Starting transformation...")
    sessions = transform_clickstream(file_path)
    
    if sessions:
        print("Starting filtering...")
        filtered_sessions = filter_sessions(sessions)
        
        if filtered_sessions:
            print("Starting funnel analysis...")
            funnel_data = analyze_funnel(filtered_sessions, llm_agent=None)
            
            if funnel_data:
                print("Starting anomaly detection...")
                anomaly = detect_anomalies(funnel_data, filtered_sessions)
                
                if anomaly:
                    print("Starting visualization...")
                    visuals = generate_visuals(funnel_data)
                    
                    if visuals:
                        print("Starting report generation...")
                        report = generate_report(funnel_data, visuals, anomaly, llm_agent=None)
                        
                        if report:
                            print("Report generation complete")
                        else:
                            print("Report generation failed")
                    else:
                        print("Visualization failed")
                else:
                    print("Anomaly detection failed")
            else:
                print("Funnel analysis failed")
        else:
            print("Filtering failed")
    else:
        print("Transformation failed")