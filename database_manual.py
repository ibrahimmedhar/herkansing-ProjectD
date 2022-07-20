import sqlite3
import os
import json
from DbClasses import Product, Category, getPrice
import random
from sqlite3 import Error
import feature_extractor
import requests
import offline as of
#weet niet zeker of sqlite via pip moet gebeuren (bij mij niet). zoja, toevoegen bij requirements.txt
listImgNames=[]
image_formats = ["image/png","image/jpg","image/jpeg"]

def create_connection(db_file):
    #create a database connection to a SQLite database, creates the file if it doesn't exist
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn

def createProducttable():
    with create_connection("database.db") as db: #way to run queries to the database
        cur = db.cursor()
        cur.execute(""" CREATE TABLE IF NOT EXISTS Products (
            id integer PRIMARY KEY AUTOINCREMENT, 
            name text NOT NULL UNIQUE, 
            price real NOT NULL,
            category_id integer NOT NULL,
            description text NOT NULL,
            discount real NOT NULL,
            product_page text NOT NULL,
            image_path text NOT NULL,
            FOREIGN KEY(category_id) REFERENCES Categories(id)
            ); """)

def createCategorytable():
    with create_connection("database.db") as db:
        cur = db.cursor()
        cur.execute(""" CREATE TABLE IF NOT EXISTS Categories (
            id integer PRIMARY KEY AUTOINCREMENT,
            category text NOT NULL,
            sub_category text NOT NULL UNIQUE
            ); """)

def createTesttable():
    with create_connection("testdatabase.db") as db: #way to run queries to the database
        cur = db.cursor()
        cur.execute(""" CREATE TABLE IF NOT EXISTS Testtable (
            id integer PRIMARY KEY AUTOINCREMENT, 
            image_path text NOT NULL
            ); """)

def selectallFromTesttable():
    with create_connection("testdatabase.db") as db:
        cur = db.cursor()
        return cur.execute(f"""SELECT * FROM Testtable""").fetchall()

def insertintoTetstable(image_path):
    with create_connection("testdatabase.db") as db:
        cur = db.cursor()
        cur.execute("""INSERT INTO Testtable (image_path) VALUES(?);""",(image_path))

def insertintoProductstable(name, price, category_id, description, discount, product_page, image_path):
    with create_connection("database.db") as db:
        cur = db.cursor()
        cur.execute(""" INSERT INTO Products (name, price, category_id, description, discount, product_page, image_path) 
            VALUES(?,?,?,?,?,?,?);""",(name, price, category_id, description, discount, product_page, image_path)) #id is autoincrement, so doesn't need to be defined

def insertintoCategorytable(category, sub_category):
    with create_connection("database.db") as db:
        cur = db.cursor()
        cur.execute(""" INSERT INTO Categories (category, sub_category) 
            VALUES(?,?);""",(category, sub_category))

def selectallFromTable(table_name):
    with create_connection("database.db") as db:
        cur = db.cursor()
        # query = f"""SELECT * FROM {table_name}"""
        cur.execute(f"""SELECT * FROM {table_name}""")
        rows = cur.fetchall()
        for i in range(len(rows)):
            if(table_name == "Products"):
                rows[i] = Product(*rows[i])
            elif(table_name == "Categories"):
                rows[i] = Category(*rows[i])
        return rows

# Selecteert producten uit db, die dezelfde naam hebben als de top30 vergeleken afbeeldingen
def selectProducts(names):
    listProductDetails=[]
    with create_connection("database.db") as db:
        cur = db.cursor()
        for n in names:
            cur.execute("SELECT * from Products WHERE name=(?);",(os.path.splitext(n)[0],))
            rows = cur.fetchall()
            if rows == []:
                continue
            else:
                listProductDetails.append(rows)
    removeNestedList = [v for sublist in listProductDetails for v in sublist]
    return removeNestedList

# Makes a list of images in dir
def getProductsJSON():
    productList = []
    a = open('static/DbData.json', "r")
    jsonObj = json.loads(a.read())
    for i in jsonObj:
        for j in jsonObj[i]:
            productList.append(jsonObj[i][j])
    a.close()
    return productList

def getCategoriesJSON():
    categoryList = []
    a = open('static/DbData.json', "r")
    jsonObj = json.loads(a.read())
    for i in jsonObj:
        for j in jsonObj[i]:
            categoryList.append({'Category': i, 'SubCategory': j})
    a.close()
    return categoryList

# Alle relevante informatie staat in de DbData.json file
# En dan bij de cursors.execute even de juiste categorie in parameters plaatsen.
def insertProductTable():
    productArr = getProductsJSON()
    categoryArr = getCategoriesJSON()

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    for pt in range(len(categoryArr)):
        for p in productArr[pt]:
            image_path = p["ImagePath"]
            r = requests.head(image_path)
            if r.headers["content-type"] in image_formats:
                name = p["Name"]
                price = p["Price"]
                discount = p["Discount"]
                discountPrice = getPrice(price, discount)
                product_page = p["ProductPage"]
                description = "The product name is: " + name + ". The price is € " + discountPrice + ". The category is: " + categoryArr[pt]["Category"] + " of sub category " + categoryArr[pt]["SubCategory"]
                cursor.execute("""INSERT OR IGNORE INTO Products (name, price, category_id, description, discount, product_page, image_path) VALUES(?,?,?,?,?,?,?)""", (name, price, pt + 1, description, discount, product_page, image_path))
            else:
                print("{image_path} does not reference a valid image. The product was not added to the database.")
    conn.commit()
    cursor.close()
    conn.close()

def insertCategoryTable():
    categories = getCategoriesJSON()
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    for c in categories:
        cursor.execute("""INSERT OR IGNORE INTO Categories (category, sub_category) VALUES(?,?)""", (c["Category"], c["SubCategory"]))
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == '__main__':
    with create_connection("database.db") as db: #uncomment to drop table
        c = db.cursor()
        c.execute("""DROP TABLE Products;""")
        c.execute("""DROP TABLE Categories""")
    createProducttable()
    createCategorytable()
    feature_extractor.parseJson(getProductsJSON(), getCategoriesJSON())
    insertCategoryTable()
    insertProductTable()
    of.OfflineAlg()