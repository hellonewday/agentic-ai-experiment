# filter.py
from datetime import datetime

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