from pymongo import MongoClient

cluster = MongoClient('mongodb+srv://devilgoncalo:Bdba.2102@twittercasestudy.3telq.mongodb.net/?retryWrites=true&w=majority')
db = cluster["TwitterData"]


def create_collection(collection_name: str):
    """Creates a new collection in our TwitterData database."""
    new_collection = db[collection_name]
    return new_collection


def insert_records(list_of_documents: list, collection):
    """
    Inserts a list of JSON records into the given collection and returns
    the number of documents added.
    Remember to add _id as an id parameter if you don't want mongodb to assign
    an automatic id to the record.
    """
    initial_count = collection.count_documents({})

    try:
        i = collection.insert_many(list_of_documents, ordered=False)
    except:
        print('There are records with duplicate ids, these were not inserted.\n')
    
    final_count = collection.count_documents({})
    docs_inserted = final_count - initial_count
    print(f'{docs_inserted} documents were added!')
    
    return docs_inserted
    

def delete_records(query, collection):
    """
    Deletes records in a collection according to the given query.
    Example params that would delete all the records in a collection:
    query = {"_id": {"$gte": 0}} or query = {}
    collection = stackoverflow
    """
    d = collection.delete_many(query)
    print(d.deleted_count, "documents deleted!")
    

def update_record(id: int, update_query: dict, collection):
    """
    Finds a record by its id and updates it with the update_query in the
    given collection.
    Example of the parameters:
    id = 100
    update_query = {"$set" : {"user_name" : updated_user_name}}
    collection = stackoverflow
    """
    collection.find_one_and_update({"_id": id}, update_query, upsert=False)
    print("1 record updated!")


def read_records(collection, query=None):
    '''
    Returns the records matching the query parameter from the selected
    collection. If the query parameter is empty it will return all the records
    '''
    return collection.find(query)


def count_records(collection, query={}):
    '''
    Returns the count of records matching the query parameter from the 
    selected collection. If the query parameter is empty it will return the
    count of all records in the collection.
    '''
    return collection.count_documents(query)