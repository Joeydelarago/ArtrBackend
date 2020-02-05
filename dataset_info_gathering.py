from pymongo import MongoClient
from utilities import *
import matplotlib.pyplot as plt
from pandas.plotting import scatter_matrix



def count_english_documents(collection):
    works = list(collection)
    en = 0
    nl = 0
    for i in works:
        if i["language"] == 'nl':
            nl += 1
        elif i["language"] == "en":
            en += 1
            print(i["principalOrFirstMaker"])
        else:
            print(i)
    print('Count en paintings: ', en)
    print("Count nl paintings: ", nl)


def correlation_scatter_dataframe(df):
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


if __name__ == '__main__':
    artwork_collection, user_collection = connect_to_mongodb()
    # df = artworks_to_dataframe(artwork_collection.find({}))
    # correlation_scatter_dataframe(df)
    count_wiki_summaries(artwork_collection.find({}))
    # count_english_documents(artwork_collection.find({}))
