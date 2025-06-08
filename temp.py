import requests
from bs4 import BeautifulSoup

url = "https://open.kattis.com/problems"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
print(soup)
problems = soup.select("table.problem_list tr")[1:6]  # skip header row
for prob in problems:
    title = prob.select_one("td a").text.strip()
    link = "https://open.kattis.com" + prob.select_one("td a")["href"]
    print(f"{title}: {link}")
