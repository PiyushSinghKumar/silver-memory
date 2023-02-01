from pymongo import MongoClient
import time

def user():
    try:
        client = MongoClient('mongodb://localhost:27017/')
    except:
        print("Couldnt connect")
    db = client.Ecom
    customer = db.cust
    premium = db.premium

    username = input('What is your username? ')
    password = input('Whats your password?')
    account = customer.find_one({"Username": username,"password": password})
    if not account:
        print(f'Could not find account with this username {username} or wrong password or wrong username.')
        return

    print('Logged in successfully.')
    print('Good News for you ')
    print("Wakanda has decided to introduce Loyalty program for our loyal customers ")
    print("are you interested to join?")
    join = input("[Y]es or [N]o")
    time.sleep(2)
    if join == 'y':
             for check in premium.find({"Username": username,"Premium_Customer":"TRUE"},{'_id':0,'Username':0}):
                 print("Congrats you are now a Premium Member")
                 username_1 = {"Username": username}
                 status = {"$set": {"Status": "Premium"}}
                 customer.update_one(username_1, status)
                 print("WAKANDAFOREVER !!")
             else:
                 print("sorry you are not eligible good bye")
    else :
        print("Sorry to see you go :(")












