import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
from urllib.request import urlopen
from requests.structures import CaseInsensitiveDict
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "Authorization" : "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzZXJ2ZXJJZCI6Imtha2FvMjgwMzE2MzU4NyIsImlkIjoxLCJ0eXBlIjoiYWNjZXNzVG9rZW4iLCJpYXQiOjE2OTY1OTI4MDIsImV4cCI6MTY5OTU5MjgwMn0.8fVYvhAI2LP_RsgR0VNIYljLSuv6cCv5tkV3NunKJL4"
}
host = "http://43.202.78.122:8080"
total_cnt = 0
conflict_cnt = 0
error_cnt = 0
success_cnt = 0

def get_date(tr):  # 공연 날짜
    input_date_time = tr.select('td.date')[0].text
    cleaned_string = re.sub(r'[^0-9]', '', input_date_time)
    return '20'+cleaned_string

def save(musical):
    global total_cnt
    global conflict_cnt
    global success_cnt
    total_cnt+=1
    u = musical.select('a')[0]['href']
    goods_number = get_goods_number(musical.select('a')[0]['href'])
    image_url = musical.select('a')[0].select('img')[0]['src']
    res = get_info(goods_number)
    temp = requests.get(f"{host}/api/musicals/INTERPARK{res['id']}", headers=headers)

    if temp.status_code == 404:
        res['posterUrl'] = image_url
        musical_request_url = f'{host}/api/musicals'
        response = requests.post(musical_request_url, json=res, headers=headers)
        print(response.text)
        actors = get_actors(goods_number)
        for i in actors:
            actor_request_url = f'{host}/api/actors'
            response = requests.post(actor_request_url, json=i, headers=headers)
        # print(response.text)
        success_cnt+=1
    elif temp.status_code == 200:
        conflict_cnt+=1
    else:
        print(temp.text)

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
    age = data['viewRateName']

    price_url = f'https://api-ticketfront.interpark.com/v1/goods/23008707/prices/group'
    response = requests.get(price_url, headers=headers)
    dict = response.json()
    values = dict.values()
    price_arr = []
    for value in values:
        price_arr.append(f"{value['기본가'][0]['seatGradeName']} : {value['기본가'][0]['salesPrice']}")

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
        'age' : age,
        'price' : price_arr
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
    global total_cnt
    # 디코딩
    text = f.read().decode('cp949')
    soup = BeautifulSoup(text, 'html.parser')
    musicals = soup.select('td.RKthumb')
    for musical in musicals:
        total_cnt+=1
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

    age = soup.select('div.rn-product-area1 > dl > dd')[0].text.strip()

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

def yes24():
    url = "https://www.yes24.com/Product/Search?domain=TICKET&query=%EB%AE%A4%EC%A7%80%EC%BB%AC&page=1&size=1000&dispNo2=%EB%AE%A4%EC%A7%80%EC%BB%AC&bookingStat=%EC%98%88%EB%A7%A4%EC%A4%91"
    num = 0
    global success_cnt
    global conflict_cnt
    global error_cnt
    global total_cnt
    response = requests.get(url)
    if response.status_code != 200:
        exit(0)

    soup = BeautifulSoup(response.text, 'html.parser')
    musicals = soup.select('#yesSchList > li > div')

    for musical in musicals:
        total_cnt+=1
        try:
            u = musical.select('a')[0]['href']
            info = get_info_yes24(u)
            musical_request_url = f'{host}/api/musicals'
        except:
            error_cnt+=1
        temp = requests.get(f"{host}/api/musicals/YES24{info['id']}", headers=headers)
        if temp.status_code == 404:
            response = requests.post(musical_request_url, json=info, headers=headers)

            print(response.text)
            success_cnt+=1
        elif temp.status_code == 200:
            conflict_cnt+=1
        else:
            print(temp.text)


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
age = []
price = []


### 관람등급 추출
def age_def(age_list):
    if len(age_list) >= 2:
        second_txt_info = age_list[1].text.strip()
        age.append(second_txt_info)


### 가격 리스트 생성
def price_def(price_list):
    new_price_list = []
    for seat_price in price_list:
        new_price_list.append(
            seat_price.select_one(".seat_name").text + " " + seat_price.select_one(".price").text)
    price.append(new_price_list)
def melon():
    global success_cnt
    global conflict_cnt
    global error_cnt
    global total_cnt
    for i in range(17):
        total_cnt+=1
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
            age_list = soup.select(".box_consert_info > .info_right > .txt_info")  # 관람등급 몇세 이상
            price_list = soup.select(".box_bace_price > .list_seat li")  # 좌석명, 가격
            age_def(age_list=age_list)
            price_def(price_list=price_list)

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
        except Exception as ex:
            print(f'error : {url}, {ex}')
            error_cnt+=1
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
            dict_musical['age'] = age[i]
            dict_musical['price'] = price[i]
            print(dict_musical)
        # dict_musical['actors'] = actors[i]
        # if actors[i] != "-":
        #     dict_musical['actor_imgs'] = actor_imgs[i]
        #     dict_musical['roles'] = roles[i]
        # else:
        #     dict_musical.pop('actor_imgs', None)
        #     dict_musical.pop('roles', None)
            temp = requests.get(f"{host}/api/musicals/MELON{musical_id[i]}", headers=headers)
            if temp.status_code == 404:
                response = requests.post(f'{host}/api/musicals', json=dict_musical, headers=headers)
                print(response.text)
                success_cnt+=1
            elif temp.status_code == 200:
                conflict_cnt+=1
            else:
                print(temp.text)
def lambda_handler(event, context):
    # interpark()
    # yes24()
    melon()
    print(f"total : {total_cnt} conflict : {conflict_cnt} success : {success_cnt} error : {error_cnt}")
lambda_handler(None, None)