# Press the green button in the gutter to run the script.
import json
from typing import TextIO

if __name__ == '__main__':

    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client['Product']
    collection_product = db['Discount']
    collection_Order = db['Orders']
    collection_Customer = db['Customer']
    collection_exclusiveDeals=db['Deals']



with open('E:/Mongo Data/ProductData.json', encoding='utf-8') as f:
    file_data = json.load(f)

with open(r'E:/Mongo Data/OrderTable (3).json', encoding='utf-8') as d:
    file_order_data = json.load(d)

with open('E:/Mongo Data/CustomerData (3).json', encoding='utf-8') as e:
    file_customer_data = json.load(e)

with open('E:/Mongo Data/Deals.json', encoding='utf-8') as s:
    file_exclusive_deals = json.load(s)


collection_exclusiveDeals.insert_many(file_exclusive_deals)
collection_Customer.insert_many(file_customer_data)
collection_Order.insert_many(file_order_data)
collection_product.insert_many(file_data)


#Display all table
for doc1 in collection_Customer.find({}):
      print(doc1)
for doc2 in collection_product.find({}):
      print(doc2)
for doc3 in collection_Order.find({}):
      print(doc3)
for doc4 in collection_exclusiveDeals.find({}):
      print(doc4)

#Insert a product in Deal collection
collection_exclusiveDeals.insert_one({"BookID":"19230","Title":"Cultus","Author":"Fanya","Average_Rating":5,
                                      "Language":"Swahili","Text_Review":3,"Publication_Date":"7/26/2018",
                                      "Publisher":"Stracke-Breitenberg","Out_Of_Stock":False,"Actual_Price":748,
                                      "Selling_Price":927,"Customer_ID":20})
data=collection_exclusiveDeals.find_one({"BookID":"19230"},{"_id":0,"Title":1,"Author":1,"Selling_Price":1})
print("data inserted")
print(data)



#Delete Discount
collection_product.delete_one({"Products.Books":"6256"})

##################################################################################################
#update mobile discount on Selling Price
def products_discount_sp():
    Discount_Mobile =[{"$addFields": {"Products.Phones.Discount": {"$divide": ["$Products.Phones.Selling_Price",12.0]}}},
        {"$addFields": {"Products.Phones.TotalPrice": {"$subtract": ["$Products.Phones.Selling_Price",{"$round" : [ "$Products.Phones.Discount", 1 ]} ]}}},
        {"$project": {"_id":0,"Products.Phones.Brand": 1,"Products.Phones.Actual_Price": 1,"Products.Phones.Discount": "$Products.Phones.Discount",
                "Products.Phones.TotalPrice": "$Products.Phones.TotalPrice"}}]
    cursor = collection_product.aggregate(Discount_Mobile)
    for doc in cursor:
        print(doc)

products_discount_sp()

def exclusive_discount():
    ex_discount = [{"$project": {"Customer": "$$ROOT"}},
        {"$lookup": {"localField": "Customer.CustomerID","from": "Orders","foreignField": "Customer_ID","as": "Orders"}},
        {"$unwind": {"path": "$Orders"}},{"$match": {"Customer.Premium_Customer": True}},{"$project": {"Orders.price": "$Orders.price",
                "Customer.Customer_Name": "$Customer.Customer_Name",
                "Discount": {"$divide": ["$Orders.price",10.0]}}}]

    cursor1 = collection_Customer.aggregate(ex_discount)
    for doc in cursor1:
        print(doc)

exclusive_discount()

###############################################################################
#Get Exclusive Discount

def exclusive_deals():
    ex_deals = [
        {"$project": {"_id": 0,"Deals": u"$$ROOT"}},
        {u"$lookup": {"localField": "Deals.Customer_ID","from": "Customer","foreignField": "CustomerID","as": "Customer"}},
        {"$project": {"Deals.Publisher": "$Deals.Publisher","Deals.Language": "$Deals.Language","Deals.Actual_Price": "$Deals.Actual_Price",
            "Deals.Customer_ID": "$Deals.Customer_ID","_id": 0}
        }
    ]

    cursor = collection_exclusiveDeals.aggregate(ex_deals)
    for dealsdoc in cursor:
        print(dealsdoc)

        client.close()
exclusive_deals()
