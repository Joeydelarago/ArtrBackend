import re

import pymongo
import wikipedia
from pymongo import MongoClient

from utilities import connect_to_mongodb


def resume_from(title, works):
    for i in range(len(works)):
        if works[i]["title"] == title:
            print("%s artworks remaining" % (len(works) - i))
            return works[i:]
    print("'title' not found in list")
    return []

def open_id_file():
    try:
        last_ids_file = open("txt_files/lasttitle.txt", "+r")
        lines = last_ids_file.read().splitlines()

        last_title = ""
        if len(lines) > 0:
            last_title = lines[-1]

        return open("txt_files/lasttitle.txt", "+w"), last_title

    except IOError:
        # File does not exist so it needs to be created
        last_ids_file = open("txt_files/lasttitle.txt", "+w")
        return last_ids_file, ""

def download_images(collection):
    title_file, last_title = open_id_file()
    try:
        works = list(collection.sort([("title", pymongo.ASCENDING)]))

        if last_title != "":
            works = resume_from(last_title, works)
            print("Resuming from: " + last_title)

        for i in works:
            print(i["title"])
            results = wikipedia.search(i["title"], results=10)

            # Don't search paintings called self portrait
            if i["title"].lower() == "self-portrait" or "wiki_text" in i.keys():
                continue

            for page in results:
                try:
                    if page in ["self-portrait", "still life"]:
                        continue

                    p = wikipedia.page(page)
                    words = p.content.split()
                    num_occurances_painting = words.count('painting')
                    if num_occurances_painting > 2:
                        summary = p.summary
                        summary = re.sub("([\(\[]).*?([\)\]])", "", summary)
                        summary = re.sub(r'[0-9]+', '', summary)
                        summary = summary.replace(i["title"], "")
                        artwork_collection.update({"_id": i["_id"]},
                                                  {"$set": {"wiki_text": summary}})
                        print(summary)
                        print(page)
                        break
                except wikipedia.exceptions.PageError:
                    pass
                except wikipedia.exceptions.DisambiguationError:
                    pass
            last_title = i["title"]
            print("-" * 100)

    finally:
        title_file.write(last_title)
        title_file.close()

def download_images(collection):
    title_file, last_title = open_id_file()
    movements = []
    with open("txt_files/art_movements.txt", "r") as f:
        for movement in f:
            movements.append(movement)

    print(movements)

    try:
        works = list(collection.sort([("title", pymongo.ASCENDING)]))

        if last_title != "":
            works = resume_from(last_title, works)
            print("Resuming from: " + last_title)

        for i in works:
            try:
                if i["wiki_text"] != "":
                    print(i["title"])
                    results = wikipedia.search(i["title"], results=10)

                    # Don't search paintings called self portrait
                    if i["title"].lower() == "self-portrait" or "wiki_text" in i.keys():
                        continue

                    for page in results:
                        try:
                            if page in ["self-portrait", "still life"]:
                                continue

                            p = wikipedia.page(page)
                            words = p.content.split()
                            num_occurances_painting = words.count('painting')

                            if num_occurances_painting > 2:
                                movement_dictionary = {i: 0 for i in movement}
                                p = wikipedia.page(page)
                                # INSERT WORD SEARCHING ALGORITHM HERE

                                artwork_collection.update({"_id": i["_id"]},
                                                          {"$set": {"movement": movement}})
                        except wikipedia.exceptions.PageError:
                            pass
                        except wikipedia.exceptions.DisambiguationError:
                            pass
                    last_title = i["title"]
                    print("-" * 100)
            except Exception as e:
                pass


    finally:
        title_file.write(last_title)
        title_file.close()

if __name__ == "__main__":
    artwork_collection, user_collection = connect_to_mongodb()
    download_images(artwork_collection.find({}))



