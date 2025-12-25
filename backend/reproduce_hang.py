import requests
import time
import sys

BASE_URL = "http://localhost:8000"
MANUSCRIPT_ID = "f8a11377-511f-4b47-9b5d-a3ef6d1a07cf"  # From the screenshot URL

def reproduce():
    print(f"Triggering extraction for {MANUSCRIPT_ID}...")
    try:
        # Start extraction
        resp = requests.post(f"{BASE_URL}/bible/extract/{MANUSCRIPT_ID}")
        if resp.status_code != 200:
            print(f"Failed to start: {resp.text}")
            return
            
        data = resp.json()
        task_id = data["task_id"]
        print(f"Started task: {task_id}")
        
        # Poll
        while True:
            status_resp = requests.get(f"{BASE_URL}/tasks/{task_id}")
            if status_resp.status_code != 200:
                print(f"Failed to get status: {status_resp.text}")
                break
                
            task_data = status_resp.json()
            status = task_data.get("status")
            progress = task_data.get("progress", 0)
            message = task_data.get("message", "")
            
            print(f"Status: {status} | Progress: {progress}% | Message: {message}")
            
            if status == "completed":
                print("SUCCESS: Task completed!")
                break
            elif status == "failed":
                print(f"FAILURE: Task failed with error: {task_data.get('error')}")
                break
                
            time.sleep(2)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reproduce()
