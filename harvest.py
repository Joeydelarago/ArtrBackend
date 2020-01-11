#!/usr/bin/env python3
import requests
from pymongo import MongoClient

import sys
import json
url="https://www.rijksmuseum.nl/api/en/collection?key=8PkrYFyD&format=json&type=painting&imgonly=True&p=%s&ps=100"
url1="https://www.rijksmuseum.nl/api/en/collection/%s?key=8PkrYFyD&format=json"


def harvest_from_ids():
    last_id = ""

    # Check if ids file is present
    try:
        ids_file = open("painting_id.txt", "r")
        ids = ids_file.readlines()
        ids_file.close()
    except IOError:
        # File does not exist
        raise Exception("You need to supply an input file of art object ids")

    # check at what the last line the file stopped at was
    try:
        last_ids_file = open("lastid.txt", "+r")
        last_id = last_ids_file.readline()
        last_ids_file.close()
    except IOError:
        # File does not exist so it needs to be created
        last_ids_file = open("lastid.txt", "+w")
        last_ids_file.close()

    failed_file = open("failedDownloads.txt", "+a")
    last_ids_file = open("lastid.txt", "+w")

    if len(last_id) > 0:
        ids = ids[ids.index(last_id):]

    client = MongoClient("mongodb://0.0.0.0:45536")
    db = client["artr"]
    collection = db["artworks"]

    for id in ids:
        try:
            response = requests.get(url1 % id.strip())

            print(id.strip())
            if response.status_code == 500:
                failed_file.write(id)
                print(response.status_code, url1 % id.strip())
            else:
                print(response.status_code, url1 % id.strip())
                collection.insert(response.json()["artObject"])
        except:
            last_ids_file.write(id)
            last_ids_file.close()
            failed_file.close()

    failed_file.close()
    last_ids_file.close()

def get_ids():
    try:
        ids_file = open("painting_id.txt", "a")
    except IOError:
        # File does not exist
        raise Exception("Idk tbh")

    page = 0


    try:
        while True:
            response = requests.get(url % page)
            data = json.loads(response.text)
            page += 1

            for i in data["artObjects"]:
                ids_file.write(i["objectNumber"] + "\n")

            print(page)




    except Exception as e:
        print(e)
        ids_file.close()


if __name__ == "__main__":
    harvest_from_ids()

