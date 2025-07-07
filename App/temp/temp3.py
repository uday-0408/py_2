import requests

# URL of your running container (update port if needed)
url = "http://localhost:8002/run"

# Test payload
code = """x=input()
for i in range(1000000):
    #print(x)"""
payload = {
    "language": "python",
    "code": code,
    "input": "Hello from Python client",
}
# Make POST request
response = requests.post(url, json=payload)
# 0.0104 , 31268 KB
# Display the result
if response.status_code == 200:
    data = response.json()
    print("Output:", data.get("stdout", "").strip())
    print("Error:", data.get("stderr", "").strip())
    print("Exit Code:", data.get("exit_code"))
    print("Time Taken:", data.get("time_taken"), "seconds")
    print("Memory Used:", data.get("memory_used"), "KB")
else:
    print("Error:", response.status_code, response.text)
