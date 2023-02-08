import os
import socket
import struct
import multiprocessing
import logging
import array
import subprocess
import shlex
import json
import urllib.request
import pprint
import pyodbc
import hashlib 
import uuid
import requests

api_key = "fl36xkrepxj1ontpnikzitb3iwvv4d"
url     = "https://api.barcodelookup.com/v2/products?barcode={upc}&key=" + api_key


def upcLookup(upc,annotations=False):
    #===============================
    global url
    name                =''
    description         =''
    collection          =''
    productImageUrl     =''
    weight              =''
    error               =''
    manufacturer        =''
    manufacturer_number =''
    department          =''
    price               =''
    #===============================
    try: 
        #----------------------------------------------
        localUrl = url.format(upc=upc)

        with urllib.request.urlopen(localUrl) as localUrl:
            data = json.loads(localUrl.read().decode())
        #----------------------------------------------
        barcode = data["products"][0]["barcode_number"]
        #----------------------------------------------
        name = data["products"][0]["product_name"]
        name = name.replace(',', ' ')
        #----------------------------------------------
        description = data["products"][0]["description"]
        description = description.replace(',', '.')
        #----------------------------------------------
        categories = data["products"][0]["category"].split('>')
        collection = categories[len(categories)-1]
        #----------------------------------------------
        images = data["products"][0]["images"]
        if len(images) > 0:
            productImageUrl = images[0]
        #----------------------------------------------
        weight = data["products"][0]["weight"]
        #----------------------------------------------
        manufacturer = data["products"][0]["manufacturer"]
        manufacturer = manufacturer.replace(',', '')
        manufacturer_number = data["products"][0]["mpn"]
        #----------------------------------------------
        stores = data["products"][0]["stores"]
        if len(stores) > 0:
            price = stores[0]["store_price"]
        else:
            price = 0
        #----------------------------------------------
        categories = data["products"][0]["category"]
        department = getCategory(categories)
        #----------------------------------------------
        if annotations: 
            print (localUrl)
            print ("Barcode Number: ", barcode)
            print ("Product Name: ", name)
            print ("Product description: ", description)
            print ("Product Category: ", collection)
            print ("Product ImageUrl: ", productImageUrl)
            print ("Product weight: ", weight)
            print ("Product manufacturer: ", manufacturer)
            print ("Product manufacturer number: ", manufacturer_number)
            print ("Product price: ", price)
            print ("Product department: ", department)    
        #----------------------------------------------
    except Exception as e:
        print(f"Error for {upc} barcodeLookup:\t",e)
    #===============================
    barcode_results = {
        "name"                  :   name,
        "description"           :   description,
        "collection"            :   collection,
        "productImageUrl"       :   productImageUrl,
        "weight"                :   weight,
        "manufacturer"          :   manufacturer,
        "manufacturer_number"   :   manufacturer_number,
        "price"                 :   price,
        "department"            :   department,
        "error"                 :   error
        }
    #===============================
    return barcode_results


   
