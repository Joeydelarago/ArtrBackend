from tkinter import *

import pymongo
from pymongo import MongoClient
import numpy as np
import io
import pandas as pd
import PIL
from PIL import ImageTk, Image, ImageOps
import requests
from io import BytesIO
import threading

ID = 696969
class BasicGUI:
    loaded_images = []
    loaded_artworks = []
    def __init__(self, artworks, master):
        self.artworks = artworks
        self.master = master
        master.title("Testing gui")
        self.canvas = Canvas(master, width=1500, height=1000)
        self.canvas.pack()

        self.load_artworks()
        self.update_image()

        master.bind("<KeyRelease>", self.key_up)

    def key_up(self, e):
        if e.char == "y" or e.char == "n":
            user_data = user_collection.find_one({'user': ID})
            work = self.loaded_artworks.pop()
            if user_data is None:
                user_collection.insert({"user": ID, "artworks": {}})

            liked = True if e.char == "y" else False
            user_collection.update({"user": ID}, {"$set": {"artworks.%s" % work["title"]: liked}})

            self.update_image()

    def update_image(self):
        img = Image.open(BytesIO(self.loaded_images.pop()))
        img.thumbnail((1500, 1000), Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(img)
        self.canvas.create_image(20, 20, anchor=NW, image=self.img)
        self.canvas.image = self.img
        if len(self.loaded_artworks) < 7:
            download_thread = threading.Thread(target=self.load_artworks)
            download_thread.start()

    def load_artworks(self):
        for i in range(10):
            work = self.artworks.pop()
            response = requests.get(work['webImage']['url'])
            self.loaded_images.insert(0, response.content)
            self.loaded_artworks.insert(0,  work)

def getArtworks(collection):
    return list(collection.find().limit(200).sort([("_id", pymongo.ASCENDING)]))


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
                   'correlation': i['correlation']}
        artworks.append(artwork)

    return pd.DataFrame(artworks)


if __name__ == '__main__':
    client = MongoClient("mongodb://0.0.0.0:45536")
    db = client["artr"]
    artwork_collection = db["artworks"]
    user_collection = db["users"]
    old_user_collection = db["old_users"]
    print(db.command("dbstats"))
    root = Tk()
    my_gui = BasicGUI(getArtworks(artwork_collection), root)
    root.mainloop()