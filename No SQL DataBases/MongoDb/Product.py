import json

from bson import ObjectId
from pymongo import MongoClient, ReturnDocument

client = MongoClient('localhost', 27017)
Product = client['Product']
Inventory_Products = Product['Product Details']

with open("C://Users/Shreyash Anand/Desktop/DE Project/ProductData.json", encoding='utf-8') as f:
    file_data = json.load(f)

#Insert Product

my_data = {
    "Products": {
        "Books": dict(Product_ID="234567", Title="Lost in the Dark", Author="Anestassia", Average_Rating=5,
                      Language="Eng", Text_Review=5, Publication_Date="12/12/2021", Publisher="Brooks",
                      Out_Of_Stock="false", Actual_Price=500, Selling_Price=700)
    }
}
Inventory_Products.insert_one(my_data)
print("Product Added in the Inventory ", my_data)

#Update

Inventory_data = {"_id": ObjectId("620540fb6310b17584071084")}
find_result = Product["Product Details"].find_one(Inventory_data)
print(find_result)

if find_result != "None":
    Inventory_Products.find_one_and_update({"_id": ObjectId("620540fb6310b17584071084")},
                                           {"$set":
                                                {"Products.Books.Selling_Price": "230000"},
                                            }, upsert=True)
    print("The Updated Product data was-", find_result)
else:
    print("No such Product Details exist")

# Delete Product

Product_data={"_id": ObjectId("620540fb6310b17584071084")}
find_result = Product["Product Details"].find_one(Product_data)
print(find_result)

#print(find_result)
#print(type(find_result))

if find_result != "None":
    Product_details_update = Inventory_Products.delete_one({"_id": ObjectId("620540fb6310b17584071084")})
    print("The record of product is deleted.", Product_details_update)
else:
    print("No such Product Details exist")

client.close()
