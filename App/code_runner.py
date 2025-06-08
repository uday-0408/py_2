import http.client
import json
import time

# API config
API_HOST = "judge0-ce.p.rapidapi.com"
API_KEY = "e0f508d109mshd80507861f478a1p1dde1bjsn599150ef2022"  # Replace with your real key

headers = {
    "content-type": "application/json",
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}

def send_code_submission(code, language_id=71):
    """Send code to Judge0 and return the submission token."""
    conn = http.client.HTTPSConnection(API_HOST)
    payload = json.dumps({
        "language_id": language_id,
        "source_code": code
    })
    conn.request("POST", "/submissions?base64_encoded=false&wait=false", body=payload, headers=headers)
    res = conn.getresponse()
    data = res.read()
    conn.close()
    return json.loads(data)["token"]

def get_submission_result(token):
    """Fetch result of submitted code using token."""
    conn = http.client.HTTPSConnection(API_HOST)
    conn.request("GET", f"/submissions/{token}?base64_encoded=false", headers=headers)
    res = conn.getresponse()
    result = res.read()
    conn.close()
    return json.loads(result)

def execute_code(code):
    """Read code from file, submit, wait, and print output."""
    # with open(file_path, "r") as f:
    #     code = f.read()

    print("Submitting code...\n")
    token = send_code_submission(code)
    print("Waiting for result...\n")
    time.sleep(2)

    result = get_submission_result(token)
    if result.get("stdout"):
        print("Output:\n" + result["stdout"])
        return result["stdout"]
    elif result.get("stderr"):
        print("Error:\n" + result["stderr"])
    else:
        print("No output. Check submission result:\n", result)

# Example usage
# execute_code("code.py")
