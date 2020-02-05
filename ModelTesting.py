import numpy as np
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
from utilities import *

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
from sklearn.model_selection import cross_val_score
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

if __name__ == '__main__':
    artwork_collection, user_collection = connect_to_mongodb()
    users = list(user_collection.find({}))
    examples = []
    for u in users:
        for user_work in u["artworks"]:
            work = artwork_collection.find_one({"label.title": user_work})
            if work == None:
                continue
            i = dict(work)
            like = 1 if u['artworks'][user_work] == True else 0
            iconClass = ""
            if len(i['classification']['iconClassIdentifier']) > 1:
                iconClass = " ".join(i['classification']['iconClassIdentifier'])

            example = {'yearEarly': i['dating']['yearEarly'],
                       # 'techniques': i['techniques'],
                       # 'materials': i['materials'],
                       'iconClass': iconClass,
                       'dissimilarity': i.get('dissimilarity', 0),
                       'contrast': i.get('contrast', 0),
                       'energy': i.get('energy', 0),
                       'correlation': i.get('correlation', 0),
                       'userId' : u['user'],
                       'liked': like}
            examples.append(example)
        # user_artworks = {**user_artworks, **i["artworks"]}

        print(len(u["artworks"]))
        # print(u["artworks"])

    df = pd.DataFrame(examples)
    cross_val(df)

    # print(user_artworks)
    # for i in range(0):
    #     print(i)
    # print(len(list(user_artworks)))
    # print(db.command("dbstats "))
    # print(db.command("collstats", "users"))