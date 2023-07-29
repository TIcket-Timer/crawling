import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
from urllib.request import urlopen
from collections import defaultdict
import json
import requests
def get_actors(goods_number):
    url = f'https://api-ticketfront.interpark.com/v1/goods/casting?castingRole=LEAD&goodsCode={goods_number}'


    response = requests.get(url)
    data = response.json()['data']
    actors = defaultdict(list)
    for actor in data:
        actor_info = {
            'actorName' : actor['manName'],
            'image' : actor['image1FileUrl']
        }
        actors[actor['characterName']].append(actor_info)
    return dict(actors)

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
        'musical_id' : goods_number,
        'site_id' : 1,
        'title' : title,
        'poster_url' : poster_url,
        'start_date' : start_date,
        'end_date' : end_date,
        'place' : place,
        'running_time' : running_time,
        'site_link' : site_link,
        'actors' : get_actors(goods_number)
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
    # musicals = soup.select('span.fw_bold > a')
    musicals = soup.select('td.RKthumb')
    for musical in musicals:
        u = musical.select('a')[0]['href']
        goods_number = get_goods_number(musical.select('a')[0]['href'])
        image_url = musical.select('a')[0].select('img')[0]['src']
        res = get_info(goods_number)
        res['poster_url'] = image_url
        print(res)
        # print(res)
    # 공연
lambda_handler(None, None)