from pymongo import MongoClient

def SA():
    try :
        client = MongoClient('mongodb://localhost:27017/')
    except:
        print("Counldnt connect")
        db = client.Ecom
        '''prem = db.order_1.aggregate([{$match: {Delivered: true}},{$group:{_id: "$Username", total: {$sum: "$Total_Amount"}}},{$sort: {total: -1}},{$limit: 47}])
        for i in prem:
            db.prem.save(prem)
            print("initialed")'''

