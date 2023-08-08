import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
from urllib.request import urlopen
from collections import defaultdict
import json
import requests
from multiprocessing.dummy import Pool as ThreadPool
def save(musical):
    u = musical.select('a')[0]['href']
    goods_number = get_goods_number(musical.select('a')[0]['href'])
    image_url = musical.select('a')[0].select('img')[0]['src']
    res = get_info(goods_number)
    res['posterUrl'] = image_url
    musical_request_url = 'http://localhost:8080/api/musicals'
    response = requests.post(musical_request_url, json=res)
    actors = get_actors(goods_number)
    for i in actors:
        actor_request_url = 'http://localhost:8080/api/actors'
        response = requests.post(actor_request_url, json=i)
    print(response.text)


def work_thread(musicals, thread_num=10):
    pool = ThreadPool(thread_num)
    pool.map(save, musicals)
    pool.close()
    pool.join()

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

def get_info(goods_number):


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


def lambda_handler(event, context):
    f = urlopen(
        'http://ticket.interpark.com/TPGoodsList.asp?Ca=Mus&Sort=2')

    # 디코딩
    text = f.read().decode('euc-kr')
    soup = BeautifulSoup(text, 'html.parser')
    musicals = soup.select('span.fw_bold > a')
    musicals = soup.select('td.RKthumb')
    print(musicals)
    work_thread(musicals, 100)
    request = [] # Musical 정보
    # for musical in musicals:
    #     u = musical.select('a')[0]['href']
    #     goods_number = get_goods_number(musical.select('a')[0]['href'])
    #     image_url = musical.select('a')[0].select('img')[0]['src']
    #     # 뮤지컬 정보 얻기
    #     info = get_info(goods_number)
    #     info['poster_url'] = image_url
    #     request.append(info)
    #     print(info)
    #
    #     # 배우 정보 얻기
    #     actors = get_actors(goods_number)
    #     print(actors)
    #
    #     # print(res)
    # 공연
lambda_handler(None, None)