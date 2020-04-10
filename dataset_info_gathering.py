from pymongo import MongoClient
from artr_utilities import *
import matplotlib.pyplot as plt
from pandas.plotting import scatter_matrix



def count_english_documents(collection):
    works = collection
    en = 0
    nl = 0
    for i in works:
        print(i)
        if i["language"] == 'nl':
            nl += 1
        elif i["language"] == "en":
            en += 1
        else:
            print(i)
    print('Count en paintings: ', en)
    print("Count nl paintings: ", nl)


def correlation_scatter_dataframe(df):
    print(df)
    scatter_matrix(df, figsize=(15, 15))
    plt.matshow(df.corr())
    plt.show()


def describe_dataframe(df):
    df.describe(include="all")


def unique_artists(collection):
    names = []
    for i in collection:
        if len(i['principalMakers']) > 1:
            print("This many artists: " + str(len(i['principalMakers'])))
        for artist in i['principalMakers']:
            names.append(artist['name'])
    print(len(set(names)))

def count_wiki_summaries(collection):
    count = 0
    for i in collection:
        try:
            if i["wiki_text"] != "":
                count += 1
        except Exception as e:
            pass
    print("Wiki Summaries downloaded for %s items" % count)

def count_movements(collection):
    count = 0
    movements = {}
    for i in collection:
        try:
            m = i ["movement"]
            if m != "":
                count += 1
                if m in movements.keys():
                    movements[m] += 1
                else:
                    movements[m] = 1

        except Exception as e:
            pass
    print("Movements for %s items" % count)
    print(movements)


def count_unique_tags(collection):
    tags = []
    for i in collection:
        try:
            if i["imagga_tags"] != "":
                print(i['title'])
                for tag in i["imagga_tags"]:
                    tags.append(tag['tag'])
        except Exception as e:
            pass
    print(max(set(tags), key=tags.count))
    print(len(set(tags)))

def iconclass_count(collection):
    count = {}
    for i in range(20):
        count[i] = 0
    for i in collection:
        try:
            if i['classification']['iconClassIdentifier'] != "":
                num = len(i['classification']['iconClassIdentifier'])
                count[num] = count[num] + 1
        except Exception as e:
            pass
    print(count)

def count_cnn_features(collection):
    count = 0
    for i in collection:
        print(len(i['cnn_features']))
        return

if __name__ == '__main__':
    artwork_collection, user_collection = connect_to_mongodb()
    # df = artworks_to_dataframe(artwork_collection.find({}))
    # correlation_scatter_dataframe(df)
    count_movements(artwork_collection.find({}))
    # count_english_documents(artwork_collection.find({}))
    # count_unique_tags(artwork_collection.find({}))
    # iconclass_count(artwork_collection.find({}))
    # count_cnn_features(artwork_collection.find({}))