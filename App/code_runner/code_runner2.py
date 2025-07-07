import http.client
import json
import base64
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv(
    "API_KEY"
)  # .env file should have: API_KEY=e0f508d109mshd80507861f478a1p1dde1bjsn599150ef2022


API_HOST = "judge029.p.rapidapi.com"

headers = {
    "content-type": "application/json",
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST,
}

# Language name to Judge0 language_id map
LANGUAGE_ID_MAP = {
    "python": 71,
    "cpp": 54,
    "c": 50,
    "java": 62,
    "javascript": 63,
    "go": 60,
    "rust": 73,
    "typescript": 74,
}


def decode_base64(text):
    if text is None:
        return ""
    return base64.b64decode(text).decode("utf-8").strip()


def get_language_id(language):
    return LANGUAGE_ID_MAP.get(language.lower(), 71)


def send_code_submission(code, language, input_data=""):
    language_id = get_language_id(language)
    encoded_code = base64.b64encode(code.encode()).decode()
    encoded_input = base64.b64encode(input_data.encode()).decode()

    payload_data = {
        "language_id": language_id,
        "source_code": encoded_code,
        "stdin": encoded_input,
    }

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


def execute_code(code, language="python", input_data=""):
    """
    Mimics FastAPI runner. Returns string: output, error, or exit code message.
    """
    try:
        print(f"code came in execute_code (Judge0):\n{code}")
        result = send_code_submission(code, language, input_data)

        stdout = decode_base64(result.get("stdout"))
        stderr = decode_base64(result.get("stderr"))
        compile_output = decode_base64(result.get("compile_output"))
        time_taken = str(result.get("time") or "None")
        memory_used = str(result.get("memory") or "None")
        exit_code = result.get("exit_code", 1 if (stderr or compile_output) else 0)

        print("output", stdout)
        print(f"Time:{time_taken} sec  Memory: {memory_used} KB")

        if stderr or compile_output:
            error_message = stderr or compile_output or "Unknown Error"
            return f"Error:\n{error_message}"
        elif stdout:
            if exit_code == 0:
                return stdout
            else:
                return f"{stdout}\n\nExit Code: {exit_code}"
        else:
            return f"No Output.\nExit Code: {exit_code}"

    except Exception as e:
        return f"Exception occurred: {str(e)}"
