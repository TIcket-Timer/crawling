import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
from urllib.request import urlopen


url = f'https://api-ticketfront.interpark.com/v1/goods/23007154/summary?goodsCode=23007154&priceGrade=&seatGrade='
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"
}
response = requests.get(url, headers=header)
data = response.json()['data']
print(data)