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
actors = []
res = requests.get(url,headers=header)
html = res.text
json_html = json.loads(html)

try:
  for i in range(16):
      if json_html["data"][i]["perfTypeName"] != "뮤지컬":
          continue

      periodInfo = json_html["data"][i]["periodInfo"]
      url = "https://ticket.melon.com/performance/index.htm?prodId=" + str(json_html["data"][i]["prodId"])
      res = requests.get(url,headers=header)
      html = res.text
      soup = BeautifulSoup(html,'html.parser')
      actor_list = soup.select(".singer")

      if not actor_list:
          actor_list = '-'
          actors.append(actor_list)
      else:
        new_actor_list = []
        for actor in actor_list:
            new_actor_list.append(actor.text)
        actor_list = ','.join(new_actor_list)
        actors.append(actor_list)

      musical_id.append(json_html["data"][i]["prodId"])
      site_link.append(url)
      title.append(json_html["data"][i]["subTitle"])
      poster_url.append("https://cdnticket.melon.co.kr"+json_html["data"][i]["posterImg"])
      start_date.append(periodInfo[:periodInfo.find('-') - 1])
      end_date.append(periodInfo[periodInfo.find('-') + 2:])
      place.append(json_html["data"][i]["placeName"])
      runningTime.append(json_html["data"][i]["runningTime"])


  def lambda_handler(event, context):
      for i in range(30):
        dict_musical['musical_id'] = musical_id[i]
        dict_musical['site_id'] = 2
        dict_musical['title'] = title[i]
        dict_musical['poster_url'] = poster_url[i]
        dict_musical['start_date'] = start_date[i]
        dict_musical['end_date'] = end_date[i]
        dict_musical['place'] = place[i]
        dict_musical['running_time'] = runningTime[i]
        dict_musical['site_link'] = site_link[i]
        dict_musical['actors'] = actors[i]
        print(dict_musical)
  lambda_handler(None, None)

except:
   pass


