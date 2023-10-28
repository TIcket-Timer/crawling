import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
from urllib.request import urlopen
import re
host = "http://localhost:8080"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "Authorization" : "Bearer "
}
total_cnt = 0
conflict_cnt = 0
error_cnt = 0
success_cnt = 0


def extract_no_from_url(url):
    parsed_url = urlparse(url)
    query_string = parsed_url.query

    query_parameters = parse_qs(query_string)

    no_values = query_parameters.get("no", [])

    return no_values[0]
def extract_bid_from_url(url):
    parsed_url = urlparse(url)
    query_string = parsed_url.query

    query_parameters = parse_qs(query_string)

    bid_values = query_parameters.get("bid", [])

    return bid_values[0]
def get_date(tr):  # 공연 날짜
    input_date_time = tr.select('td.date')[0].text
    cleaned_string = re.sub(r'[^0-9]', '', input_date_time)
    return '20'+cleaned_string


def get_title(tr):
    return tr.select('td.subject > a')[0].text

def get_url(tr):
    temp = tr.select('td.subject > a')[0]
    return temp['href']
def get_image_url_content(url):
    # url = f"http://ticket.interpark.com/webzine/paper/TPNoticeView.asp?bbsno=34&pageno=1&stext=&no={no}&groupno={no}&seq=0&KindOfGoods=TICKET&Genre=1&sort=WriteDate"
    f = urlopen(url)

    # 디코딩
    text = f.read().decode('cp949')
    soup = BeautifulSoup(text, 'html.parser')
    print(soup.select('span.poster > img'))
    image_url = soup.select('span.poster > img')[0]['src']

    content = soup.select('div.desc > div.introduce > div.data > p')[0].text
    return image_url, content
def save(notice):
    global total_cnt
    global conflict_cnt
    global success_cnt
    total_cnt+=1
    musical_request_url = f'{host}/api/musicalNotices'
    temp = requests.get(f"{host}/api/musicalNotices/{notice['id']}")
    # 저장된 데이터가 없을 때만 저장
    if temp.status_code == 404:
        response = requests.post(musical_request_url, json=notice, headers=headers)
        print(response)
        print(response.text)
        success_cnt+=1
    elif temp.status_code == 200:
        conflict_cnt+=1

def interpark():
    f = urlopen(
        'http://ticket.interpark.com/webzine/paper/TPNoticeList_iFrame.asp?bbsno=34&pageno=1&KindOfGoods=TICKET&Genre=1&sort=WriteDate&stext=',
    )

    # 디코딩
    text = f.read().decode('cp949')
    soup = BeautifulSoup(text, 'html.parser')
    global error_cnt
    # 공연
    arr = soup.select('div > div > div.list > div.table > table > tbody > tr')
    for i in range(len(arr)):
        # image_url, content = get_image_url_content(f'https://ticket.interpark.com/webzine/paper/{get_url(arr[i])}')
        try:
            request = {
                'id' : extract_no_from_url(get_url(arr[i])),
                'siteCategory': 'INTERPARK',
                'openDateTime': get_date(arr[i]),
                'title' : get_title(arr[i]),
                'url' : get_url(arr[i]),
                # 'content' : content,
                # 'image_url' : image_url
            }
            save(request)
        except:
            error_cnt+=1


def melon():
    url = "https://ticket.melon.com/csoon/ajax/listTicketOpen.htm"

    data = {
        "orderType": "0",
        "pageIndex": "1",
        "schGcode": "GENRE_ALL",
        "schText": "뮤지컬"
    }

    res = requests.post(url, headers=headers, json=data)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')
    openDates = soup.select(".date")
    title = soup.select(".tit")

    open_date = "20000101"
    global error_cnt
    for i in range(10):
        try:
            if openDates[i].text != "오픈일정 보기 >":
                open_date = re.sub(r'[^0-9]', '', openDates[i].text)
            link = "https://ticket.melon.com/csoon" + title[i].attrs['href'].replace(".", "")
            link = link[:37] + "." + link[37:]

            request = {
                'id': link[-4:],
                'siteCategory': 'MELON',
                'openDateTime': open_date,
                'title': title[i].text.strip(),
                'url': link,
                # 'content': "",
                # 'image_url': ""
            }
            print(request)
            save(request)
        except:
            error_cnt+=1
def yes24():
    url = "http://m.ticket.yes24.com/Notice/Ajax/axList.aspx"

    data = {
        'page': '1',
        'size': '20',
        'order': '1',
        'type': '1'
    }

    response = requests.post(url, data=data)

    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.select('li')
    global error_cnt
    for product in products:
        try:
            name = product.select('div.brd_name.limit_2ln')[0].text
            if '뮤지컬' in name :
                link = product.select('a')[0]['href']
                open_date = product.select('em.txt')[0].text
                request = {
                    'id': extract_bid_from_url(link),
                    'siteCategory': 'YES24',
                    'openDateTime': re.sub(r'[^0-9]', '', open_date),
                    'title': name,
                    'url': link,
                    # 'content': "",
                    # 'image_url': ""
                }
                print(request)
                save(request)
        except:
            error_cnt+=1


def lambda_handler(event, context):
    interpark()
    yes24()
    melon()
    print(f"total : {total_cnt} conflict : {conflict_cnt} success : {success_cnt} error : {error_cnt}")
lambda_handler(None, None)