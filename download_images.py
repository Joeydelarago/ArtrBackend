import requests
import os

from utilities import connect_to_mongodb

def resume_from(title, works):
    for i in range(len(works)):
        if works[i]["title"] == title:
            print("%s artworks remaining" % (len(works) - i))
            return works[i:]
    print("'title' not found in list")
    return []

if __name__ == '__main__':
    artwork_collection, user_collection = connect_to_mongodb()
    artworks = list(artwork_collection.find({}))
    # artworks = resume_from("Square Man", artworks)
    for i in artworks:
        try:
            # skip if image is already downloaded
            if os.path.exists("images/" + i["id"]):
                continue
            print(i["title"])
            f = open("images/" + i["id"], 'wb')
            f.write(requests.get(i['webImage']['url']).content)
            f.close()
        except Exception as e:
            print(e)
