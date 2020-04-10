from tkinter import *

from pymongo import MongoClient
from PIL import ImageTk, Image
import requests
from io import BytesIO
import threading

ID = 123
images = ['en-SK-A-854', 'en-SK-A-3426', 'en-SK-C-87', 'en-SK-A-4160', 'en-SK-A-4254-9', 'en-SK-A-4524', 'en-SK-A-1474', 'en-SK-A-1023', 'en-SK-A-17', 'en-SK-A-2001', 'en-SK-A-2256', 'en-SK-A-2026', 'en-SK-A-5039', 'en-SK-A-419', 'en-SK-A-316', 'en-SK-A-917', 'en-SK-A-4262', 'en-SK-A-1338', 'en-SK-A-3074', 'en-SK-A-5', 'en-SK-A-1973', 'en-SK-A-4917', 'en-SK-A-1857', 'en-SK-A-1413', 'en-SK-A-4744', 'en-SK-C-1689', 'en-SK-C-1766', 'en-SK-A-2003', 'en-SK-A-659', 'en-SK-A-561', 'en-SK-A-1004', 'en-SK-A-2964', 'en-SK-C-466', 'en-SK-A-4467', 'en-SK-A-4588', 'en-SK-A-1747-A', 'en-SK-A-2468', 'en-SK-A-1755', 'en-SK-A-1937', 'en-SK-C-394', 'en-SK-A-3432', 'en-SK-A-2587-2', 'en-SK-A-1538', 'en-SK-A-1869', 'en-SK-A-691', 'en-SK-A-2139', 'en-SK-A-3017', 'en-SK-A-2365', 'en-SK-A-3529', 'en-SK-A-3919', 'en-SK-C-1673', 'en-SK-A-1470', 'en-SK-C-215', 'en-SK-A-865', 'en-SK-A-3378', 'en-SK-A-635', 'en-SK-A-257', 'en-SK-A-4493', 'en-SK-A-2995', 'en-SK-A-2059', 'en-SK-A-2957', 'en-SK-C-1659', 'en-SK-A-4149', 'en-SK-A-839', 'en-SK-A-3805', 'en-SK-A-4176', 'en-SK-A-2667', 'en-SK-A-1670', 'en-SK-A-581', 'en-SK-A-1102', 'en-SK-A-610', 'en-SK-C-1368', 'en-SK-C-1536', 'en-SK-A-2465', 'en-SK-A-1853', 'en-SK-A-4496', 'en-SK-A-1700', 'en-SK-A-3397', 'en-SK-A-2206', 'en-SK-A-1558', 'en-SK-A-3112', 'en-SK-A-5023', 'en-SK-A-274', 'en-SK-C-524', 'en-SK-A-3351', 'en-SK-A-3409', 'en-SK-A-4773', 'en-SK-C-1608', 'en-SK-A-4592', 'en-SK-A-3420', 'en-SK-A-396', 'en-SK-A-1838', 'en-SK-A-3515', 'en-SK-A-4831', 'en-SK-A-3078', 'en-SK-A-474', 'en-SK-A-1796', 'en-SK-A-1332', 'en-SK-A-639', 'en-SK-A-163']

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
    return list(collection.find({"id":{"$in":images}}))


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