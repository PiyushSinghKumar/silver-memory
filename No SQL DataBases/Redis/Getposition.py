import redis
redis = redis.Redis(
    host='localhost',
    port='6379')

List = ["Delivery", "Driver", "Warehouse"]
print("Please Choose a key option as 1, 2, 3 from : \n 1. Delivery \n 2. Driver \n 3. Warehouse")
i = input("Enter - ")
i = int(i)

if i <= 3:
    i = i-1
    Keyname = List[i]
else:
    print("Enter correct key")

MemberName = input("Enter Member name: ")

Location = redis.geopos(Keyname, MemberName)

if Location == [None]:
    print("Enter correct details since you have entered wrong details")
else:
    print(" Coordinates: ", Location)
