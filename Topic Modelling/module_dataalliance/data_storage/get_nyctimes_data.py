import requests
import pymongo
from  datetime import datetime, timedelta
from decouple import config
import time

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

db = myclient.articles
collection = db.nyt_articles

API_KEY = config('NYC_TIMES_KEY')

apikey = API_KEY
query = "Covid"
begin_date = "20220201"  # YYYYMMDD
#page = "0"  # <0-200>
sort = "relevance"  # newest, oldest
response_field = 'abstract,snippet,headline,pub_date'
status_code = 200
out_status_code = 200

while out_status_code == 200:
    page = 0
    while status_code == 200:
        query_url = f"https://api.nytimes.com/svc/search/v2/articlesearch.json?" \
                    f"q={query}" \
                    f"&api-key={apikey}" \
                    f"&begin_date={begin_date}" \
                    f"&page={page}" \
                    f"&sort={sort}" \
                    f"&fl={response_field}"
        
        r=requests.get(query_url)
        time.sleep(20)
        if r.status_code == 200:
            out = r.json()
            collection.insert_one(out)
        print("page: ",page)
        page = page + 1
        status_code = r.status_code
        print("status_code: ",status_code)

    date = datetime.strptime((out['response']['docs'][0]['pub_date'][0:10]), '%Y-%m-%d')
    begin_date = (date + timedelta(days=1)).strftime("%Y-%m-%d")
    out_status_code = r.status_code
    print("out_status_code: ",out_status_code)