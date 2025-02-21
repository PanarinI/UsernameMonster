import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL страницы с проданными юзернеймами
url = "https://fragment.com/?sort=price_asc&filter=sold"

# Отправляем запрос к странице
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers)

# Проверяем успешность запроса
if response.status_code != 200:
    print("Ошибка при загрузке страницы:", response.status_code)
    exit()

# Разбираем HTML с помощью BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Списки для хранения данных
usernames = []

# Находим все элементы с юзернеймами и статусом Sold
for link in soup.find_all("a", class_="table-cell"):
    username_element = link.find("div", class_="table-cell-value tm-value")
    status_element = link.find("div", class_="table-cell-status-thin thin-only tm-status-unavail")

    if username_element and status_element and status_element.text.strip().lower() == "sold":
        username = username_element.text.strip()
        usernames.append(username)

# Сохранение данных в CSV
df = pd.DataFrame({"Username": usernames})
df.to_csv("sold_usernames.csv", index=False, encoding="utf-8")

print("Данные успешно сохранены в sold_usernames.csv")
