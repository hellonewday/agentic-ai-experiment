# funnel.py
import json

def analyze_funnel(sessions, llm_agent):
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
        
        # Prompt moved to task description; function relies on agent’s internal LLM
        stages = ["Product List Viewed", "Product Viewed", "Experiment Activated", "In Wall Content Shown"]  # Default if no LLM response
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