from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.models import Model
import numpy as np
from database_manual import selectProducts, selectallFromTable
import threading
from PIL import Image
import urllib.request
import os
import json

# See https://keras.io/api/applications/ for details

class FeatureExtractor:
    def __init__(self):
        base_model = VGG16(weights='imagenet')
        self.model = Model(inputs=base_model.input, outputs=base_model.get_layer('fc1').output)

    def extract(self, img):
        """
        Extract a deep feature from an input image
        Args:
            img: from PIL.Image.open(path) or tensorflow.keras.preprocessing.image.load_img(path)

        Returns:
            feature (np.ndarray): deep feature with the shape=(4096, )
        """
        img = img.resize((224, 224))  # VGG must take a 224x224 img as an input
        img = img.convert('RGB')  # Make sure img is color
        x = image.img_to_array(img)  # To np.array. Height x Width x Channel. dtype=float32
        x = np.expand_dims(x, axis=0)  # (H, W, C)->(1, H, W, C), where the first elem is the number of img
        x = preprocess_input(x)  # Subtracting avg values for each pixel
        feature = self.model.predict(x)[0]  # (1, 4096) -> (4096, )
        return feature / np.linalg.norm(feature)  # Normalize

class DbFeatures:
    def __init__(self, products = selectallFromTable("Products")):
        self.products = products
        self.lock = threading.Lock()
        self.features = []
        self.fe = FeatureExtractor()
        self.productCount = 0
    
    def getFeature(self, threadId = 0):
        with self.lock:
            while self.productCount < len(self.products):
                # get image from web
                product = self.products[self.productCount]
                urllib.request.urlretrieve(product.image_path, f"static/imageStorageTemp/product-result-{self.productCount}.png")

                feature = self.fe.extract(img = Image.open(os.path.abspath(f"static/imageStorageTemp/product-result-{self.productCount}.png")))
                self.productCount = self.productCount + 1
                self.features.append(feature)
                print("loading: ", product.id, " using thread no. ", threadId)
            
def parseJson(products, categories):
    # removes unwanted characters from json file values (like '/' in names)
    jsonObj = None
    with open('static/DbData.json', "r") as jsonFile:
        jsonObj = json.load(jsonFile)

        for pt in range(len(categories)):
            for p in range(len(jsonObj[categories[pt]["Category"]][categories[pt]["SubCategory"]])):
                parsedName = jsonObj[categories[pt]["Category"]][categories[pt]["SubCategory"]][p]["Name"].replace('/', ' ')
                parsedName = parsedName.replace('|', ' ')
                jsonObj[categories[pt]["Category"]][categories[pt]["SubCategory"]][p]["Name"] = parsedName
    with open('static/DbData.json', "w") as jsonFile:
        json.dump(jsonObj, jsonFile, indent=4)