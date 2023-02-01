import redis
redis = redis.Redis(
    host='localhost',
    port='6379')

print("Please Choose a key option to find distance between as 1, 2, 3 from : \n 1. Warehouse to Delivery \n 2. Driver to Delivery \n 3. Driver to Warehouse")
i = input("Enter - ")
i = int(i)

if i == 1:
    # Combining two keys
    redis.zunionstore("Temp", ("Delivery", "Warehouse"), aggregate="MIN")

    # Expiring Temporary created key
    redis.expire("Temp", 600)

    Delivery = input("Enter Delivery name: ")
    Warehouse = input("Enter Warehouse name: ")

    Distance = redis.geodist("Temp", Warehouse, Delivery, unit="km")

    if Distance == None:
        print("Enter correct details since you have entered wrong details")
    else:
        print(" Distance: ", Distance)

elif i == 2:
    # Combining two keys
    redis.zunionstore("Temp", ("Delivery", "Driver"), aggregate="MIN")

    # Expiring Temporary created key
    redis.expire("Temp", 600)

    Delivery = input("Enter Delivery name: ")
    Driver = input("Enter Driver name: ")

    Distance = redis.geodist("Temp", Driver, Delivery, unit="km")

    if Distance == None:
        print("Enter correct details since you have entered wrong details")
    else:
        print(" Distance: ", Distance)

elif i == 2:
    # Combining two keys
    redis.zunionstore("Temp", ("Driver", "Warehouse"), aggregate="MIN")

    # Expiring Temporary created key
    redis.expire("Temp", 600)

    Warehouse = input("Enter Warehouse name: ")
    Driver = input("Enter Driver name: ")

    Distance = redis.geodist("Temp", Driver, Warehouse, unit="km")

    if Distance == None:
        print("Enter correct details since you have entered wrong details")
    else:
        print(" Distance: ", Distance)

else:
    print("Choose the correct option")
