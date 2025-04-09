import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data(sessions_file: str, funnel_events_file: str) -> tuple[dict, list]:
    """Load sessions and funnel events from JSON files."""
    logging.info(f"Loading funnel events from {funnel_events_file}")
    with open(funnel_events_file, 'r') as f:
        funnel_events = json.load(f)
    
    logging.info(f"Loading sessions from {sessions_file}")
    with open(sessions_file, 'r') as f:
        sessions = json.load(f)
    
    return funnel_events, sessions