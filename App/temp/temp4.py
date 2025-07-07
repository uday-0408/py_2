import requests

language = "java"
code = """public class Main {
    public static void main(String[] args) {
        int x = 10;
        for(int i = 0; i < x; i++) {
            System.out.println(i);
        }
        System.out.println("Hello, World!");
    }
}"""
input_data = ""

response = requests.post(
    "http://localhost:8002/run",
    json={"language": language, "code": code, "input": input_data},
    timeout=10,
)

result = response.json()
print(result)
stdout = result.get("stdout", "").strip()
stderr = result.get("stderr", "").strip()

if stderr:
    print("Error:\n", stderr)
else:
    print("Output:\n", stdout)
