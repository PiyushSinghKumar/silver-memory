import redis

redis = redis.Redis(
    host='localhost',
    port='6379')


def enterlocation():
    Longitude = float(input("Longitude: "))
    Latitude = float(input("Latitude: "))
    MemberName = input("Enter Member name: ")
    redis.geoadd(Keyname, (Longitude, Latitude, MemberName))


List = ["Delivery", "Driver", "Warehouse"]
print("Please Choose a key as 1, 2, 3 from : \n 1. Delivery \n 2. Driver \n 3. Warehouse \n 4. Enter new Key")
i = input("Enter - ")
i = int(i)

if i <= 3:
    i = i-1
    Keyname = List[i]
    print(Keyname)
    enterlocation()

elif i == 4:
    Keyname = input("Key: ")
    print(Keyname)
    enterlocation()
else:
    print("Choose correct option")
