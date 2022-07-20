import random
class Product:
    def __init__(self, id, name, price, category_id, description, discount, product_page, image_path): #creates a Product object with given values
        self.id = id
        self.name = name
        self.price = price
        self.category_id = category_id
        self.description = description
        self.discount = discount
        self.image_path = image_path
        self.product_page = product_page
    
    def getInfo(self):
        return f"[{self.id}] {self.name} ({self.image_path} - {self.product_page})"

class Category:
    def __init__(self, id, category, sub_category):
        self.id = id
        self.category = category
        self.sub_category = sub_category

def getPrice(price, discount = 0):
    newPrice = price * (1 - float(discount))
    pstrRounded = str(round(newPrice, 2))
    cents = False
    decimalCount = 0
    result = ""
    for i in range(len(pstrRounded)):
        if cents and pstrRounded[i] != ".":
            result += pstrRounded[i]
            decimalCount = decimalCount + 1
        elif pstrRounded[i] == ".":
            result += ","
            cents = True
        elif not cents:
            result += pstrRounded[i]
        else:
            break
    if decimalCount == 1:
        result += "0"
    cents = result[-2:]
    if cents == "00":
        result = result.replace(cents, "-", 1)
    return "€" + result