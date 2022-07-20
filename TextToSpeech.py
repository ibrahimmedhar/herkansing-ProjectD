from hashlib import new
from gtts import gTTS
import os
from database_manual import selectallFromTable
import threading

def createTempProductMp3(prodDescription,name):
    language = 'en'
    mp3File = gTTS(text=prodDescription, lang=language, slow=False)
    mp3File.save("./static/mp3files/" + name + '.mp3')

class Mp3Gen:
    def __init__(self, ids):
        self.lock = threading.Lock()
        self.products = selectallFromTable("Products")
        self.ids = ids
        self.mp3Count = 0

    def generateMp3Threading(self, threadId):
        mp3 = None
        while self.mp3Count < len(self.ids):
            with self.lock:
                self.products[self.ids[self.mp3Count]].name
                if((self.products[self.ids[self.mp3Count]].name)+".mp3" not in "./static/mp3files"):
                    mp3 = self.products[self.ids[self.mp3Count]]
                    self.mp3Count = self.mp3Count + 1
            if(mp3 != None):
                print("generating mp3: Name = " + mp3.name + " with Thread no. " + str(threadId))
                createTempProductMp3(mp3.description, mp3.name)