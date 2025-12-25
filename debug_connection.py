
import requests
import socket

def check_port(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((host, port))
        s.close()
        return True
    except:
        return False

def check_url(url):
    try:
        response = requests.get(url, timeout=2)
        return response.status_code, response.json()
    except Exception as e:
        return str(e)

print("Diagnostic Report:")
print(f"Checking 127.0.0.1:8000 directly via Socket: {check_port('127.0.0.1', 8000)}")
print(f"Checking localhost:8000 directly via Socket: {check_port('localhost', 8000)}")

print("-" * 20)
print("Checking API Health (127.0.0.1):")
print(check_url("http://127.0.0.1:8000/"))

print("-" * 20)
print("Checking API Health (localhost):")
print(check_url("http://localhost:8000/"))
