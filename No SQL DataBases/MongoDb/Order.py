import json
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
Order = client['Order']
Order_Details = Order['Order Details']

with open("C://Users/Shreyash Anand/Desktop/DE Project/OrderTable.json", encoding='utf-8') as f:
    file_data = json.load(f)

Order_Details.insert_many(file_data)
# collection_currency.insert_one(file_data)

client.close()