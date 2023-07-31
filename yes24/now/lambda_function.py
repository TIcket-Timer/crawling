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

    running_time = soup.select('div.rn-product-area1 > dl > dd')[1].text.strip()

    actors = soup.select('div.rn-product-area1 > dl > dd')[2].select('a')
    actor_str = ''
    for actor in actors :
        actor_str += (actor.text + ', ')
    actor_str = actor_str[:-2]

    date = soup.select('span.ps-date')[0].text

    if '~' not in date :
        start_date = date
        end_date = date
    else :
        mid = date.index('~')
        start_date = date[0:mid-1]
        end_date = date[mid+2:]
    place = soup.select('span.ps-location')[0].text

    res = {
        'musical_id' : id,
        'site_id' : 3,
        'title' : title,
        'poster_url' : poster_url,
        'start_date' : start_date,
        'end_date' : end_date,
        'place' : place,
        'running_time' : running_time,
        'site_link' : url,
        'actors' : actor_str
    }
    print(res)
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
        get_info(u)

lambda_handler(None, None)
