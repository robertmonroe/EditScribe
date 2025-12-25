import requests

# Test the backend API
print("Testing EditScribe Backend API...")
print("="*50)

# Test 1: Health check
try:
    response = requests.get("http://localhost:8000/")
    print(f"\n✓ Health Check: {response.status_code}")
    print(f"  Response: {response.json()}")
except Exception as e:
    print(f"\n✗ Health Check Failed: {e}")

# Test 2: Upload endpoint with a test file
try:
    # Create a test file
    test_content = """Chapter 1

The detective walked into the room.
"""
    
    files = {'file': ('test.txt', test_content, 'text/plain')}
    response = requests.post("http://localhost:8000/upload", files=files)
    
    print(f"\n✓ Upload Test: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Manuscript ID: {data.get('manuscript_id')}")
        print(f"  Word Count: {data.get('word_count')}")
    else:
        print(f"  Error: {response.text}")
        
except Exception as e:
    print(f"\n✗ Upload Test Failed: {e}")

print("\n" + "="*50)
