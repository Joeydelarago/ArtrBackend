import requests
import os

from artr_utilities import connect_to_mongodb
from PIL import Image

images = ['en-SK-A-854', 'en-SK-A-3426', 'en-SK-C-87', 'en-SK-A-4160', 'en-SK-A-4254-9', 'en-SK-A-4524', 'en-SK-A-1474', 'en-SK-A-1023', 'en-SK-A-17', 'en-SK-A-2001', 'en-SK-A-2256', 'en-SK-A-2026', 'en-SK-A-5039', 'en-SK-A-419', 'en-SK-A-316', 'en-SK-A-917', 'en-SK-A-4262', 'en-SK-A-1338', 'en-SK-A-3074', 'en-SK-A-5', 'en-SK-A-1973', 'en-SK-A-4917', 'en-SK-A-1857', 'en-SK-A-1413', 'en-SK-A-4744', 'en-SK-C-1689', 'en-SK-C-1766', 'en-SK-A-2003', 'en-SK-A-659', 'en-SK-A-561', 'en-SK-A-1004', 'en-SK-A-2964', 'en-SK-C-466', 'en-SK-A-4467', 'en-SK-A-4588', 'en-SK-A-1747-A', 'en-SK-A-2468', 'en-SK-A-1755', 'en-SK-A-1937', 'en-SK-C-394', 'en-SK-A-3432', 'en-SK-A-2587-2', 'en-SK-A-1538', 'en-SK-A-1869', 'en-SK-A-691', 'en-SK-A-2139', 'en-SK-A-3017', 'en-SK-A-2365', 'en-SK-A-3529', 'en-SK-A-3919', 'en-SK-C-1673', 'en-SK-A-1470', 'en-SK-C-215', 'en-SK-A-865', 'en-SK-A-3378', 'en-SK-A-635', 'en-SK-A-257', 'en-SK-A-4493', 'en-SK-A-2995', 'en-SK-A-2059', 'en-SK-A-2957', 'en-SK-C-1659', 'en-SK-A-4149', 'en-SK-A-839', 'en-SK-A-3805', 'en-SK-A-4176', 'en-SK-A-2667', 'en-SK-A-1670', 'en-SK-A-581', 'en-SK-A-1102', 'en-SK-A-610', 'en-SK-C-1368', 'en-SK-C-1536', 'en-SK-A-2465', 'en-SK-A-1853', 'en-SK-A-4496', 'en-SK-A-1700', 'en-SK-A-3397', 'en-SK-A-2206', 'en-SK-A-1558', 'en-SK-A-3112', 'en-SK-A-5023', 'en-SK-A-274', 'en-SK-C-524', 'en-SK-A-3351', 'en-SK-A-3409', 'en-SK-A-4773', 'en-SK-C-1608', 'en-SK-A-4592', 'en-SK-A-3420', 'en-SK-A-396', 'en-SK-A-1838', 'en-SK-A-3515', 'en-SK-A-4831', 'en-SK-A-3078', 'en-SK-A-474', 'en-SK-A-1796', 'en-SK-A-1332', 'en-SK-A-639', 'en-SK-A-163']
path = "a_images/"
query = {"id": {"$in": images}}

def resume_from(title, works):
    for i in range(len(works)):
        if works[i]["title"] == title:
            print("%s artworks remaining" % (len(works) - i))
            return works[i:]
    print("'title' not found in list")
    return []


def crop_images():
    artwork_collection, user_collection = connect_to_mongodb()
    artworks = list(artwork_collection.find({}))
    check = True
    for i in artworks:
        try:
            if os.path.exists(path + i["id"] + ".jpg"):
                print(i["title"])
                im = Image.open(path + i["id"] + ".jpg")
                width, height = im.size

                if width > height:
                    crop_area = ((width-height)/2, 0, width - ((width-height)/2), height)
                    im = im.crop(crop_area)
                elif height > width:
                    crop_area = (0, (height-width)/2, width, height - ((height-width)/2))
                    im = im.crop(crop_area)

                if check:
                    im.show()
                    x = input("Continue?")

                if x.lower() == "y":
                    continue
                elif x == "1":
                    check = False

                im.save(path + i["id"] + ".jpg")
        except Exception as e:
            print(e)


def download_images():
    artwork_collection, user_collection = connect_to_mongodb()
    artworks = list(artwork_collection.find(query))
    # artworks = resume_from("Square Man", artworks)
    image_file = open("a_images/a_images.txt", "+w")
    count = 0
    for i in artworks:
        count += 1
        try:
            # skip if image is already downloaded
            if os.path.exists(path + i["id"] + ".jpg"):
                continue
            print(i["title"])
            location = path + str(count) + "_" + i["id"] + ".jpg"
            f = open(location, 'wb')
            f.write(requests.get(i['webImage']['url']).content)
            f.close()

            image_file.write(location)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    download_images()