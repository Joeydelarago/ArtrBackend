import pymongo
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications import VGG16
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.applications.vgg16 import decode_predictions
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import RMSprop

from artr_utilities import connect_to_mongodb


def get_image_features(collection):
    works = collection.find({})


    count = 0
    vgg16_model = VGG16()
    model = Sequential()
    print(vgg16_model.summary())
    for layer in vgg16_model.layers[:-2]:
        print(layer)
        model.add(layer)

    for work in works:
        count += 1
        if count < 2700:
            continue
        image_array = img_to_array(load_img("images/" + work["id"] + ".jpg", target_size=(224, 224)))
        image_tensor_1 = image_array.reshape(
            (1, image_array.shape[0], image_array.shape[1], image_array.shape[2]))
        image_tensor_1 = preprocess_input(image_tensor_1)

        f = list(model.predict(image_tensor_1)[0])
        for i in range(len(f)):
            f[i] = float(f[i])

        collection.update({"_id": work["_id"]}, {"$set": {"cnn_features": f}})
        print(work['title'])
        print("%f" % (count / 4247))

def remove_cnn_features(collection):
    for work in collection.find({}):
        collection.update({"_id": work["_id"]}, {"$set": {"cnn_features": {}}})
if __name__ == "__main__":
    artwork_collection, user_collection = connect_to_mongodb()
    get_image_features(artwork_collection)
    # remove_cnn_features(artwork_collection)