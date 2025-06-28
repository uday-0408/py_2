import requests


def execute_code(code, language="python", input_data=""):
    """
    Call FastAPI-based code runner and return output.
    """
    try:
        print(f"code came in execute_code of code_runner3 :{code}")
        response = requests.post(
            "http://localhost:8000/run",
            json={"language": language, "code": code, "input": input_data},
            timeout=10,
        )

        if response.status_code == 200:
            result = response.json()
            output = result.get("stdout", "").strip()
            error = result.get("stderr", "").strip()
            exit_code = result.get("exit_code", 0)
            print("output", output)

            if error:
                return f"Error:\n{error}"
            elif output:
                if exit_code == 0:
                    return output  # Don't show exit code on success
                else:
                    return f"{output}\n\nExit Code: {exit_code}"
            else:
                return f"No Output.\nExit Code: {exit_code}"
        else:
            return f"Error: Status {response.status_code}"
    except Exception as e:
        return f"Exception occurred: {str(e)}"
