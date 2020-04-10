from random import randint

from flask import Flask, request, jsonify
from pymongo import MongoClient
from collections import Counter
import numpy as np
import pandas as pd




app = Flask(__name__)


@app.route("/")
def index():
    return "This is root!!!!"


@app.route('/api/images/<id>')
def get_artworks(id):
    artworks = get_artworks_jaccard_set(id, 20)
    print("artwork suggestions", end="")
    print(artworks)
    return jsonify(artworks)


@app.route('/api/images/result/<id>', methods=['POST'])
def image_results(id):
    user_data = user_collection.find_one({'user': id})
    if user_data is None:
        user_collection.insert({"user": id, "artworks": {}})
    else:
        results = dict(request.json)
        for name, liked in results.items():
            user_collection.update({"user": id}, {"$set": {"artworks.%s" % name: liked}})
    user_data2 = user_collection.find_one({'user': id})
    return "", 200


def get_user_artwork_titles(id):
    user_data = user_collection.find_one({'user': id})
    if user_data != None:
        artwork_titles = list(user_data['artworks'].keys())
    else:
        artwork_titles = []
    return artwork_titles


def get_user_artwork_documents(id):
    titles = get_user_artwork_titles(id)
    return artwork_collection.find({'title': {'$in': titles}})


def get_artworks_random(id, amount):
    cursor = artwork_collection.aggregate([{'$sample': {'size': amount}}])
    artworks = []
    for item in cursor:
        if item['title'] not in get_user_artwork_titles(id):
            try:
                artworks.append(
                    {'id': item['id'], 'name': item['title'], 'image_url': item['webImage']['url']})

            except Exception as e:
                print(item)
                print(e)
    return artworks


def get_artworks_jaccard_set(id, amount):
    user_artworks = user_collection.find_one({'user': id}, {"artworks": 1, "_id": 0})
    liked_artwork_documents = []
    disliked_artwork_documents = []

    if user_artworks != None:
        user_artworks = dict(user_artworks)['artworks']
        liked_artwork_titles = [work for work, liked in user_artworks.items() if liked == True]
        disliked_artwork_titles = [work for work, liked in user_artworks.items() if liked == False]
        artwork_titles = list(user_artworks.keys())
        liked_artwork_documents = artwork_collection.find({'title': {'$in': liked_artwork_titles}})
        disliked_artwork_documents = artwork_collection.find({'title': {'$in': disliked_artwork_titles}})
    else:
        print("user_artworks is None")

    liked_identifiers = set()
    disliked_identifiers = set()

    classes = []

    for work in liked_artwork_documents:
        # Adding all of the different iconClass identifiers to the set identifiers
        classes = classes + work['classification']['iconClassIdentifier']
        # liked_identifiers.update(set(work['classification']['iconClassIdentifier']))
    counter = Counter(classes)
    liked_identifiers.update([x[0] for x in counter.most_common(10)])

    classes = []
    for work in disliked_artwork_documents:
        classes = classes + work['classification']['iconClassIdentifier']

    counter = Counter(classes)
    disliked_identifiers.update([x[0] for x in counter.most_common(10)])

    suggested_artworks = []

    if len(liked_identifiers) > 0:
        cursor = artwork_collection.aggregate([{'$sample': {'size': 500}}])
        similar_artworks_jacc_sim = {}
        similar_artworks_by_title = {}

        for work in cursor:
            liked_identifier_set = np.array(list(liked_identifiers))
            disliked_identifier_set = np.array(list(disliked_identifiers))
            work_identifier_set = np.array(work['classification']['iconClassIdentifier'])
            jac_sim_liked = np.intersect1d(liked_identifier_set, work_identifier_set).size / np.union1d(liked_identifier_set, work_identifier_set).size
            jac_sim_disliked = np.intersect1d(disliked_identifier_set, work_identifier_set).size / np.union1d(disliked_identifier_set, work_identifier_set).size

            if work['title'] not in get_user_artwork_titles(id):
                print("%s - %s = %s" %(jac_sim_liked, jac_sim_disliked, jac_sim_liked - jac_sim_disliked))
                similar_artworks_jacc_sim[work['title']] = jac_sim_liked - jac_sim_disliked
                similar_artworks_by_title[work['title']] = work

        max_similar_works = sorted(similar_artworks_jacc_sim, key=similar_artworks_jacc_sim.get, reverse=True)[:amount]
        for work in [similar_artworks_by_title[title] for title in max_similar_works]:
            suggested_artworks.append({'id': work['id'], 'name': work['title'], 'image_url': work['webImage']['url']})

    else:
        print("List of user artworks is empty")

    #Add random suggestions to make up the missing items
    if len(suggested_artworks) == 0:
        #This has to be done otherwise if you append to the empty list it nests that list inside
        #instead of appending all the items in it
        suggested_artworks = get_artworks_random(id, amount)
    elif len(suggested_artworks) < amount:
        suggested_artworks.append(get_artworks_random(id, amount - len(suggested_artworks)))

    return suggested_artworks

def suggest_artworks(num=10):
    pass

def artworks_to_dataframe(cursor):
    artworks = []
    for i in cursor:
        artwork = {'techniques': i['techniques'], 'materials': i['materials'], 'yearEarly': i['dating']['yearEarly'], 'iconClass': i['classification']['iconClassIdentifier']}
        artworks.append(artwork)

    return pd.DataFrame(artworks)


def store_user_data():
    old_user_collection.drop()
    old_user_collection.insert(user_collection.find({}))

def load_user_data():
    user_collection.drop()
    user_collection.insert(old_user_collection.find({}))

def delete_artworks_missing_iconclass():
    count = 0
    count2 = 0

    #Get all artworks
    artwork_documents = artwork_collection.find({})

    for i in artwork_documents:
        count2 += 1
        if i['classification']['iconClassIdentifier'] == []:
            #Delete artwork if it's missing identifiers
            count += 1
            artwork_collection.delete_one({'id': i['id']})

    print("Count missing iconclass: %s" % count)
    print("Count Total: %s" % count2)

def print_dataframe_info(df):
    print(df.shape)

# def cross_val_score(df):
#     numeric_features = ["yearEarly"]
#     nominal_features = ["techniques", "materials", "iconClass"]
#     preprocessor = ColumnTransformer([("num", StandardScaler(), numeric_features),
#                                       ("nom", OneHotEncoder(handle_unknown="ignore"),
#                                        nominal_features)], remainder="drop")
#
#     pipeline = Pipeline([("pre", preprocessor), ("est", LinearRegression())])
#     y = df["mpg"].values
#     np.mean(cross_val_score(pipeline, df, y, scoring="neg_mean_absolute_error", cv=10))

if __name__ == '__main__':
    client = MongoClient("mongodb://0.0.0.0:45536")
    db = client["artr"]
    artwork_collection = db["artworks"]
    user_collection = db["users"]
    old_user_collection = db["old_users"]
    print(db.command("dbstats"))
    # print_dataframe_info(artworks_to_dataframe(get_user_artwork_documents('1')))
    app.run(debug=True, host='0.0.0.0', port=45537)