import requests
from bs4 import BeautifulSoup


def lambda_handler(event, context):
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

    for product in products:
        name = product.select('div.brd_name.limit_2ln')[0].text
        if '뮤지컬' in name :
            link = product.select('a')[0]['href']
            open_date = product.select('em.txt')[0].text

            print(link)
            print(open_date)
            print(name)


lambda_handler(None, None)
   