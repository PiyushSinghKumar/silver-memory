import random
import math
import redis

redis = redis.Redis(
    host='localhost',
    port='6379')


# storing strings in a list
digits = [i for i in range(0, 10)]

# initializing a string
random_str = ""

# we can generate any lenght of string we want
for i in range(6):
    # generating a random index
    # if we multiply with 10 it will generate a number between 0 and 10 not including 10
    # multiply the random.random() with length of your base list or str

    index = math.floor(random.random() * 10)
    random_str += str(digits[index])


OrderDeliver = input("Are you waiting for an OTP? Y/N: ")
if OrderDeliver == "Y":
    # Storing OTP in redis server
    redis.set("OTP_Driver", random_str)
    redis.expire("OTP_Driver", 600)

    redis.set("OTP_Customer", random_str)
    redis.expire("OTP_Customer", 600)
    print("OTP: ", random_str)

elif OrderDeliver == "N":
    print("Please wait for the order to be delivered")

else:
    print("Please enter only Y or N")
