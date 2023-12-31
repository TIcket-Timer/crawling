from bs4 import BeautifulSoup
import requests,json

url = "https://ticket.melon.com/performance/ajax/prodList.json?commCode=&sortType=REAL_RANK&perfGenreCode=GENRE_ART_ALL&perfThemeCode=&filterCode=FILTER_ALL&v=1"
header = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "X-Requested-With" : "XMLHttpRequest"
}
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
age_list = []
age = []
price = []
res = requests.get(url,headers=header)
html = res.text
json_html = json.loads(html)

### 관람등급 추출
def age_def(age_list):
    if len(age_list) >= 2:
        second_txt_info = age_list[1].text.strip()
        age.append(second_txt_info)

### 가격 리스트 생성
def price_def(price_list):
    new_price_list = []
    for seat_price in price_list:
        new_price_list.append(seat_price.select_one(".seat_name").text + " " + seat_price.select_one(".price").text)
    price.append(new_price_list)

### 배우명 리스트 생성
def actor_def(actor_list):
    if not actor_list:
        actor_list = '-'
        actors.append(actor_list)
    else:
        new_actor_list = []
        for actor in actor_list:
            new_actor_list.append(actor.text)
        actor_list = ','.join(new_actor_list)
        actors.append(actor_list)

### 캐스팅 리스트 생성
def casting_def(casting_list):
    if not casting_list:
        casting_list = '-'
        roles.append(casting_list)
    else:
        new_casting_list = []
        for casting in casting_list: 
            new_casting_list.append(casting.text)
        casting_list = ','.join(new_casting_list)
        roles.append(casting_list)

### 배우 사진 리스트 생성
def actor_img_def(actor_img_list):
    if not actor_img_list:
        actor_img_list = '-'
        actor_imgs.append(actor_img_list)
    else:
        new_actor_img_list = []
        for img in actor_img_list:
            new_actor_img_list.append(img.get("src"))
        actor_img_list = ','.join(new_actor_img_list)
        actor_imgs.append(actor_img_list)


try:
  for i in range(17):
        if json_html["data"][i]["perfTypeName"] != "뮤지컬":
            continue
        
        periodInfo = json_html["data"][i]["periodInfo"]
        url = "https://ticket.melon.com/performance/index.htm?prodId=" + str(json_html["data"][i]["prodId"])
        res = requests.get(url,headers=header)
        html = res.text
        soup = BeautifulSoup(html,'html.parser')
        actor_list = soup.select(".singer") # 배우명
        casting_list = soup.select(".part") # 배역
        actor_img_list = soup.select(".thumb > .crop img") # 사진
        age_list = soup.select(".box_consert_info > .info_right > .txt_info") #관람등급 몇세 이상
        price_list = soup.select(".box_bace_price > .list_seat li") #좌석명, 가격

        age_def(age_list=age_list)
        price_def(price_list=price_list)
        actor_def(actor_list=actor_list)
        casting_def(casting_list=casting_list)
        actor_img_def(actor_img_list=actor_img_list)

        musical_id.append(json_html["data"][i]["prodId"])
        site_link.append(url)
        title.append(json_html["data"][i]["subTitle"])
        poster_url.append("https://cdnticket.melon.co.kr"+json_html["data"][i]["posterImg"])
        start_date.append(periodInfo[:periodInfo.find('-') - 1])
        end_date.append(periodInfo[periodInfo.find('-') + 2:])
        place.append(json_html["data"][i]["placeName"])
        runningTime.append(json_html["data"][i]["runningTime"])

except:
   pass

def lambda_handler():
    for i in range(len(musical_id)):
        dict_musical['musical_id'] = musical_id[i]
        dict_musical['site_id'] = 2
        dict_musical['title'] = title[i]
        dict_musical['age'] = age[i]
        dict_musical['price'] = price[i]
        dict_musical['poster_url'] = poster_url[i]
        dict_musical['start_date'] = start_date[i]
        dict_musical['end_date'] = end_date[i]
        dict_musical['place'] = place[i]
        dict_musical['running_time'] = runningTime[i]
        dict_musical['site_link'] = site_link[i]
        dict_musical['actors'] = actors[i]
        if actors[i] != "-":
            dict_musical['actor_imgs'] = actor_imgs[i]
            dict_musical['roles'] = roles[i]
        else:
            dict_musical.pop('actor_imgs', None)
            dict_musical.pop('roles', None)
        print(dict_musical)

lambda_handler()
