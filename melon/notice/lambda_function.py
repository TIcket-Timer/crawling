from bs4 import BeautifulSoup
import requests

def lambda_handler(event, context):
    url = "https://ticket.melon.com/csoon/ajax/listTicketOpen.htm"
    header = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
        "X-Requested-With" : "XMLHttpRequest"
    }   
    data = {
        "orderType" : "0",
        "pageIndex" : "1",
        "schGcode" : "GENRE_ALL",
        "schText" : "뮤지컬"
    }
    
    res = requests.post(url,headers=header,json=data)
    html = res.text
    soup = BeautifulSoup(html,'html.parser')
    openDates = soup.select(".date")
    title = soup.select(".tit")


    for i in range(10):
        if openDates[i].text == "오픈일정 보기 >":
            print("티켓오픈일 : -")
        else:
            print("티켓오픈일 : ",openDates[i].text)
        print("제목 : ",title[i].text.strip())
        link = "https://ticket.melon.com/csoon" + title[i].attrs['href'].replace(".","")
        link = link[:37] + "." + link[37:]
        print("링크 : ", link)
        print("Id : ", link[-4:])
        print()
lambda_handler(None, None)
