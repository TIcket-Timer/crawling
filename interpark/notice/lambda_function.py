import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
from urllib.request import urlopen
def get_date(tr):  # 공연 날짜
    return tr.select('td.date')[0].text

def get_title(tr):
    return tr.select('td.subject > a')[0].text

def get_url(tr):
    temp = tr.select('td.subject > a')[0]
    return temp['href']

def lambda_handler(event, context):
    f = urlopen(
        'http://ticket.interpark.com/webzine/paper/TPNoticeList_iFrame.asp?bbsno=34&pageno=1&KindOfGoods=TICKET&Genre=1&sort=WriteDate&stext=')

    # 디코딩
    text = f.read().decode('euc-kr')
    soup = BeautifulSoup(text, 'html.parser')

    # 공연
    arr = soup.select('div > div > div.list > div.table > table > tbody > tr')
    print(len(arr))
    for i in range(len(arr)):
        print(arr[i].select('td.subject'))
        print(get_date(arr[i]))
        print(get_title(arr[i]))
        print(get_url(arr[i]))
lambda_handler(None, None)