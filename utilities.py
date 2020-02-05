import pandas as pd
from pymongo import MongoClient


def artworks_to_dataframe(cursor):
    artworks = []
    for i in cursor:
        artwork = {'techniques': i['techniques'],
                   'materials': i['materials'],
                   'yearEarly': i['dating']['yearEarly'],
                   'iconClass': i['classification']['iconClassIdentifier'],
                   'dissimilarity': i['dissimilarity'],
                   'contrast': i['contrast'],
                   'energy': i['energy'],
                   'correlation': i['correlation'],
                   'wikiText': i['wiki_text'],
                   'descriptionText': i['description']}
        artworks.append(artwork)

    return pd.DataFrame(artworks)


def connect_to_mongodb():
    client = MongoClient("mongodb://0.0.0.0:45536")
    db = client["artr"]
    artwork_collection = db["artworks"]
    user_collection = db["users"]
    old_user_collection = db["old_users"]
    return artwork_collection, user_collection
