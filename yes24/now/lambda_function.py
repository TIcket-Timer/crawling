import requests
from bs4 import BeautifulSoup

def get_info(url):
    response = requests.get(url)
    if response.status_code != 200:
        exit(0)

    soup = BeautifulSoup(response.text, 'html.parser')
    id = url[(url.find('=') + 1):]

    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.select('p.rn-big-title')[0].text

    poster_url = soup.select('div.rn-product-imgbox > img')[0]['src']

    age = soup.select('div.rn-product-area1 > dl > dd')[0].text.strip()

    running_time = soup.select('div.rn-product-area1 > dl > dd')[1].text.strip()

    prices_arr = []
    prices = soup.select('dd.rn-product-price > ul > li')
    for price in prices:
        prices_arr.append(price.text.strip())

    actors = soup.select('div.rn-product-area1 > dl > dd')[2].select('a')
    actor_str = ''
    for actor in actors :
        actor_str += (actor.text + ', ')
    actor_str = actor_str[:-2]

    date = soup.select('span.ps-date')[0].text.replace('.', '')

    if '~' not in date :
        start_date = date
        end_date = date
    else :
        mid = date.index('~')
        start_date = date[0:mid-1]
        end_date = date[mid+2:]
    place = soup.select('span.ps-location')[0].text

    res = {
        'id' : id,
        'siteCategory' : 'YES24',
        'title' : title,
        'posterUrl' : poster_url,
        'startDate' : start_date,
        'endDate' : end_date,
        'place' : place,
        'runningTime' : running_time,
        'siteLink' : url,
        'age' : age,
        'price' : prices_arr
    }

    return res

def lambda_handler(event, context):
    url = "https://www.yes24.com/Product/Search?domain=TICKET&query=%EB%AE%A4%EC%A7%80%EC%BB%AC&page=1&size=1000&dispNo2=%EB%AE%A4%EC%A7%80%EC%BB%AC&bookingStat=%EC%98%88%EB%A7%A4%EC%A4%91"
    num = 0

    response = requests.get(url)
    if response.status_code != 200:
        exit(0)

    soup = BeautifulSoup(response.text, 'html.parser')
    musicals = soup.select('#yesSchList > li > div')

    for musical in musicals:
        u = musical.select('a')[0]['href']
        info = get_info(u)
        print(info)

lambda_handler(None, None)
