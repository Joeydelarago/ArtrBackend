#!/usr/bin/env python3
import requests
from pymongo import MongoClient

import sys
import json

from artr_utilities import connect_to_mongodb

url="https://www.rijksmuseum.nl/api/en/collection?key=8PkrYFyD&format=json&type=painting&imgonly=True&p=%s&ps=100"
url1="https://www.rijksmuseum.nl/api/en/collection/%s?key=8PkrYFyD&format=json"


def harvest_from_ids():
    collection, _ = connect_to_mongodb()

    last_id = ""

    failed_file = open("txt_files/failedDownloads.txt", "w+")

    # Check if ids file is present
    try:
        ids_file = open("txt_files/painting_id.txt", "r")
        ids = ids_file.readlines()

    except IOError:
        # File does not exist
        raise Exception("You need to supply an input file of art object ids")

    # check at what the last line the file stopped at was
    try:
        last_ids_file = open("txt_files/lastid.txt", "+r")
        last_id = last_ids_file.readline()
    except IOError:
        last_ids_file = open("txt_files/lastid.txt", "w+")



    if len(last_id) > 0:
        ids = ids[ids.index(last_id):]

    for id in ids:
        try:
            response = requests.get(url1 % id.strip())

            print(id.strip())
            if response.status_code == 500:
                failed_file.write(id)
                print(response.status_code, url1 % id.strip())
            else:
                print("inserting")
                collection.insert(response.json()["artObject"])
        finally:
            last_ids_file.write(id)


    last_ids_file.close()
    failed_file.close()
    failed_file.close()
    last_ids_file.close()

def get_ids():
    downloaded_ids = list(map(lambda x: x["id"][3:], list(artwork_collection.find({}))))
    print(downloaded_ids)
    try:
        ids_file = open("txt_files/painting_id.txt", "a")
    except IOError:
        # File does not exist
        raise Exception("Idk tbh")

    page = 0

    items = 0


    try:
        while True:
            response = requests.get(url % page)
            data = json.loads(response.text)
            page += 1

            for i in data["artObjects"]:
                if i["objectNumber"] not in downloaded_ids:
                    ids_file.write(i["objectNumber"] + "\n")
                    items+=1
            if len(data['artObjects']) > 0:
                print(page)
            else:
                exit()




    except Exception as e:
        print(e)
        ids_file.close()


if __name__ == "__main__":
    artwork_collection, user_collection = connect_to_mongodb()
    harvest_from_ids()

