import http.client
import json
import base64
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")  # .env file should have: API_KEY=your_api_key_here

API_HOST = "judge029.p.rapidapi.com"

# Common headers
headers = {
    "content-type": "application/json",
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST,
}


def decode_base64(text):
    """
    Helper to decode base64-encoded strings safely.
    """
    if text is None:
        return ""
    return base64.b64decode(text).decode("utf-8").strip()


def send_code_submission(code, language_id=71, input_data="", expected_output=None):
    """
    Submit code to Judge0 and return the result directly using wait=true.
    """
    encoded_code = base64.b64encode(code.encode()).decode()
    encoded_input = base64.b64encode(input_data.encode()).decode()

    payload_data = {
        "language_id": language_id,
        "source_code": encoded_code,
        "stdin": encoded_input,
    }

    if expected_output is not None:
        encoded_expected = base64.b64encode(expected_output.encode()).decode()
        payload_data["expected_output"] = encoded_expected

    payload = json.dumps(payload_data)

    conn = http.client.HTTPSConnection(API_HOST)
    conn.request(
        "POST",
        "/submissions?base64_encoded=true&wait=true",
        body=payload,
        headers=headers,
    )
    res = conn.getresponse()
    data = res.read()
    conn.close()

    return json.loads(data)


def execute_code(code, language_id=71, input_data="", expected_output=None):
    """
    Execute code and return decoded stdout or errors.
    """
    try:
        result = send_code_submission(code, language_id, input_data, expected_output)

        if result.get("stdout"):
            return decode_base64(result["stdout"])
        elif result.get("stderr"):
            return "Error:\n" + decode_base64(result["stderr"])
        elif result.get("compile_output"):
            return "Compilation Error:\n" + decode_base64(result["compile_output"])
        elif result.get("status", {}).get("description"):
            return "Unknown Error: " + str(result)
        else:
            return "Unknown Error"
    except Exception as e:
        return f"Exception occurred: {str(e)}"
