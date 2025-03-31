# anomaly.py
import pandas as pd

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