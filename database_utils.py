from artr_utilities import *

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

def unique_users():
    _, user_collection = connect_to_mongodb()
    users = list(user_collection.find({}))
    for user in users:
        print("User ID: " + user['user'], end=" ")
        print("Count Artworks: " + str(len(user['artworks'])))

def print_three_artworks():
    artwork_collection, _ = connect_to_mongodb()
    artworks = list(artwork_collection.find({}))
    for i in range(3):
        print(artworks[i])

def remove_works_without_image():
    artwork_collection, _ = connect_to_mongodb()
    artworks = list(artwork_collection.find({}))
    count = 0
    for work in artworks:
        try:
            url = work['webImage']['url']
        except TypeError:
            count += 1
            artwork_collection.delete_one({"id": work["id"]})
    print(count)

def clear_cnn_features():
    artwork_collection, _ = connect_to_mongodb()

    query = {"address": "Valley 345"}
    newvalues = {"$set": {"cnn_features": {}}}

    artwork_collection.update(query, newvalues)

def find_all_with_title(title):
    artwork_collection, _ = connect_to_mongodb()
    query = {"title": title}
    items = artwork_collection.find(query)
    for i in items:
        print(i)

def remove_non_paintings():
    artwork_collection, _ = connect_to_mongodb()
    # 'objectCollection': ['paintings'],
    query = {"$nor": [{"objectCollection" : ['paintings']}]}
    print(len(list(artwork_collection.find(query))))
    artwork_collection.delete_many(query)



if __name__ == "__main__":
    artwork_collection, user_collection = connect_to_mongodb()
    # remove_artwork_duplicates(artwork_collection.find({}))
    # collection_size(artwork_collection.find({}))
    # remove_works_without_image()
    # print_three_artworks()
    # title = "Still Life with Peacocks"
    # find_all_with_title(title)
    # clear_cnn_features()
    remove_non_paintings()

