import matplotlib.pyplot as plt
import skimage
import numpy as np
import PIL.Image as Image
from pymongo import MongoClient

from skimage import feature
from skimage.exposure import exposure
from skimage.feature import greycomatrix, greycoprops
from sklearn import preprocessing
from skimage import data
from skimage.color import rgb2gray
from skimage import io



def testing():
    PATCH_SIZE = 512

    # open the camera image
    image_1 = io.imread('images/image.jpg', as_gray=True)
    image_1 = skimage.img_as_uint(image_1)

    image_2 = io.imread('images/image_2.jpg', as_gray=True)
    image_2 = skimage.img_as_uint(image_2)

    image_3 = io.imread('images/image_3.jpg', as_gray=True)
    image_3 = skimage.img_as_uint(image_3)

    image_4 = io.imread('images/image_4.jpg', as_gray=True)
    image_4 = skimage.img_as_uint(image_4)

    # image_3 = io.imread('image_4.jpg')
    # print(np.array(image_3).mean(axis=(0, 1)))

    images = [image_1, image_2, image_3, image_4]

    for i in range(len(images)):
        img = images[i]
        img_height, img_width = img.shape
        v_min, v_max = np.percentile(img, (0, 100))
        img = exposure.rescale_intensity(img, in_range=(0, v_max))
        img = img // (v_max // 255)
        img = img.astype(int)
        images[i] = img


    # #image requantisizng
    # v_min, v_max = np.percentile(image_1, (0, 100))
    # image_1 = exposure.rescale_intensity(image_1, in_range=(0, v_max))
    # image_1 = image_1 // (v_max // 255)
    # image_1 = image_1.astype(int)
    #
    # v_min, v_max = np.percentile(image_2, (0, 100))
    # image_2 = exposure.rescale_intensity(image_2, in_range=(0, v_max))
    # image_2 = image_2 // (v_max // 255)
    # image_2 = image_2.astype(int)
    # image_1 = preprocessing.MinMaxScaler(feature_range=(0, 255)).fit_transform(image_1).astype(int)
    # image_2 = preprocessing.MinMaxScaler(feature_range=(0, 255)).fit_transform(image_2).astype(int)

    # imgplot = plt.imshow(image_1)
    # plt.show()
    # print(image_1)


    dissimelarities = []
    correlations = []
    contrasts = []
    energies = []

    for img in images:
        glcm = greycomatrix(img, distances=[5], angles=[0], levels=300,
                            symmetric=True, normed=True)
        dissimelarities.append(greycoprops(glcm, 'dissimilarity')[0, 0])
        correlations.append(greycoprops(glcm, 'correlation')[0, 0])
        energies.append(greycoprops(glcm, 'energy')[0,0])
        contrasts.append(greycoprops(glcm, 'contrast')[0,0])

    print("Dissimelarity: %s \n Correlation: %s \n Energy: %s \n Contrast: %s" %(dissimelarities, correlations, energies, contrasts))
    fig = plt.figure(figsize=(8, 8))

    ax = fig.add_subplot(3, 2, 1)
    ax.imshow(image_1)
    bx = fig.add_subplot(3, 6, 1)
    bx.imshow(image_2)

    cx = fig.add_subplot(3, 9, 1)
    cx.imshow(image_3)

    ax.set_xlabel('Original Image')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('image')

    fig.suptitle('Grey level co-occurrence matrix features', fontsize=14, y=1.05)
    plt.tight_layout()
    plt.show()

def analyze_artwork(work) -> []:
    image = io.imread(work['webImage']['url'], as_gray=True)
    image = skimage.img_as_uint(image)

    v_min, v_max = np.percentile(image, (0, 100))
    image = exposure.rescale_intensity(image, in_range=(0, v_max))
    image = image // (v_max // 255)
    image = image.astype(int)


    glcm = greycomatrix(image, distances=[5], angles=[0], levels=500,
                        symmetric=True, normed=True)
    dissimelaritiy = greycoprops(glcm, 'dissimilarity')[0, 0]
    correlation = greycoprops(glcm, 'correlation')[0, 0]
    energy = greycoprops(glcm, 'energy')[0, 0]
    contrast = greycoprops(glcm, 'contrast')[0, 0]
    print("Title: %s" % work["title"])
    print([dissimelaritiy, contrast, energy, correlation])
    return [dissimelaritiy, contrast, energy, correlation]


def update_artworks(collection):
    works = artwork_collection.find({})
    # works = resume_from("Landscape with a Peddler and Woman Resting", list(works))
    # works = works[2:]
    for item in works:
        try:
            if 'dissimilarity' not in item.keys():
                gclm_values  = analyze_artwork(item)
                item['dissimilarity'] = gclm_values[0]
                item['contrast'] = gclm_values[1]
                item['energy'] = gclm_values[2]
                item['correlation'] = gclm_values[3]
                collection.update_one({'_id': item['_id']}, {"$set": item}, upsert=False)
        except Exception as e:
            print(e)



if __name__ == '__main__':
    client = MongoClient("mongodb://0.0.0.0:45536")
    db = client["artr"]
    artwork_collection = db["artworks"]
    user_collection = db["users"]
    old_user_collection = db["old_users"]
    print(db.command("dbstats"))
    update_artworks(artwork_collection)