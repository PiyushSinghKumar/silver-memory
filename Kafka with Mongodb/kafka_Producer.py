import requests as re
import pprint
from kafka import KafkaProducer
import time
import json
producer = KafkaProducer(bootstrap_servers="localhost:9092")
data = re.get("https://developer.nrel.gov/api/alt-fuel-stations/v1.json?api_key=xt60OBgzugNRwrF1OXGkmXhBCLAKw4PQ1QNcE9Da&fuel_type=ELEC")

# &limit=1
# print("limit remaining", data.X-RateLimit-Remaining)

pprint.pprint(data.json()['fuel_stations'])
# pprint.pprint(data.json())

fuel_station_list = data.json()['fuel_stations']

# # print(type(fuel_station_list))

# # print(len(data.json()))
producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# data
for i in fuel_station_list:
    # print(i)
    producer.send("EV", i)
    # producer.close()
    # print(i)
    # time.sleep(2)
    producer.flush()