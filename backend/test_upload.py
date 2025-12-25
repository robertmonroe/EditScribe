import requests
import os

BASE_URL = "http://localhost:8000"

def test_upload():
    # Create a dummy md file
    filename = "test_manuscript.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# Chapter 1\n\nThis is a test manuscript.\n" * 100)
    
    print(f"Uploading {filename}...")
    try:
        with open(filename, "rb") as f:
            files = {"file": (filename, f, "text/markdown")}
            resp = requests.post(f"{BASE_URL}/upload", files=files)
            
        if resp.status_code == 200:
            print("SUCCESS: Upload completed!")
            print(resp.json())
        else:
            print(f"FAILURE: Upload failed with {resp.status_code}")
            print(resp.text)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    test_upload()
