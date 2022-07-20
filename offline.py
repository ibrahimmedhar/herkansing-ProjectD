from unicodedata import category
from PIL import Image
import feature_extractor as fe
import database_manual as db
from time import perf_counter
from pathlib import Path
import numpy as np
import threading
import shutil
import os
import json

def OfflineAlg():
    featureClass = fe.DbFeatures()
    featureThreads = list()
    try:
        shutil.rmtree('static/imageStorageTemp')
    except:
        print("directory was already removed, continuing w execution")
    try:
        os.mkdir('static/imageStorageTemp')
    except:
        print("directory was already created, continuing w execution")
    
    products = db.getProductsJSON()
    categories = db.getCategoriesJSON()
    fe.parseJson(products, categories)

    start_time = perf_counter()
    for i in range(5):
        x = threading.Thread(target=featureClass.getFeature, args=(i,))
        featureThreads.append(x)
        x.start()
    for y in featureThreads:
        y.join()
    end_time = perf_counter()
    print("Total time:", end_time - start_time, "Seconds.")
    featureClass.features = np.array(featureClass.features)

    with open('static/featureStorage.npy', 'wb+') as fs:
        np.save(fs, featureClass.features)
    
    shutil.rmtree('static/imageStorageTemp')