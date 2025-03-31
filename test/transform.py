# transform.py
import pandas as pd
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
                        "event_products": row["products"] if pd.notna(row["products"]) else "[]",
                        "filters": row["filters"] if pd.notna(row["filters"]) else "[]",
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