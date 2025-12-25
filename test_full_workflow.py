import requests
import os

BASE_URL = "http://localhost:8000"
FILE_PATH = "sample_manuscript.txt"

def run_workflow():
    print(f"--- Simulating Author Workflow ---")
    
    # 1. Create Sample File
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, "w") as f:
            f.write("Chapter 1\nIt was a dark and stormy night. Suddenly, a shot rang out.")
        print(f"[x] Created sample manuscript: {FILE_PATH}")

    # 2. Upload (Start New Project)
    print(f"[ ] Uploading manuscript...")
    with open(FILE_PATH, "rb") as f:
        files = {"file": (FILE_PATH, f, "text/plain")}
        try:
            res = requests.post(f"{BASE_URL}/upload", files=files)
            if res.status_code != 200:
                print(f"[!] Upload Failed: {res.status_code} - {res.text}")
                return
            
            data = res.json()
            manuscript_id = data.get("manuscript_id")
            print(f"[x] Upload Success! Manuscript ID: {manuscript_id}")
        except Exception as e:
             print(f"[!] Upload Connection Error: {e}")
             return

    # 3. Simulate Redirect to Project Page (verification only)
    print(f"[x] Redirecting to /project/{manuscript_id}")

    # 4. Check Initial Stage Status (Acquisitions)
    print(f"[ ] Checking initial stage status...")
    res = requests.get(f"{BASE_URL}/workflow/{manuscript_id}/acquisitions/result")
    if res.status_code == 404:
        print(f"[x] Acquisitions stage is ready (No result yet).")
    else:
        print(f"[?] Unexpected status for new project: {res.status_code}")

    # 5. Run Acquisitions Agent (Simulate clicking 'Run Analysis')
    print(f"[ ] Running Acquisitions Agent...")
    try:
        # Note: This might take time with a real LLM, but for dev we expect it to work
        res = requests.post(f"{BASE_URL}/workflow/{manuscript_id}/acquisitions")
        if res.status_code == 200:
            print(f"[x] Acquisitions Agent Completed Successfully.")
            result = res.json()
            print(f"    - Report Summary: {result.get('report', {}).get('title', 'Report generated')}")
        else:
             print(f"[!] Agent Run Failed: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"[!] Agent Connection Error: {e}")

if __name__ == "__main__":
    run_workflow()
