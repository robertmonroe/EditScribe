"""
Simple script to test EditScribe upload functionality
"""
import requests
import sys

API_URL = "http://localhost:8000"

def test_upload():
    """Test uploading a file to EditScribe"""
    
    # Create test manuscript
    test_content = """Chapter 1

Detective Sarah Chen stared at the case file. Three murders, three weeks, same symbol.

"Still here?" Marcus asked from the doorway.

"Someone has to solve this," she replied.

Chapter 2

The fourth victim lay in an alley. This time, a clue: an address on a scrap of paper.

"1247 Riverside Drive," Marcus read. "The old warehouse district."

Sarah's pulse quickened. "Let's go."
"""
    
    print("Testing EditScribe Backend...")
    print("="*60)
    
    # Test 1: Health check
    print("\n1. Testing API health...")
    try:
        response = requests.get(f"{API_URL}/")
        print(f"   ✓ API is running: {response.json()}")
    except Exception as e:
        print(f"   ✗ API not responding: {e}")
        print("\n   Make sure the backend is running:")
        print("   cd c:/Users/3dmax/EditScribe/backend")
        print("   python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    
    # Test 2: Upload
    print("\n2. Testing file upload...")
    try:
        files = {'file': ('test_manuscript.txt', test_content.encode(), 'text/plain')}
        response = requests.post(f"{API_URL}/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            manuscript_id = data['manuscript_id']
            print(f"   ✓ Upload successful!")
            print(f"   Manuscript ID: {manuscript_id}")
            print(f"   Word count: {data['word_count']}")
            print(f"   Next stage: {data['next_stage']}")
            return manuscript_id
        else:
            print(f"   ✗ Upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ✗ Upload error: {e}")
        return False

if __name__ == "__main__":
    manuscript_id = test_upload()
    
    if manuscript_id:
        print("\n" + "="*60)
        print("✅ BACKEND IS WORKING!")
        print("="*60)
        print(f"\nYour manuscript ID: {manuscript_id}")
        print("\nYou can now:")
        print("1. Open http://localhost:3000 in your browser")
        print("2. Upload a file through the UI")
        print("3. Or use the API directly with this manuscript ID")
    else:
        print("\n" + "="*60)
        print("❌ BACKEND TEST FAILED")
        print("="*60)
        sys.exit(1)
