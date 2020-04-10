import pandas as pd
from pymongo import MongoClient
import database_utils


def artworks_to_dataframe(cursor):
    # This is only for raw artworks not user liked artworks
    artworks = []
    features = ['dissimilarity',
                'contrast',
                'energy',
                'correlation',
                # 'wiki_text',
                'movement']
    for i in cursor:
        artwork = {
            # 'techniques': i['techniques'],
            #        'materials': i['materials'],
                   'yearEarly': i['dating']['yearEarly'],
                   # 'iconClass': i['classification']['iconClassIdentifier'],
                   # 'descriptionText': i['description']
        }
        for f in features:
            if f in i.keys():
                artwork[f] = i[f]
        artworks.append(artwork)

    return pd.DataFrame(artworks)


def resume_from(title, works):
    for i in range(len(works)):
        if works[i]["title"] == title:
            print("%s artworks remaining" % (len(works) - i))
            return works[i:]
    print("'title' not found in list")
    return []


def get_all_artworks():
    collection, _ = connect_to_mongodb()
    return collection.find({})


def get_user_artworks_dataframe(user="116287988939301391169"):
    # Get dataframe of artworks for my user id
    artwork_collection, user_collection = connect_to_mongodb()

    works = list(user_collection.find({'user': user}))[0]['artworks']

    # List of features for adding and removing them from dataframe easily
    features = ['dissimilarity',
                'contrast',
                'energy',
                'correlation',
                'wiki_text',
                'movement_text',
                'imagga_tags',
                'movement',
                'cnn_features']

    examples = []


    for work, liked in works.items():
        artwork = artwork_collection.find_one({"title": work})
        if artwork == None:
            # print("Couldn't find: " + work)
            continue
        i = dict(artwork)
        like = 1 if liked else 0
        iconClass = ""

        if len(i['classification']['iconClassIdentifier']) > 1:
            iconClass = " ".join(i['classification']['iconClassIdentifier'])

        example = {'yearEarly': i['dating']['yearEarly'],
                   'techniques': " ".join(i['techniques']),
                   'materials': " ".join(i['materials']),
                   'iconClass': iconClass}

        tags = ""
        try:
            for tag in i['imagga_tags']:
                tags = tags + " " + tag['tag']
        except KeyError:
            pass
        example['imagga_tags_text'] = tags

        for f in features:
            if f in i.keys():
                example[f] = i[f]
            elif f == 'movement_text' or f == 'wiki_text':
                example[f] = ""
            elif f == 'imagga_tags':
                example[f] = []

        if i['label']['description'] == None:
            example["description"] = ""
        else:
            example["description"] = i['label']['description']

        example['liked'] = like

        examples.append(example)
    # user_artworks = {**user_artworks, **i["artworks"]}

    return pd.DataFrame(examples)

def get_user_cnn_feature_frame(user="116287988939301391169"):
    # Get dataframe of artworks for my user id
    artwork_collection, user_collection = connect_to_mongodb()

    works = list(user_collection.find({'user': user}))[0]['artworks']

    examples = []

    for work, liked in works.items():
        print(work)

        artwork = artwork_collection.find_one({"title": work})

        if artwork == None:
            continue

        i = dict(artwork)

        like = 1 if liked else 0

        example = {}

        for j in range(4096):
            example[str(j)] = i['cnn_features'][j]


        example['liked'] = like

        examples.append(example)

    return pd.DataFrame(examples)

def get_user_images(user="116287988939301391169"):
    # Get images for training neural network
    artwork_collection, user_collection = connect_to_mongodb()
    works = list(user_collection.find({'user': user}))[0]['artworks']

    filenames = []
    likes = []

    for title, liked in works.items():
        artwork = artwork_collection.find_one({"title": title})

        if artwork == None:
            # print("Couldn't find: " + title)
            continue

        if liked:
            likes.append("liked")
        else:
            likes.append("disliked")

        filenames.append(artwork["id"] + ".jpg")

    df = pd.DataFrame({
        'filename': filenames,
        'liked': likes
    })
    return df

def get_artwork_cnn_frame():
    # Get dataframe of artworks for my user id
    artwork_collection, _ = connect_to_mongodb()

    works = list(artwork_collection.find({}))

    examples = []
    ids = []

    for work in works:
        examples.append(list(work['cnn_features']))
        ids.append(work['id'])

    return examples, ids

def connect_to_mongodb():
    client = MongoClient("mongodb://0.0.0.0:45536")
    db = client["artr"]
    artwork_collection = db["artworks"]
    user_collection = db["users"]
    old_user_collection = db["old_users"]
    return artwork_collection, user_collection

if __name__ == "__main__":
    pass
