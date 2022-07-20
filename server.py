import numpy as np
import os
from os.path import exists
import json
import sys
import threading
from PIL import Image
import shutil
from feature_extractor import FeatureExtractor, parseJson
from datetime import datetime
from flask import Flask, request, render_template, url_for, session
from pathlib import Path
from database_manual import selectProducts, selectallFromTable
from time import perf_counter
from DbClasses import getPrice
from TextToSpeech import createTempProductMp3, Mp3Gen
import string
import random

app = Flask(__name__)

#session data encryptionkey
app.secret_key = ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(8))

# Read image features
fe = FeatureExtractor()

# grab features from static/featureStorage.npy
with open('static/featureStorage.npy', 'rb') as fs:
    features = np.load(fs)

# get products from DB
Products = selectallFromTable("Products")

@app.route('/', methods=['GET', 'POST',])
def index():
    if os.path.exists('static/declare.json'):
            os.remove('static/declare.json')
    if request.method == 'POST':
        # removes directory 'static/uploaded' & file contained inside
        # uploaded contains the last-uploaded image by user
        shutil.rmtree('static/uploaded')
        os.mkdir('static/uploaded')
        if(exists('static/mp3files')):   
            shutil.rmtree('static/mp3files')
        

        
        
        os.mkdir('static/mp3files')

        file = request.files['query_img']

        noPictureSelected = 'Geen bestand geselecteerd.'

        if file.filename == '':
            return render_template('index.html', noPictureSelected=noPictureSelected)

        # Save query image
        img = Image.open(file.stream)  # PIL image
        uploaded_img_path = "static/uploaded/" + datetime.now().isoformat().replace(":", ".") + "_" + file.filename
        img.save(uploaded_img_path)
        
        if len(Products) == 0:
            return render_template('index.html',
                               query_path=uploaded_img_path,
                               scores= 1) 

        # Run search
        query = fe.extract(img)
        dists = np.linalg.norm(features-query, axis=1)  # L2 distances to features
        ids = np.argsort(dists)[:90]  # Top 30 results

        mp3ThreadClass = Mp3Gen(ids)
        mp3Threads = list()

        start_time = perf_counter()

        for i in range(4):
            x = threading.Thread(target=mp3ThreadClass.generateMp3Threading, args=(i,))
            mp3Threads.append(x)
            x.start()
        # for y in mp3Threads:
        #     y.join()

        end_time = perf_counter()
        print("Total time mp3 gen: ", end_time - start_time)

        # establish scores to pass to HTML
        fullLoad = [(
            Products[id].image_path, 
            Products[id].name, 
            getPrice(Products[id].price, Products[id].discount), 
            f"./static/mp3files/{Products[id].name}.mp3", 
            Products[id].product_page) 
            for id in ids]

        jsondata = {}
        otherdata = []    
        jsoncount=0

        for id in ids:
            key = "product" + str(jsoncount)
            item = key={"img":Products[id].image_path, "name":Products[id].name,"price":getPrice(Products[id].price, Products[id].discount),"mp3":f"./static/mp3files/{Products[id].name}.mp3","page":Products[id].product_page}
            jsoncount = jsoncount+1
            otherdata.append(item)

        jsondata = json.dumps(otherdata)

        with open('./static/declare.json','w') as j:
            j.write(jsondata)



        return render_template('index.html',
                               query_path=uploaded_img_path,
                               scores= fullLoad[:9], fullLoad=jsondata) 

    else:
        return render_template('index.html')

if __name__=="__main__":
    app.run("0.0.0.0")
