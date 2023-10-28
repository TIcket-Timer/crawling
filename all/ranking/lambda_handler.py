import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
from urllib.request import urlopen
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "Authorization" : "Bearer .."
}
host = "http://localhost:8080"

def extract_from_url(name, url):
    parsed_url = urlparse(url)
    query_string = parsed_url.query

    query_parameters = parse_qs(query_string)

    values = query_parameters.get(name, [])

    return values[0]
def inter():
    # 디코딩

    f = urlopen(
        'https://ticket.interpark.com/MusicalIndex.asp')
    text = f.read().decode('cp949')
    soup = BeautifulSoup(text, 'html.parser')
    musicals = soup.select('dd.tag >span > a')

    # 10개만 가져옴
    inter = ['INTERPARK'+extract_from_url("GoodsCode", musical['href']) for musical in musicals[:min(10, len(musicals))]]

    req = {
        "siteCategory" : "INTERPARK",
        "musicalIds" : inter
    }
    res = requests.post(f'{host}/api/musicals/ranking', json=req, headers=headers)
    return res.text
def melon():
    melon_url = "https://ticket.melon.com/performance/ajax/prodList.json?commCode=&sortType=REAL_RANK&perfGenreCode=GENRE_ART_MCAL&perfThemeCode=&filterCode=FILTER_ALL&v=1"

    res = requests.get(melon_url, headers=headers)
    musicals = ['MELON'+str(musical['prodId']) for musical in res.json()['data']]
    print(musicals[:min(10, len(musicals))])
    req = {
        "siteCategory" : "MELON",
        "musicalIds" :musicals[:min(10, len(musicals))]
    }
    res = requests.post(f'{host}/api/musicals/ranking', json=req, headers=headers)
    return res.text
    # text = f.read().decode('utf-8')
    # soup = BeautifulSoup(text, 'html.parser')
    # print(soup.select('li'))
def yes24():
    yes_url = "http://ticket.yes24.com/New/Rank/Ajax/RankList.aspx"
    data = {
        'pt': '1',
        'ci': '16',
        'et': '2023-10-24',
        'genre': '15457'
    }
    res = requests.post(url=yes_url, data=data)
    soup = BeautifulSoup(res.text, 'html.parser')
    arr = ['YES24'+extract_from_url("IdPerf", musical['href']) for musical in soup.select('a')]
    print(arr[:min(10, len(arr))])
    req = {
        "siteCategory" : "YES24",
        "musicalIds" : arr[:min(10, len(arr))]
    }
    res = requests.post(f'{host}/api/musicals/ranking', json=req, headers=headers)
    return res.text
arr1 = inter()
print(arr1)
arr2 = melon()
print(arr2)
arr3 = yes24()
print(arr3)

