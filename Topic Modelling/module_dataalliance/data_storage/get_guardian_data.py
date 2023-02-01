import requests
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
Articles = myclient.guardian_articles
collection = Articles.guardian_collection

query = "(covid OR Covid)"
query_fields = "body"
section = "news" 
from_date = "2022-02-01"

page = 1
status_code = 200

while status_code == 200:
    query_url = f"https://content.guardianapis.com/search?" \
            f"api-key={'9d3d5b03-3d13-45a1-b8c2-95de7d7da4e0'}" \
            f"&q={query}" \
            f"&query-fields={query_fields}" \
            f"&section={section}" \
            f"&from-date={from_date}" \
            f"&show-fields=body,shortUrl" \
            f"&page-size={'50'}" \
            f"&page={page}"

    r = requests.get(query_url)
    if r.status_code == 200:
        out = r.json()
        collection.insert_one(out)

    page = page + 1

    status_code = r.status_code