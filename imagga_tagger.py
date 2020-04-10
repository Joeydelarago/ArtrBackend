import pymongo
import requests
from artr_utilities import *
from wikipedia_scraping import open_id_file

api_key = 'acc_ca02bf645611730'
api_secret = '90bc931bb4840ee124ad32fe9bc120cf'


def get_imagga_tags():
    title_file, last_title = open_id_file()
    collection, _ = connect_to_mongodb()
    try:
        works = list(collection.find({}).sort([("title", pymongo.ASCENDING)]))

        print(last_title)
        if last_title != "":
            works = resume_from(last_title, works)
            print("Resuming from: " + last_title)
        for work in works:
            print(work['title'])
            url = work['webImage']['url']
            response = requests.get(
                'https://api.imagga.com/v2/tags?image_url=%s' % url,
                auth=(api_key, api_secret))


            tags = clean_response(response.json())

            artwork_collection.update({"_id": work["_id"]},
                                      {"$set": {"imagga_tags": tags}})  

            last_title = work["title"]
    finally:
        title_file.write(last_title)
        title_file.close()

def clean_response(response):

    d = dict(response)
    output = []
    for tag in d['result']['tags']:
        if tag['confidence'] > 35:
            output.append({'confidence': tag['confidence'], 'tag' : tag['tag']['en']})
    return output

if __name__ == "__main__":
    artwork_collection, user_collection = connect_to_mongodb()
    get_imagga_tags()