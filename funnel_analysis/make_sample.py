## read sessions.json
import json
import random 

with open("sessions.json", "r", encoding="utf-8") as f:
    sessions = json.load(f)
    ## get random 10 sessions
    random_sessions = random.sample(sessions, 300)
    ## save to sample_sessions.json
    with open("sample_sessions.json", "w", encoding="utf-8") as f:
        json.dump(random_sessions, f, ensure_ascii=False, indent=2)
        print("Random sessions saved to sample_sessions.json")