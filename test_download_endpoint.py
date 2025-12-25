import requests

def test_download():
    # Use a known ID - I see 9066bc79... in the screenshot info
    manuscript_id = "9066bc79-605a-4276-9060-6815766674b0" 
    url = f"http://127.0.0.1:8000/workflow/{manuscript_id}/download"
    
    print(f"Testing download from {url}")
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        if response.status_code == 200:
            print("Look first 100 chars:")
            print(response.text[:100])
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_download()
