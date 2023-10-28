import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
from urllib.request import urlopen

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"
}
host = "http://localhost:8080"
def save(musical):
    u = musical.select('a')[0]['href']
    goods_number = get_goods_number(musical.select('a')[0]['href'])
    image_url = musical.select('a')[0].select('img')[0]['src']
    res = get_info(goods_number)
    res['posterUrl'] = image_url
    print(res)
    headers = {
        'Authorization':'Bearer eyJhbGciOiJIUzI1NiJ9.eyJzZXJ2ZXJJZCI6Imtha2FvMjgwMzE2MzU4NyIsImlkIjoxLCJ0eXBlIjoiYWNjZXNzVG9rZW4iLCJpYXQiOjE2OTcxMjI0MTksImV4cCI6MTY5NzE1MjQxOX0.d-awE0NkewzUNk-S0K0cLVM7Yi-xsAcXJm2VoURYBcA'
    }
    musical_request_url = f'{host}/api/musicals'
    response = requests.post(musical_request_url, json=res, headers=headers)
    print(response.text)
    actors = get_actors(goods_number)
    for i in actors:
        actor_request_url = f'{host}/api/actors'
        response = requests.post(actor_request_url, json=i, headers=headers)
    print(response.text)




def get_actors(goods_number):
    url = f'https://api-ticketfront.interpark.com/v1/goods/casting?castingRole=LEAD&goodsCode={goods_number}'


    response = requests.get(url, headers=headers)
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

def get_info(goods_number):


    url = f'https://api-ticketfront.interpark.com/v1/goods/{goods_number}/summary?goodsCode=23007154&priceGrade=&seatGrade='
    response = requests.get(url, headers=headers)
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


def lambda_handler(event, context):
    f = urlopen(
        'http://ticket.interpark.com/TPGoodsList.asp?Ca=Mus&Sort=2')

    # 디코딩
    text = f.read().decode('cp949')
    soup = BeautifulSoup(text, 'html.parser')
    musicals = soup.select('td.RKthumb')
    for musical in musicals:
        save(musical)

lambda_handler(None, None)