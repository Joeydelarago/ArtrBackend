import numpy as np
import pymongo
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from pymongo import MongoClient
import numpy as np
import io
import pandas as pd
import PIL
from PIL import ImageTk, Image, ImageOps
import requests
from io import BytesIO
import threading

from tensorflow.keras.applications import VGG16
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dense

from tensorflow.keras.optimizers import RMSprop
from sklearn.model_selection import train_test_split, cross_val_score
import tensorflow
from scipy.spatial.distance import euclidean
from scipy import stats
from sklearn.cluster import AgglomerativeClustering

from artr_utilities import *

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.decomposition import PCA
from sklearn.decomposition import TruncatedSVD
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import SGDRegressor
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import KFold
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.model_selection import StratifiedKFold
from sklearn.dummy import DummyClassifier
from sklearn.dummy import DummyRegressor
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import SVR

def cross_val(df):
    numeric_features = ["yearEarly", "dissimilarity"]
    # nominal_features = ["techniques", "materials", "iconClass"]
    nominal_features = ["iconClass"]
    preprocessor = ColumnTransformer([("num", StandardScaler(), numeric_features),
                                      # ("nom", CountVectorizer(max_features=1500, analyzer='word', lowercase=False), "iconClass")
                                      ],remainder="drop")

    pipeline = Pipeline([("pre", preprocessor), ("est", LogisticRegression())])
    y = df["liked"].values
    print(np.mean(cross_val_score(pipeline, df, y, cv=10)))


def getArtworks(collection):
    return list(collection.find().limit(200).sort([("_id", pymongo.ASCENDING)]))

def train_transfer_learning_model():
    network = build_network()

    images = get_user_images()

    train_df, validate_df = train_test_split(images, test_size=.2, random_state=1)
    train_df, test_df = train_test_split(train_df, test_size=.25, random_state=1)
    train_df = train_df.reset_index(drop=True)
    test_df = test_df.reset_index(drop=True)
    validate_df = validate_df.reset_index(drop=True)

    print(test_df.shape[0] // 30)
    print(train_df.shape[0] // 30)
    print(train_df.shape, test_df.shape)

    train_datagen = ImageDataGenerator(
        rotation_range=15,
        zoom_range=0.2,
        # rescale=1. / 255,
        # shear_range=0.1,
        # width_shift_range=0.1,
        # height_shift_range=0.1,
        horizontal_flip = True
    )

    test_datagen = ImageDataGenerator(
        rotation_range=15,
        rescale=1. / 255,
        zoom_range=0.2,
        horizontal_flip=True,
    )

    train_generator = train_datagen.flow_from_dataframe(
        train_df,
        "images/",
        x_col='filename',
        y_col='liked',
        target_size=(224, 224),
        class_mode='categorical',
        batch_size=30
    )

    test_generator = test_datagen.flow_from_dataframe(
        test_df,
        "images/",
        x_col='filename',
        y_col='liked',
        target_size=(224, 224),
        class_mode='categorical'
    )

    history = network.fit_generator(
        train_generator,
        epochs=10,
        validation_data=test_generator,
        validation_steps=test_df.shape[0] // 30,
        steps_per_epoch=train_df.shape[0] // 30
    )

def find_clusters():
    X, titles = get_artwork_cnn_frame()
    print("Computing groups")
    clustering = AgglomerativeClustering(n_clusters=100).fit(X.copy(True))
    print("Converting groupings to list")

    groups = [{} for i in range(100)]
    print(len(groups))

    labels = clustering.labels_
    print("Count labels: " + str(len(labels)))
    for i in range(len(labels)):
        group = labels[i]
        title = titles[i]
        values = X.get(i)
        # print("Group: " + str(group))
        # print("Artwork: " + titles[i])
        groups[group][title] = values

    # print(len(titles))
    # print(len(labels))


    # flat_list = [item for sublist in titles for item in sublist]
    # titleset = set(flat_list)
    # print("Len of titles: " + str(len(titleset)))

    for group in groups:
        average_point = ave = [np.average(col) for col in zip(*list(group.values()))]

        distances = []
        for item in group.values():
            distances.append(euclidean(average_point, item))
        min_item = distances.index(min(distances))
        print(group.keys()[min_item])

def build_network():
    vgg16_base = VGG16(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
    network = Sequential()
    network.add(vgg16_base)
    vgg16_base.trainable = False
    network.add(Flatten())
    network.add(Dense(1024, activation="relu"))
    network.add(Dense(1024, activation="relu"))
    network.add(Flatten())
    network.add(Dense(2, activation="softmax"))
    network.compile(optimizer=RMSprop(lr=0.00003), loss="binary_crossentropy", metrics=["accuracy"])
    return network

if __name__ == '__main__':
    #train_transfer_learning_model()
    find_clusters()
