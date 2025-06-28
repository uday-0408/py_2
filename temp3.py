import requests

# URL of your FastAPI code runner
url = "http://localhost:8000/run"

# Java code to run
code = """
import java.util.Scanner;
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = sc.nextInt();
        System.out.println(a*b);
    }
}
"""

# JSON payload
payload = {
    "language": "java",
    "code": code,
    "input": "10 120",
}

# Send request to code runner
try:
    response = requests.post(url, json=payload, timeout=10)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
except requests.exceptions.RequestException as e:
    print("Error:", str(e))
