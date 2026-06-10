import json
import os
import hashlib
from datetime import datetime

DATA_DIR = "data"

def init_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    files = {
        "complaints.json": [],
        "trace_logs.json": [],
        "tasks.json": []
    }
    
    for filename, default in files.items():
        path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(path):
            with open(path, "w") as f:
                json.dump(default, f, indent=2)
    
    print("Storage ready — 3 JSON files created in /data folder")

def save_complaint(input_text):
    path = os.path.join(DATA_DIR, "complaints.json")
    
    with open(path, "r") as f:
        complaints = json.load(f)
    
    complaint = {
        "id": len(complaints) + 1,
        "input_text": input_text,
        "input_hash": hashlib.sha256(input_text.encode()).hexdigest()[:12],
        "created_at": datetime.now().isoformat()
    }
    
    complaints.append(complaint)
    
    with open(path, "w") as f:
        json.dump(complaints, f, indent=2, ensure_ascii=False)
    
    return complaint["id"]

def save_trace(complaint_id, agent_name, input_data, output_data, confidence, duration_ms):
    path = os.path.join(DATA_DIR, "trace_logs.json")
    
    with open(path, "r") as f:
        logs = json.load(f)
    
    log = {
        "id": len(logs) + 1,
        "complaint_id": complaint_id,
        "agent_name": agent_name,
        "input_data": input_data,
        "output_data": output_data,
        "confidence": confidence,
        "duration_ms": duration_ms,
        "created_at": datetime.now().isoformat()
    }
    
    logs.append(log)
    
    with open(path, "w") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

def save_tasks(complaint_id, task_list):
    path = os.path.join(DATA_DIR, "tasks.json")
    
    with open(path, "r") as f:
        tasks = json.load(f)
    
    for task in task_list:
        task["id"] = len(tasks) + 1
        task["complaint_id"] = complaint_id
        task["status"] = "pending"
        tasks.append(task)
    
    with open(path, "w") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

def get_all_complaints():
    path = os.path.join(DATA_DIR, "complaints.json")
    with open(path, "r") as f:
        return json.load(f)

def get_trace_by_complaint(complaint_id):
    path = os.path.join(DATA_DIR, "trace_logs.json")
    with open(path, "r") as f:
        logs = json.load(f)
    return [l for l in logs if l["complaint_id"] == complaint_id]

if __name__ == "__main__":
    init_storage()