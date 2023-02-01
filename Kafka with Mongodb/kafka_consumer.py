# from kafka import KafkaConsumer
# consumer = KafkaConsumer(bootstrap_servers="localhost:9092", enable_auto_commit=False)
# consumer.subscribe("EV")
# for msg in consumer:
#     print(msg.value.decode("utf-8"))
#     consumer.commit_async()

from kafka import KafkaConsumer
from pymongo import MongoClient
import json

try:
    client = MongoClient('mongodb://localhost:27017/') 
except:
    print("Could not connect to MongoDB")

db = client.DataEngineering2

EV = db.EV

if __name__ == "__main__":
    consumer = KafkaConsumer("EV",bootstrap_servers = ['localhost:9092'],
                            auto_offset_reset='earliest')
    print("starting the consumer")
    

    for msg in consumer:
        # print("EV = {}".format(json.loads(msg.value)))
        # print(type(json.loads(msg.value)))
        # EV.insert_many(msg.value)
        EV.insert_one(json.loads(msg.value))