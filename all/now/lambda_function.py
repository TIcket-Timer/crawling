import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
from urllib.request import urlopen

def save(musical):
    u = musical.select('a')[0]['href']
    goods_number = get_goods_number(musical.select('a')[0]['href'])
    image_url = musical.select('a')[0].select('img')[0]['src']
    res = get_info_interpark(goods_number)
    res['posterUrl'] = image_url
    musical_request_url = 'http://localhost:8080/api/musicals'
    response = requests.post(musical_request_url, json=res)
    actors = get_actors(goods_number)
    for i in actors:
        actor_request_url = 'http://localhost:8080/api/actors'
        response = requests.post(actor_request_url, json=i)
    print(response.text)


def get_actors(goods_number):
    url = f'https://api-ticketfront.interpark.com/v1/goods/casting?castingRole=LEAD&goodsCode={goods_number}'


    response = requests.get(url)
    data = response.json()['data']
    actors = []
    for actor in data:
        actor_info = {
            'musicalId' : goods_number,
            'actorName' : actor['manName'],
            'roleName' : actor['characterName'],
            'profileUrl' : actor['image1FileUrl']
        }
        actors.append(actor_info)
    return actors

def get_info_interpark(goods_number):


    url = f'https://api-ticketfront.interpark.com/v1/goods/{goods_number}/summary?goodsCode=23007154&priceGrade=&seatGrade='
    response = requests.get(url)
    data = response.json()['data']
    title = data['goodsName']
    poster_url = f'http://ticketimage.interpark.com/rz/image/play/goods/poster/23/{goods_number}_p_s.jpg'
    start_date = data['playStartDate']
    end_date = data['playEndDate']
    place = data['placeName']
    running_time = data['runningTime']
    site_link = f'https://tickets.interpark.com/goods/{goods_number}'
    res = {
        'id' : str(goods_number),
        'siteCategory' : 'INTERPARK',
        'title' : title,
        'posterUrl' : poster_url,
        'startDate' : start_date,
        'endDate' : end_date,
        'place' : place,
        'runningTime' : running_time,
        'siteLink' : site_link,
        # 'actors' : get_actors(goods_number)
    }
    return res

def get_goods_number(url):
    # URL 파싱
    parsed_url = urlparse(url)

    query_params = parse_qs(parsed_url.query)

    group_code = query_params.get('GroupCode', [''])[0]

    return group_code


def interpark():
    f = urlopen(
        'http://ticket.interpark.com/TPGoodsList.asp?Ca=Mus&Sort=2')

    # 디코딩
    text = f.read().decode('euc-kr')
    soup = BeautifulSoup(text, 'html.parser')
    musicals = soup.select('td.RKthumb')
    for musical in musicals:
        save(musical)

def get_info_yes24(url):
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
        'siteLink' : url

    }

    return res

def yes24():
    url = "https://www.yes24.com/Product/Search?domain=TICKET&query=%EB%AE%A4%EC%A7%80%EC%BB%AC&page=1&size=1000&dispNo2=%EB%AE%A4%EC%A7%80%EC%BB%AC&bookingStat=%EC%98%88%EB%A7%A4%EC%A4%91"
    num = 0

    response = requests.get(url)
    if response.status_code != 200:
        exit(0)

    soup = BeautifulSoup(response.text, 'html.parser')
    musicals = soup.select('#yesSchList > li > div')

    for musical in musicals:
        u = musical.select('a')[0]['href']
        info = get_info_yes24(u)
        musical_request_url = 'http://localhost:8080/api/musicals'
        response = requests.post(musical_request_url, json=info)
        


def lambda_handler(event, context):
    interpark()
    yes24()