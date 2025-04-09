import pandas as pd
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

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
                        "filters": json.loads(row["filters"]) if pd.notna(row["filters"]) else [],
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

# New function to save filtered sessions to JSON
def save_sessions_to_json(sessions, file_path="sessions.json"):
    """
    Save the filtered sessions to a JSON file.
    
    Args:
        sessions (list): List of session dictionaries to save
        file_path (str): Path to the output JSON file. Default is 'sessions.json'
    
    Returns:
        bool: True if successfully saved, False otherwise
    """
    try:
        if not sessions:
            print("No sessions to save")
            return False
        
        print(f"Saving {len(sessions)} sessions to {file_path}...")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)
        
        file_size_mb = round(os.path.getsize(file_path) / (1024 * 1024), 2)
        print(f"Successfully saved sessions to {file_path} ({file_size_mb} MB)")
        return True
    except Exception as e:
        print(f"Failed to save sessions to {file_path}: {str(e)}")
        return False

if __name__ == "__main__":
    import os  # Add this import at the top of your file
    
    file_path = "data.csv"
    print("Starting transformation...")
    sessions = transform_clickstream(file_path)

    ## read the data in data.csv, get set of event_name, store in text file
    if sessions:
        print("Starting collecting event names...")
        event_names = set()
        for session in sessions:
            for event in session["events"]:
                event_names.add(event["event_name"])
        
        with open("event_names.txt", "w", encoding="utf-8") as f:
            for event_name in sorted(event_names):
                f.write(f"{event_name}\n")
    if sessions:
        print("Starting filtering...")
        filtered_sessions = filter_sessions(sessions)
        if filtered_sessions:
            # Save the filtered sessions to JSON
            if save_sessions_to_json(filtered_sessions):
                print("Finish operation!")
            else:
                print("Saving to JSON failed")
        else:
            print("Filtering failed")
    else:
        print("Transformation failed")
