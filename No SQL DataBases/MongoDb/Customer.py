import json

from bson import ObjectId
from pymongo import MongoClient
from pymongo.collection import ReturnDocument

client = MongoClient('localhost', 27017)
Customer = client['Customer']
CUstomer_Details = Customer['Customer Details']

with open("C://Users/Shreyash Anand/Desktop/DE Project/CustomerData.json", encoding='utf-8') as f:
    file_data = json.load(f)

Customer_Details_Insert = CUstomer_Details.insert_one(file_data)
client.close()
