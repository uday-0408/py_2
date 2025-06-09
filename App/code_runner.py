import http.client
import json
import time

API_HOST = "judge0-ce.p.rapidapi.com"
API_KEY = ""  # Replace with your real key

headers = {
    "content-type": "application/json",
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}

def send_code_submission(code, language_id=71, input_data=""):
    """Submit code to Judge0 and return the token."""
    conn = http.client.HTTPSConnection(API_HOST)
    payload = json.dumps({
        "language_id": language_id,
        "source_code": code,
        "stdin": input_data
    })
    conn.request("POST", "/submissions?base64_encoded=false&wait=false", body=payload, headers=headers)
    res = conn.getresponse()
    data = res.read()
    conn.close()
    return json.loads(data)["token"]

def get_submission_result(token):
    """Retrieve the result of code execution."""
    conn = http.client.HTTPSConnection(API_HOST)
    conn.request("GET", f"/submissions/{token}?base64_encoded=false", headers=headers)
    res = conn.getresponse()
    result = res.read()
    conn.close()
    return json.loads(result)

def execute_code(code, language_id=71, input_data=""):
    """Execute code and return the result output or error."""
    try:
        token = send_code_submission(code, language_id, input_data)
        time.sleep(2)  # Wait before fetching result

        result = get_submission_result(token)
        if result.get("stdout"):
            return result["stdout"]
        elif result.get("stderr"):
            return "Error:\n" + result["stderr"]
        elif result.get("compile_output"):
            return "Compilation Error:\n" + result["compile_output"]
        else:
            return "Unknown Error: " + str(result)
    except Exception as e:
        return f"Exception occurred: {str(e)}"
