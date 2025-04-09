import pandas as pd
import dask.dataframe as dd
from datetime import datetime
import logging
from .config import CONFIG

def process_sessions(sessions: list, funnel_events: dict, dask_threshold: int) -> tuple[pd.DataFrame, list]:
    """Process sessions into a DataFrame with event sequences, timing, and URLs."""
    stages = CONFIG['stage_order']  # Use the defined stage order
    events_list = []
    
    logging.info("Processing sessions for funnel stages")
    for session in sessions:
        session_id = session['session_id']
        start_time = datetime.fromisoformat(session['start_session'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(session['end_session'].replace('Z', '+00:00'))
        duration = (end_time - start_time).total_seconds()
        events = session['events']
        
        event_data = [(event['event_name'], datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00')),
                       event.get('page_url', 'N/A')) for event in events]
        event_names = [e[0] for e in event_data]
        event_timestamps = [e[1] for e in event_data]
        event_urls = [e[2] for e in event_data]
        
        for stage in stages:
            if stage not in funnel_events:
                continue  # Skip stages not in funnel_events
            stage_events = set(funnel_events[stage])
            stage_hits = [i for i, event in enumerate(event_names) if event in stage_events]
            if stage_hits:
                first_hit = min(stage_hits)
                time_to_stage = (event_timestamps[first_hit] - start_time).total_seconds()
                events_list.append({
                    'session_id': session_id,
                    'stage': stage,
                    'time_to_stage': time_to_stage,
                    'duration': duration,
                    'events': event_names,
                    'url': event_urls[first_hit],
                    'timestamp': event_timestamps[first_hit],
                    'age': session.get('age'),
                    'gender': session.get('gender'),
                    'country': session.get('country')
                })
    
    df = pd.DataFrame(events_list)
    if len(sessions) > dask_threshold:
        logging.info("Switching to Dask for large dataset processing")
        df = dd.from_pandas(df, npartitions=8)
    
    return df, stages