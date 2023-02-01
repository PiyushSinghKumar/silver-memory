import json

from bson import ObjectId
from pymongo import MongoClient
from pymongo.collection import ReturnDocument

client = MongoClient('localhost', 27017)
Staff = client['Staff']
Staff_Collection = Staff['Staff Details']

with open("C://Users/Shreyash Anand/Desktop/DE Project/Staff_Data.json", encoding='utf-8') as f:
    file_data = json.load(f)

# Insert Staff Details
staff_details = {"Staff Name": "John Mans",
                 "Staff Address": "BS 13 Heidelberg",
                 "Staff Email": "john.mans@gmail.com",
                 "Staff Date of Joining": "21/02/2015",
                 "Gender": "Male"
                 }

Staff_Details_Insert = Staff_Collection.insert_one(staff_details)

# Update Staff Details

staff_data = {"_id": ObjectId("62054566b9abe827da011cd2")}
find_result = Staff_Collection["Staff Details"].find_one(staff_data)
print(find_result)

if find_result != "None":
    updated_data = {
        "_id": ObjectId("62054566b9abe827da011cd2"),
        "email": "testing123@gmail.com"
    }

    Staff_details_update = Staff_Collection.update_many({"_id": ObjectId("62054566b9abe827da011cd2")},
                                                           {"$set":
                                                                {"Staff Email": "tester@gmail.com"}
                                                            }, upsert=True, return_document=ReturnDocument.AFTER)
    print("The Updated Staff Details are -", Staff_details_update)
    # print("Found Staff Details:", find_result)
else:
    print("No such Staff Details exist")

# delete

staff_data = {"_id": ObjectId("62054566b9abe827da011cd2")}
find_result = db["Staff Details"].find_one(staff_data)
print(find_result)

# print(find_result)
# print(type(find_result))

if find_result != "None":
    updated_data = {
        "_id": ObjectId("62054566b9abe827da011cd2"),
        "email": "testing123@gmail.com"
    }

    Staff_details_update = Staff_Collection.delete_one({"_id": ObjectId("62054566b9abe827da011cd2")})
    print("The record of staff is deleted.", Staff_details_update)
    # print("Found Staff Details:", find_result)
else:
    print("No such Staff Details exist")

# Staff_Details_Insert = collection_currency.update_one(Staff_Details)
client.close()
