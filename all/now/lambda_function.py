import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
from urllib.request import urlopen
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "Authorization" : "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzZXJ2ZXJJZCI6Imtha2FvMjgwMzE2MzU4NyIsImlkIjoxLCJ0eXBlIjoiYWNjZXNzVG9rZW4iLCJpYXQiOjE2OTY1OTI4MDIsImV4cCI6MTY5OTU5MjgwMn0.8fVYvhAI2LP_RsgR0VNIYljLSuv6cCv5tkV3NunKJL4"
}
host = "http://43.202.78.122:8080"
def get_date(tr):  # 공연 날짜
    input_date_time = tr.select('td.date')[0].text
    cleaned_string = re.sub(r'[^0-9]', '', input_date_time)
    return '20'+cleaned_string
def save(musical):
    u = musical.select('a')[0]['href']
    goods_number = get_goods_number(musical.select('a')[0]['href'])
    image_url = musical.select('a')[0].select('img')[0]['src']
    res = get_info(goods_number)
    res['posterUrl'] = image_url
    print(res)
    # headers = {
    #     'Authorization':'Bearer eyJhbGciOiJIUzI1NiJ9.eyJzZXJ2ZXJJZCI6Imtha2FvMjgwMzE2MzU4NyIsImlkIjoxLCJ0eXBlIjoiYWNjZXNzVG9rZW4iLCJpYXQiOjE2OTcxMjI0MTksImV4cCI6MTY5NzE1MjQxOX0.d-awE0NkewzUNk-S0K0cLVM7Yi-xsAcXJm2VoURYBcA'
    # }
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


def interpark():
    f = urlopen(
        'http://ticket.interpark.com/TPGoodsList.asp?Ca=Mus&Sort=2')

    # 디코딩
    text = f.read().decode('cp949')
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
        musical_request_url = f'{host}/api/musicals'
        response = requests.post(musical_request_url, json=info, headers=headers)
        print(response.text)


melon_url = "https://ticket.melon.com/performance/ajax/prodList.json?commCode=&sortType=REAL_RANK&perfGenreCode=GENRE_ART_ALL&perfThemeCode=&filterCode=FILTER_ALL&v=1"
dict_musical = {}
title = []
poster_url = []
start_date = []
end_date = []
place = []
runningTime = []
musical_id = []
site_link = []
actors_img = []
actors = []
roles = []
actor_imgs = []
res = requests.get(melon_url,headers=headers)
html = res.text
json_html = json.loads(html)

def melon():
    for i in range(17):
        try:
            if json_html["data"][i]["perfTypeName"] != "뮤지컬":
                continue

            periodInfo = json_html["data"][i]["periodInfo"]
            url = "https://ticket.melon.com/performance/index.htm?prodId=" + str(json_html["data"][i]["prodId"])
            res = requests.get(url,headers=headers)
            html = res.text
            soup = BeautifulSoup(html,'html.parser')
            actor_list = soup.select(".singer") # 배우명
            casting_list = soup.select(".part") # 배역
            actor_img_list = soup.select(".thumb > .crop img") # 사진

            # 배우명 리스트 생성
            if not actor_list:
                actor_list = '-'
                actors.append(actor_list)
            else:
                new_actor_list = []
                for actor in actor_list:
                    new_actor_list.append(actor.text)
                actor_list = ','.join(new_actor_list)
                actors.append(actor_list)

            # 캐스팅 리스트 생성
            if not casting_list:
                casting_list = '-'
                roles.append(casting_list)
            else:
                new_casting_list = []
                for casting in casting_list:
                    new_casting_list.append(casting.text)
                    casting_list = ','.join(new_casting_list)
                    roles.append(casting_list)

            # 배우 사진 리스트 생성
            if not actor_img_list:
                actor_img_list = '-'
                actor_imgs.append(actor_img_list)
            else:
                new_actor_img_list = []
                for img in actor_img_list:
                    new_actor_img_list.append(img.get("src"))
                actor_img_list = ','.join(new_actor_img_list)
                actor_imgs.append(actor_img_list)

            musical_id.append(json_html["data"][i]["prodId"])
            site_link.append(url)
            title.append(json_html["data"][i]["subTitle"])
            poster_url.append("https://cdnticket.melon.co.kr"+json_html["data"][i]["posterImg"])
            cleaned_open = re.sub(r'[^0-9]', '', periodInfo[:periodInfo.find('-') - 1])
            cleaned_end = re.sub(r'[^0-9]', '', periodInfo[periodInfo.find('-') + 2:])

            start_date.append(cleaned_open)
            end_date.append(cleaned_end)
            place.append(json_html["data"][i]["placeName"])
            runningTime.append(json_html["data"][i]["runningTime"])
        except:
            continue

        for i in range(len(musical_id)):
            dict_musical['id'] = musical_id[i]
            dict_musical['siteCategory'] = 'MELON'
            dict_musical['title'] = title[i]
            dict_musical['posterUrl'] = poster_url[i]
            dict_musical['startDate'] = start_date[i]
            dict_musical['endDate'] = end_date[i]
            dict_musical['place'] = place[i]
            dict_musical['runningTime'] = runningTime[i]
            dict_musical['siteLink'] = site_link[i]
        # dict_musical['actors'] = actors[i]
        # if actors[i] != "-":
        #     dict_musical['actor_imgs'] = actor_imgs[i]
        #     dict_musical['roles'] = roles[i]
        # else:
        #     dict_musical.pop('actor_imgs', None)
        #     dict_musical.pop('roles', None)
            response = requests.post(f'{host}/api/musicals', json=dict_musical, headers=headers)
            print(response.text)
def lambda_handler(event, context):
    # interpark()
    yes24()
    # melon()
lambda_handler(None, None)