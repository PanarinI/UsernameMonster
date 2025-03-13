import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL страницы с проданными юзернеймами
url = "https://fragment.com/?sort=ending&filter=sold"

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
prices = []
dates = []

# Находим все строки таблицы с данными
rows = soup.find_all("tr", class_="tm-row-selectable")

for row in rows:
    # Извлекаем юзернейм
    username_element = row.find("div", class_="table-cell-value tm-value")
    price_element = row.find("div", class_="table-cell-value tm-value icon-before icon-ton")
#    date_element = row.find("time")

    if username_element and price_element: #and date_element:
        username = username_element.text.strip()
        price = price_element.text.strip()
 #       date = date_element["datetime"].split("T")[0]  # Получаем дату в формате YYYY-MM-DD

        usernames.append(username)
        prices.append(price)
#        dates.append(date)

# Сохранение данных в CSV
#df = pd.DataFrame({"Username": usernames, "Price": prices, "Date": dates})
df = pd.DataFrame({"Username": usernames, "Price": prices})
df.to_csv("sold_usernames_with_prices_interval21_23feb2025.csv", index=False, encoding="utf-8")

print("Данные успешно сохранены в sold_usernames_500_11.03.csv")
