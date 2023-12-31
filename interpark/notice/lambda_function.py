import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
from urllib.request import urlopen
import re
host = "http://localhost:8080"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "Authorization" : "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzZXJ2ZXJJZCI6Imtha2FvMjgwMzE2MzU4NyIsImlkIjoxLCJ0eXBlIjoiYWNjZXNzVG9rZW4iLCJpYXQiOjE2OTY1OTI4MDIsImV4cCI6MTY5OTU5MjgwMn0.8fVYvhAI2LP_RsgR0VNIYljLSuv6cCv5tkV3NunKJL4"
}
def extract_no_from_url(url):
    parsed_url = urlparse(url)
    query_string = parsed_url.query

    query_parameters = parse_qs(query_string)

    no_values = query_parameters.get("no", [])

    return no_values[0]
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
    image_url = soup.select('span.poster > img')[0]['src']
    content = soup.select('div.desc > div.introduce > div.data > p')[0].text
    return image_url, content
def save(notice):

    musical_request_url = f'{host}/api/musicalNotices'
    headers = {
        'Authorization':'Bearer eyJhbGciOiJIUzI1NiJ9.eyJzZXJ2ZXJJZCI6Imtha2FvMjgwMzE2MzU4NyIsImlkIjoxLCJ0eXBlIjoiYWNjZXNzVG9rZW4iLCJpYXQiOjE2OTcxMjI0MTksImV4cCI6MTY5NzE1MjQxOX0.d-awE0NkewzUNk-S0K0cLVM7Yi-xsAcXJm2VoURYBcA'
    }
    response = requests.post(musical_request_url, json=notice, headers=headers)
    print(response)
    print(response.text)
def lambda_handler(event, context):
    f = urlopen(
        'http://ticket.interpark.com/webzine/paper/TPNoticeList_iFrame.asp?bbsno=34&pageno=1&KindOfGoods=TICKET&Genre=1&sort=WriteDate&stext=',
    )

    # 디코딩
    text = f.read().decode('cp949')
    soup = BeautifulSoup(text, 'html.parser')

    # 공연
    arr = soup.select('div > div > div.list > div.table > table > tbody > tr')

    print(len(arr))
    for i in range(len(arr)):
        image_url, content = get_image_url_content(f'https://ticket.interpark.com/webzine/paper/{get_url(arr[i])}')
        request = {
            'id' : extract_no_from_url(get_url(arr[i])),
            'siteCategory': 'INTERPARK',
            'openDateTime': get_date(arr[i]),
            'title' : get_title(arr[i]),
            'url' : get_url(arr[i]),
            'content' : content,
            'image_url' : image_url
        }
        print(request)

        # save(request)
lambda_handler(None, None)