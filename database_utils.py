from utilities import connect_to_mongodb

def remove_field(collection, field):
    collection.update_many({}, {"$unset": {field: 1}})

def remove_artwork_duplicates(collection):
    artworks = list(collection)
    ids = list(map(lambda x: x["id"], artworks))

    for i in artworks:
        if ids.count(i["id"]) > 1:
            artwork_collection.delete_many({"id" : i["id"]})
            artwork_collection.insert(i)
            print(ids.count(i["id"]))

def collection_size(collection):
    print(len(list(collection)))

if __name__ == "__main__":
    artwork_collection, user_collection = connect_to_mongodb()
    remove_artwork_duplicates(artwork_collection.find({}))
    collection_size(artwork_collection.find({}))

