
import requests

def check_n8n():
    try:
        response = requests.get("http://localhost:5678/healthz", timeout=2)
        return f"n8n is running: {response.status_code}"
    except Exception as e:
        return f"n8n not reachable on 5678: {e}"

print(check_n8n())
