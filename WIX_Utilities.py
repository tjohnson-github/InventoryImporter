
import requests
import logging as logger
import WIX_Json
#import Formatting_Utilities
import File_Operations
#import Wix_Utilities
#from Logging_Utilities import progressBar
import dearpygui.dearpygui as dpg
import time
import Gspread_Rubric

#=================================================================================
#       JSON FORMATTING FUNCTIONS
#=================================================================================
from typing import Optional, Any, List, TypeVar, Callable, Type, cast
from uuid import UUID
from datetime import datetime
import dateutil.parser


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_int(x: Any) -> int:
    assert isinstance(x, int)
    return x


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x

def from_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def is_type(t: Type[T], x: Any) -> T:
    assert isinstance(x, t)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()

#=================================================================================
#       PRODUCT CLASSES
#=================================================================================

class Discount:
    type: str #
    value: str #

    def __init__(self, type: str, value: str) -> None:
        self.type = type
        self.value = value

    def to_dict(self) -> dict:
        result: dict = {}
        result["type"] = from_str(self.type)
        result["value"] = from_int(self.value)
        return result

class PricePerUnitData:
    total_quantity: int #
    total_measurement_unit: str #
    base_quantity: int #
    base_measurement_unit: str #

    def __init__(self, total_quantity: int, total_measurement_unit: str, base_quantity: int, base_measurement_unit: str) -> None:
        self.total_quantity = total_quantity
        self.total_measurement_unit = total_measurement_unit
        self.base_quantity = base_quantity
        self.base_measurement_unit = base_measurement_unit


class Choice:
    # each option can hold 1-30 choices
    value: str #
    description: str #

    def __init__(self, value: str, description: str) -> None:
        self.value = value
        self.description = description

    def to_dict(self) -> dict:
        result: dict = {}
        result["value"] = from_str(self.value)
        result["description"] = from_str(self.description)
        return result

#---------------------------  
class ProductOptionKey:
    name : str
    choices: Optional[List[Choice]]

    def __init__(self, name, choices: Optional[List[Choice]]) -> None:
        self.name = name
        self.choices = choices

    def to_dict(self) -> dict:
        result: dict = {}
        #=====================================
        result["name"]              = from_str(self.name)
        result["choices"] = from_list(lambda x: to_class(Choice, x), self.choices)
        #=====================================
        return result

class Size(ProductOptionKey):
    def __init__(self, choices: Optional[List[Choice]]):
        super(Size, self).__init__(choices)

class Weight(ProductOptionKey):
    def __init__(self, choices: Optional[List[Choice]]):
        super(Weight, self).__init__(choices)
    
class Color(ProductOptionKey):
    def __init__(self, choices: Optional[List[Choice]]):
        super(Color, self).__init__(choices)

class ProductOptions:
    weight: Optional[Weight]
    size: Optional[Size]
    color: Optional[Color]

    def __init__(self, weight: Optional[Weight],size: Optional[Size],color: Optional[Color]) -> None:
        self.weight = weight
        self.size = size
        self.color = color

#---------------------------  

class Props:
    name: Optional[str]
    content: Optional[str]

    def __init__(self, name: Optional[str], content: Optional[str]) -> None:
        self.name = name
        self.content = content


class Tag:
    type: str #
    # Supported types = ["title","meta","script","link"]
    children: str #
    custom: bool #
    disabled: bool #
    props: Props

    def __init__(self, type: str, children: str, custom: bool, disabled: bool, props: Props) -> None:
        self.type = type
        self.children = children
        self.custom = custom
        self.disabled = disabled
        self.props = props


class SEOData:
    tags: List[Tag]

    def __init__(self, tags: List[Tag]) -> None:
        self.tags = tags



class FlattenedNewWixProduct:

    #handleId	    fieldType	name	                            description	                        productImageUrl	                                
    #063713359032	Product	    Orn-AB Sweater Animal 3.5inH Asst	Orn-AB Sweater Animal 3.5inH Asst	https://static.wixstatic.com/media/dcbbe3_ff87e80e30c6447fae4caa80f591f492~mv2.jpg	

    #collection	                                                                sku	            ribbon	price	    surcharge	visible	   
    #Seasonal Gifts;Abbott Ornaments;Christmas Ornaments;Animals;All Products	063713359032		    17.99		            TRUE	    

    #discountMode	discountValue	inventory	weight
    #PERCENT	    0	            24	        5

    name: str #
    description: Optional[str] #
    price: float #
    #price_per_unit_data: Optional[PricePerUnitData] #
    sku: Optional[str] #
    visible: Optional[bool] #
    #discount: Optional[Discount] #
    discount_type: str
    discount_value: str
    #product_options: Optional[ProductOptions] #
    manage_variants: Optional[bool] #
    product_type = "physical"
    weight: Optional[int] #
    ribbon: Optional[str] #
    #seo_data: Optional[SEOData]
    
    #def __init__(self, name: str, description: Optional[str], price: int, price_per_unit_data: Optional[PricePerUnitData], sku: Optional[str], visible: Optional[bool], discount: Optional[Discount], product_options: Optional[ProductOptions], manage_variants: Optional[bool], product_type: Optional[str], weight: Optional[int], ribbon: Optional[str], seo_data: Optional[SEOData]) -> None:

    def __init__(self, name: str, description: Optional[str], price: float, sku: Optional[str], visible: Optional[bool],discount_value: str, discount_type: str, manage_variants: Optional[bool], weight: Optional[int], ribbon: Optional[str]) -> None:#,product_options: Optional[ProductOptions]) -> None:
        self.name = name
        self.description = description
        self.price = price
        #self.price_per_unit_data = price_per_unit_data
        self.sku = sku
        self.visible = visible
        #self.discount = discount
        self.discount_type = discount_type
        self.discount_value = discount_value

        #self.product_options = product_options
        self.manage_variants = manage_variants
        #self.product_type = product_type
        self.weight = weight
        self.ribbon = ribbon
        #self.seo_data = seo_data

    def to_dict(self) -> dict:
        result: dict = {}
        #=====================================
        result["name"]              = from_str(self.name)
        result["description"]       = from_union([from_str, from_none], self.description)
        result["price"]             = from_float(self.price)
        # price per unit data
        result["sku"]               = from_str(str(self.sku))
        #result["sku"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.sku)
        result["visible"]           = from_union([from_bool, from_none], self.visible)
        
        #result["discount"]          = to_class(Discount, self.discount)
        #result["discount"]          = self.discount.to_dict()
        result["discount_type"]      = from_str(self.discount_type)
        result["discount_value"]     = from_str(self.discount_value)

        #result["discount"] = from_union([lambda x: to_class(Discount, x), from_none], self.discount)
        #result["product_options"]   = to_class(ProductOptionKey, self.product_options)
        result["manage_variants"]   = from_union([from_bool, from_none], self.manage_variants)
        result["product_type"]      = from_str(self.product_type)
        result["weight"]            = from_union([from_int, from_none], self.weight)
        result["ribbon"]            = from_union([from_str, from_none], self.ribbon)
        # SEO data
        #=====================================
        return result

#=================================================================================
#       HTTPS FUNCTIONS
#=================================================================================

def get_all_collections():
    #=============
    resp = None
    #=============
    try:
        #---------------------------------
        for x in product_as_dict:
            print (x,":",product_as_dict[x])
        print ("================================")
        msg = product_as_dict
        #---------------------------------
        if use_get:    
            #---------------------------------
            url =   "https://johnsonsflorists.com/_functions/CreateProductFlattened?"
            print (url)
            resp = requests.get(url,msg)

            #{"query":{"name":"Test Product D",
            #"description":"Not a real product; for internal testing. Thank you for your patience.",
            #"price":"6","sku":"1234567","visible":"True","discount":["type","value"],"manage_variants":"True","weight":"5"}

            #---------------------------------
        else:
            #---------------------------------
            # POST NOT IMPLEMENTED
            pass
            #---------------------------------
        #print (resp.text)
        #---------------------------------
        if resp.status_code!=200:
            logger.error("REST API Error {0}".format(resp))
            logger.error(" Url: {0}".format(url))
            logger.error(" Json: {0}".format(msg))
        #---------------------------------
    except Exception as e:
        logger.info("\n***************   Error *********\n")
        logger.info(e)
    return resp

def get_collection(response):
    #=========================
    '''
    {"products":[
        {
            "inStock":true,
            "weight":5,
            "name":"RIVER GRAVEL 2 QT",
            "sku":"071605142020",
            "formattedDiscountedPrice":"$12.99",
            "productOptions":{},
            "mainMedia":"wix:image://v1/dcbbe3_4eb5d182a7a94851ad9996110445f38c~mv2.jpg/file.jpg#originWidth=450&originHeight=375",
            "description":"Marble Maze River Gravel is a natural river stone. Yellowish/tan color. Multiple uses indoor and outdoor.",
            "_id":"07ea39a8-83ec-459f-a783-e2f2ac054242",
            "discountedPrice":12.99,
            "link-products-slug":"/products/river-gravel-2-qt",
            "formattedPrice":"$12.99",
            "price":12.99,
            "quantityInStock":12,
            "inventoryItem":"f815c657-7c13-ba60-587c-1d0d53fabdbd",
            "_updatedDate":"2023-02-01T19:57:51.954Z",
            "slug":"river-gravel-2-qt",
            "productType":"physical",
            "ribbons":[],
            "mediaItems":[
                {
                    "description":"",
                    "id":"dcbbe3_4eb5d182a7a94851ad9996110445f38c~mv2.jpg",
                    "src":"wix:image://v1/dcbbe3_4eb5d182a7a94851ad9996110445f38c~mv2.jpg/file.jpg#originWidth=450&originHeight=375",
                    "title":"","type":"Image"
                }
             ],
             "trackInventory":true,
             "customTextFields":[],
             "ribbon":"",
             "currency":"USD",
             "productPageUrl":"/product-page/river-gravel-2-qt",
             "manageVariants":false,
             "discount":{
                "type":"NONE",
                "value":0
              },
              "additionalInfoSections":[],
              "variants":[
                    {
                        "_id":"00000000-0000-0000-0000-000000000000"
                        ,"choices":{},
                        "variant":{
                            "weight":5,
                            "sku":"071605142020",
                            "formattedDiscountedPrice":"$12.99",
                            "visible":true,
                            "discountedPrice":12.99,
                            "formattedPrice":"$12.99",
                            "price":12.99,
                            "currency":"USD"
                         }
                     }
                 ],
                "createdDate":"2021-01-22T19:44:05.181Z"}]}


    '''


    #===========================
    # https://support.wix.com/en/article/velo-wix-stores-products-collection-fields#collections-collections
    # https://www.wix.com/velo/forum/feature-requests/products-reference-to-collections
    # https://www.wix.com/velo/forum/coding-with-velo/return-all-items-in-the-wix-store-database-based-on-their-collections
    #===========================
    if response.status_code == 200:

        response_obj = response.json()['products']

        if response_obj == 'No product':
            return ''

        if len(response_obj)>1:
            # Ensures we only look at first product returned
            response_obj=response_obj[0]
        else:
            response_obj=response_obj[0]


        try:
            product = WIX_Json.Products.from_dict(response_obj)
            if product.collections == []:
                return ''
            unformatted_collections = product.collections
        except Exception as e:
            print(f"Error with getting URL {e}")
            unformatted_collections = ""
        #===========================
        try: 
            formatted_collections=''
            first_entry=True
            for items in unformatted_collections:

                collection      = items.name

                if first_entry:
                    formatted_collections+=collection
                    first_entry=False
                else:
                    formatted_collections+=";"+collection

        except Exception as e:
            print (e)
            formatted_collections = ''
        #===========================
        return formatted_collections
    else: 
        print ("Can't find COLLECTION from this kind of response: ",response)
        return ''

def get_PID(response):
    # If you feed in a general response from ____, this will select the first PID out of it
    #===========================
    if response.status_code == 200:

        response_obj = response.json()['products']

        if response_obj == 'No product':
            return ''


        ## VVV test this: can remove??
        if len(response_obj)>1:
            # Ensures we only look at first product returned
            response_obj=response_obj[0]
        else:
            response_obj=response_obj[0]


        print("-----start-------")
        for x in response_obj:
            print(x)
        print("------end------")
        try:
            product = WIX_Json.Products.from_dict(response_obj)
            PID = product.id

        except:
            PID=response_obj["_id"]


        return PID
        #===========================
    else: 
        print ("Can't find PID from this kind of response: ",response)
        return ''

def get_url(response):
    # If you feed in a general response from ____, this will select the first image URL out of it
    #===========================
    if response.status_code == 200:

        #print (response.json())

        response_obj = response.json()['products']

        #print (type(response_obj))
        #print(response_obj)
        #print(len(response_obj))

        if response_obj == 'No product':
            return ''



        if len(response_obj)>1:
            # Ensures we only look at first product returned
            response_obj=response_obj[0]
        else:
            response_obj=response_obj[0]

        print("-----start-------")
        for x in response_obj:
            print(x)
        print("------end------")


        try:
            product = WIX_Json.Products.from_dict(response_obj)
            unformatted_mainMedia = product.main_media
        except Exception as e:
            print(f"Product object not formatted correctly; trying from dict:\t{e}")

            unformatted_mainMedia=response_obj["mainMedia"]
        #===========================
        try:
            # https://www.wix.com/velo/forum/coding-with-velo/how-to-get-image-url-from-its-path-in-media-manager
            temp_list = unformatted_mainMedia.split("/");
            """
                Example temp_list: 
                    0 wix:image:
                    1 
                    2 v1
              -->   3 dcbbe3_684e8be313464fd181769fb29b757be9~mv2.jpg   <--
                    4 file.jpg#originWidth=900&originHeight=900
            """
            formatted_url = "https://static.wixstatic.com/media/"+temp_list[3]
            print ("\t\t\t",formatted_url)
        except Exception as e:
            print (f"Error with grabbing URL:\t{e}")
            formatted_url = ''
        #===========================
        return formatted_url
    else: 
        print ("Can't find URL from this kind of response: ",response)
        return ''

def get_product(sku):
    #=============
    resp = None
    #=============
    try:
        #---------------------------------
        msg={'sku':str(sku)}
        #---------------------------------
        #---------------------------------
        url = "https://johnsonsflorists.com/_functions/GetProductTest/ProductId?"
        resp = requests.get(url,msg)
        #---------------------------------
        #---------------------------------
        if resp.status_code!=200:
            print("--------------------- BAD:\t",sku)
            print(resp.text)

            #logger.error("REST API Error {0}".format(resp))
            #logger.error(" Url: {0}".format(url))
            #logger.error(" Json: {0}".format(msg))
        else:
            print("--------------------- GOOD:\t",sku)
            #print(resp.text)
        #---------------------------------
    except Exception as e:
        print(f'--------------------- ERROR:\t_{sku}_\t{e}')
        logger.info("\n***************   Error *********\n")
        logger.info(e)
    return resp

#=================================================================================
#       HTTPS PRODUCT CREATION/UPDATE
#=================================================================================

def updateProduct(product_as_dict,use_get=True):
    #=============
    resp = None
    #=============
    try:
        #---------------------------------
        for x in product_as_dict:
            print (x,":",product_as_dict[x])
        print ("================================")
        msg = product_as_dict
        #---------------------------------
        if use_get:     #get:
            #---------------------------------

            #if flat:
            url =   "https://johnsonsflorists.com/_functions/UpdateProductFieldsFlattened?"
                #url =   "https://johnsonsflorists.com/_functions/UpdateProductFieldsFlattened?"
            #else:
            #    url =   "https://johnsonsflorists.com/_functions/UpdateProductFieldsTEST?"

            #url = "https://johnsonsflorists.com/_functions/UpdateProduct/ProductId?"
            resp = requests.get(url,msg)
            #---------------------------------
        else:       #post:
            #---------------------------------
            url = "https://johnsonsflorists.com/_functions/UpdateProduct/"

            import json
            from requests.structures import CaseInsensitiveDict

            headerArg = CaseInsensitiveDict()
            headerArg["Accept"] = "application/json"
            headerArg["Content-Type"] = "application/json"
            headerArg["Accept-encoding"] = "application/json"


            dataArg = json.dumps(msg)

            resp = requests.post(url,data=dataArg,headers=headerArg)
            #---------------------------------
            #import urllib3
            #import certifi
            #http = urllib3.PoolManager(ca_certs=certifi.where())

            #headers["Accept-encoding"] = "application/json"


            #resp = http.request('POST', url, data=msg)
            #resp = requests.post(url,data=msg)
            #print (resp.text)

            #resp = http.request('POST', url, data=json.dumps(msg))
            #resp = requests.post(url,headers=headers,json=msg)
            #---------------------------------
        print (resp.text)
        #---------------------------------
        if resp.status_code!=200:
            logger.error("REST API Error {0}".format(resp))
            logger.error(" Url: {0}".format(url))
            logger.error(" Json: {0}".format(msg))
        #---------------------------------
    except Exception as e:
        logger.info("\n***************   Error *********\n")
        logger.info(e)
    return resp

def createProduct(product_as_dict,use_get=True, flat=False):
    #=============
    resp = None
    #=============
    try:
        #---------------------------------
        for x in product_as_dict:
            print (x,":",product_as_dict[x])
        print ("================================")
        msg = product_as_dict
        #---------------------------------
        if use_get:     #get:
            #---------------------------------
            url =   "https://johnsonsflorists.com/_functions/CreateProductFlattened?"
            #url =   "https://johnsonsflorists.com/_functions/CreateProductTEST?"
            #url = "https://johnsonsflorists.com/_functions/UpdateProduct/ProductId?"
            #resp = ""
            print (url)
            resp = requests.get(url,msg)

            #{"query":{"name":"Test Product D",
            #"description":"Not a real product; for internal testing. Thank you for your patience.",
            #"price":"6","sku":"1234567","visible":"True","discount":["type","value"],"manage_variants":"True","weight":"5"}

            #---------------------------------
        else:       #post:
            #---------------------------------
            url = "https://johnsonsflorists.com/_functions/UpdateProduct/"

            import json
            from requests.structures import CaseInsensitiveDict

            headerArg = CaseInsensitiveDict()
            headerArg["Accept"] = "application/json"
            headerArg["Content-Type"] = "application/json"
            headerArg["Accept-encoding"] = "application/json"


            dataArg = json.dumps(msg)

            resp = requests.post(url,data=dataArg,headers=headerArg)
            #---------------------------------
            #import urllib3
            #import certifi
            #http = urllib3.PoolManager(ca_certs=certifi.where())

            #headers["Accept-encoding"] = "application/json"


            #resp = http.request('POST', url, data=msg)
            #resp = requests.post(url,data=msg)
            #print (resp.text)

            #resp = http.request('POST', url, data=json.dumps(msg))
            #resp = requests.post(url,headers=headers,json=msg)
            #---------------------------------
        print (resp.text)
        #---------------------------------
        if resp.status_code!=200:
            logger.error("\nREST API Error {0}".format(resp))
            logger.error(" Url: {0}".format(url))
            logger.error(" Json: {0}".format(msg))
        #---------------------------------
    except Exception as e:
        logger.info("\n***************   Error *********\n")
        logger.info(e)
 
    return resp

def autoupdateWebsite(header,output_withURLs,output_withoutURLs):

    for entry in header: print (f"\t{entry}")

    #header = ['handleId', 'fieldType', 'name', 'description', 'productImageUrl', 'collection', 'sku', 
    #          'ribbon', 'price', 'surcharge', 'visible', 'discountMode', 'discountValue', 'inventory', 
    #          'weight', 'productOptionName1', 'productOptionType1', 'productOptionDescription1']

    # Is [1:] because first line is the above header for each.
    if output_withURLs!=[]:
        #/////////////////////////////////////////////////////
        #           EXISTING PRODUCT
        #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
        print ("#/////////////////////////////////////////////////////")
        print ("#           EXISTING PRODUCTs")
        print ("#/////////////////////////////////////////////////////")
        for existingItem in output_withURLs:
            
            # HYPOTHETICALLYT::::
            #   - if product already exists online and the fields we're sending it are ALREADY based on information taken from website
            #       maybe all we have to do is send it the information necessary to updateQTY
            #=================================================
            #   Get PID
            sku     = existingItem[header.index("sku")]
            resp    = get_product(sku)
            PID     = str(get_PID(resp))
            #=================================================
            if PID == '': 
                continue 
                print (f"{sku} has no PID found on WIX. This shouldn't happen, as the list obj fed to this function should already have been filtered for pre-existing on the website.")
                # Can't update a product that has not been found. Shouldn't happen...
                # Maybe Add contingency to add this missing row to the withoutURLs array?
            #<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            #<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            #<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            if existingItem[header.index('productOptionType1')]         == None:
                optiontype1 = ""
            else:   optiontype1                 =   existingItem[header.index('productOptionType1')]
            #--------------------
            if existingItem[header.index('productOptionDescription1')]  == None:
                productOptionDescription1 = ""
            else:   productOptionDescription1   =   existingItem[header.index('productOptionDescription1')]
            #--------------------
            if existingItem[header.index('productOptionName1')]         == None:
                productOptionName1 = ""
            else:   productOptionName1          =   existingItem[header.index('productOptionName1')]
            #--------------------
            temp_choice = Choice(optiontype1,productOptionDescription1)
            temp_option = ProductOptionKey(productOptionName1,[temp_choice])
            #<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            #<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            #<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            flat_temp_product = FlattenedNewWixProduct(
                name                =   existingItem[header.index("name")],
                description         =   existingItem[header.index("description")],
                sku                 =   existingItem[header.index("sku")],
                price               =   float(existingItem[header.index("price")]),
                discount_type    =   existingItem[header.index("discountMode")],
                discount_value   =   existingItem[header.index("discountValue")],
                visible             =   bool(existingItem[header.index("visible")]),
                weight              =   int(existingItem[header.index("weight")]),
                ribbon              =   existingItem[header.index("ribbon")],
                manage_variants     =   True
                )
            #<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            #=================================================
            ## FLAT
            new_dict = flat_temp_product.to_dict()

            new_dict.update({'option_name': productOptionName1})
            new_dict.update({'option_value': optiontype1})
            new_dict.update({'option_desc': productOptionDescription1})

            new_dict.update({'productId':PID})
            updateProduct(new_dict)
 
            #=================================================
            ## NON FLAT
            #updateOBJ = UpdateWixProduct(PID,temp_product)
            #temp_dict = updateOBJ.to_dict()
            #updateProduct(temp_dict)
            #=================================================
            # Fields to potentially update later:
            #QTY_to_add = existingItem[header.index("inventory")]
            collections_to_updateOrAdd = existingItem[header.index("collection")]
            url = existingItem[header.index("productImageUrl")]

            # WHAT GOES INTO THIS:
            '''
            - update product fields (everything but qty)
                - if the field already exists... do we overwrite the field with the new content?
            - update qty (this is a problem, because the way the function is currently set up is we are taking the actual inventory count at hand
                and telling the website what the actual count IS.... meaning:
                    - if site thinks we have 20.. and we say we have 25... the site adds 5. 
                    - if site thinks we have 20.. and we say we have 5.... the site subtracts 20.
                ::: SO:: two ways to go about this:
                    - 1) call the increment/decrementQTY functions separately
                        OR
                    - 2) suppose we are going to input the proper file into CounterPoint, which will trigger our updateWix task, and change the qty
                        ^^^ THIS ONE

            - for UPDATEWIX::: need to look into adding products.... do they update?
                - if YES:
                    All we need to do is generate the wix files, update product fields, and the QTY will be changed later via UPDATEWIX
                - if NO:
                    Then we update product fields AND updateQTY
            '''
    if output_withoutURLs!=[]:
        #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
        #           NEW PRODUCT
        #/////////////////////////////////////////////////////
        print ("#/////////////////////////////////////////////////////")
        print ("#           NEW PRODUCTs")
        print ("#/////////////////////////////////////////////////////")
        # NOTES:
        #   - can technically use the same class as ExistingProduct, and demand that name and price are included here, despite being optional in the class  

        # "https://johnsonsflorists.com/_functions/CreateProductFlattened?name=Test+Product+F&description=Not+a+real+product%3B+for+internal+testing.+Thank+you+for+your+patience.&price=6&sku=12345678&visible=True&discount_type=PERCENT&discount_value=0&manage_variants=True&product_type=physical&weight=5&option_name=&option_value=&option_desc="

        #   - TOM wants not to create products, but I see some options:
        #       - create, but leave invisible until later implementation (perhaps when URLs for items are given?)
        #       - auto-sort into collections based on most superficial aspect of Departments?

        successfully_added = [header]

        for newItem in output_withoutURLs:

            for i,x in enumerate(newItem):
                print (header[i],"\t",x)
            
            # CREATING NEW PRODUCT
            #<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            if newItem[header.index('productOptionType1')] == None:
                optiontype1 = ""
            else:   optiontype1                 =   newItem[header.index('productOptionType1')]
            #--------------------
            if newItem[header.index('productOptionDescription1')] == None:
                productOptionDescription1 = ""
            else:   productOptionDescription1   =   newItem[header.index('productOptionDescription1')]
            #--------------------
            if newItem[header.index('productOptionName1')] == None:
                productOptionName1 = ""
            else:   productOptionName1          =   newItem[header.index('productOptionName1')]
            #--------------------
            temp_choice = Choice(optiontype1,productOptionDescription1)
            temp_option = ProductOptionKey(productOptionName1,[temp_choice])       
            #<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            flat_temp_product = FlattenedNewWixProduct(
                name                =   newItem[header.index("name")],
                description         =   newItem[header.index("description")],
                sku                 =   newItem[header.index("sku")],
                price               =   float(newItem[header.index("price")]),
                discount_type           =   newItem[header.index("discountMode")],
                discount_value          =   newItem[header.index("discountValue")],
                visible              =  False,      # =   bool(newItem[header.index("visible")]),
                weight              =   int(newItem[header.index("weight")]),
                ribbon              =   newItem[header.index("ribbon")],
                manage_variants     =   True)
            #<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            #=================================================
            #=================================================
            # Now convert to DICT and feed to createProduct()
            #=================================================
            temp_dict = flat_temp_product.to_dict()
            temp_dict.update({'option_name': productOptionName1})
            temp_dict.update({'option_value': optiontype1})
            temp_dict.update({'option_desc': productOptionDescription1})
            #=================================================
            # Create
            resp = createProduct(temp_dict)
            if resp!=None:
                if resp.status_code==200:
                    successfully_added.append(newItem)
            #good_add.append(True)
            #else: 
            #    good_add.append(False)
            #else:
            #    good_add.append(False)
            # Now convert to DICT and feed to updateProduct()
            #=================================================
            # No Collections Exist
            # No URL Exists
            #QTY_to_add = newItem[header.index("inventory")]
            # ^^ SHOULD BE UNUSED



        #Gspread_Rubric.updateSheetfromTop("JFGC_NakedProducts_AutoAdd",successfully_added)

        


#=================================================================================
#       MAIN
#=================================================================================


def generate_wix_files_from_xlsx(filename,parentfolder,i):
    # Given an COUNTERPOINT-formatted excel file, and its parent folder, 
    #    generate the two wix formatted files in the same directory.
    if filename.endswith('.xlsx'):  fromFile = parentfolder+filename
    else:                           fromFile = parentfolder+filename+'.xlsx'
    #===============================================
    with dpg.window(label="Wix Format Progress"):
        title = f"wix_prog_{i}"
        dpg.add_progress_bar(id=title,overlay="% Complete",show=True,width=200)
    #===============================================
    working_list    = File_Operations.excel_to_list(fromFile)[0]
    working_header  = working_list[0]
    working_rows    = working_list[1:]
    #===============================================
    #ITEM_NO	, PROF_ALPHA_2 , DESCR , LST_COST , PRC_1 , TAX_CATEG_COD , CATEG_COD , ACCT_COD , ITEM_VEND_NO , PROF_COD_4 , PROF_ALPHA_3 , PROF_DAT_1 , QTY , ImageUrl , ImageUrl2 , Description , ProductType , Collection , OptionName , OptionType , OptionDescription
    output_header       =   ['handleId','fieldType','name','description','productImageUrl','collection','sku','ribbon','price','surcharge','visible','discountMode','discountValue','inventory','weight','productOptionName1','productOptionType1','productOptionDescription1']
    output_withURLs     =   [output_header]
    output_withoutURLs  =   [output_header]
    #===============================================
    for i,row in enumerate(working_rows):
        print (f'\n\n<><><><><><><><><>\t{i} out of {len(working_rows)}')
        print (row)
        #===============================================
        percent_complete    =   (working_rows.index(row)/len(working_rows))
        dpg.configure_item(title,show=True,default_value=percent_complete,overlay=f"{int(percent_complete*100)}%")
        #===============================================
        temp_list   =   []
        sku         =   ''
        has_url     =   None
        #===============================================
        for column in output_header:
            if column == 'handleId':
                #------------------------------
                sku = row[working_header.index('ITEM_NO')]
                sku = sku.replace(" ","")
                #=================================================
                # The following was because some products were returned as 404 or 500 errors, when no products should still be 200
                #   merely with "No products" found
                good_resp   =   False
                counter     =   0
                while not good_resp:
                    resp = get_product(sku)

                    if resp==None:
                        counter+=1
                        continue

                    if resp.status_code!=200:
                        print (f"--> bad resp: trying again {counter}x...")
                        counter+=1
                        time.sleep(7)
                    else:
                        good_resp=True

                    if counter==5:
                        break

                if good_resp==False: 
                    print(f"{sku} not yielding correct response from WIX... please check row data:")
                    print (row)
                    print("Skipping for now...")
                    continue
                #=================================================
                temp_list.append(sku)
                #------------------------------
            elif column == 'sku':
                temp_list.append(sku)
            elif column == 'fieldType':
                #------------------------------
                temp_list.append("Product")
                #------------------------------
            elif column == 'name' or column == 'description':
                #------------------------------
                temp_list.append(row[working_header.index('DESCR')])
                #------------------------------
            elif column == 'productImageUrl':
                #------------------------------
                url = row[working_header.index('ImageUrl')]
                if url == '' or url == None or url=='None':
                    #------------
                    temp_url = get_url(resp)
                    #------------
                    if temp_url     ==  '':
                        has_url = False
                    else: has_url   =   True
                    #------------
                    temp_list.append(temp_url)
                else:
                    temp_list.append(url)
                    has_url = True
                #------------------------------
            elif column == 'collection':
                #------------------------------
                temp_list.append(get_collection(resp))
                #------------------------------
            elif column == 'ribbon':
                #------------------------------
                temp_list.append('')
                #------------------------------
            elif column == 'price':
                #------------------------------
                # Could check again here for '$', but should already be cleaned.
                temp_list.append(row[working_header.index('PRC_1')])
                #------------------------------
            elif column == 'surcharge':
                #------------------------------
                temp_list.append('')
                #------------------------------
            elif column == 'visible':
                #------------------------------
                temp_list.append('TRUE')
                #------------------------------
            elif column == 'discountMode':
                #------------------------------
                temp_list.append('PERCENT')
                #------------------------------
            elif column == 'discountValue':
                #------------------------------
                temp_list.append('0')
                #------------------------------
            elif column == 'inventory':
                #------------------------------
                temp_list.append(row[working_header.index('QTY')])
                #------------------------------
            elif column == 'weight':
                #------------------------------
                temp_list.append('5')
                #------------------------------
            elif column == 'productOptionName1':
                # Special consideration for variants must be made
                temp_list.append('')
                #------------------------------
            elif column == 'productOptionType1':
                # Special consideration for variants must be made
                temp_list.append('')
                #------------------------------
            elif column == 'productOptionDescription1':
                # Special consideration for variants must be made
                temp_list.append('')
                #------------------------------
            elif column == 'ribbon':
                temp_list.append(row[working_header.index('CATEG_COD')])
            #=================================================
        dpg.configure_item(title,show=True,default_value=1,overlay="100%")
        #=================================================
        if has_url:
            if temp_list not in output_withURLs:
                output_withURLs.append(temp_list)
        else: 
            # here, try and implement the 
            '''for row in output_withoutURLs[1:]:

                _tempUrl = ""
                _name = row[output_header.index("name")]

                #name / description confidence/fidelity scores

                row[output_header.index("productImageUrl")] = _tempUrl'''

            if temp_list not in output_withoutURLs:
                output_withoutURLs.append(temp_list)
    #===============================================
    #Gspread_Rubric.updateSheetfromTop("JFGC_NakedProducts",output_withoutURLs)

    #===============================================
    return output_withURLs,output_withoutURLs


def noUrl_autofill_main(filename, parentfolder):
    #print(filename)
    #print(parentfolder)
    fromFile = f'{parentfolder}\{filename}'
    #print(fromFile)

    import OpenAI

    with dpg.window(label="NO_URL Autofull Progress"):
        title = f"NO_URL_PROG"
        dpg.add_progress_bar(id=title,overlay="% Complete",show=True,width=200)

    #===============================================
    working_list    = File_Operations.excel_to_list(fromFile)[0]
    working_header  = working_list[0]
    working_rows    = working_list[1:]
    #===============================================
    #ITEM_NO	, PROF_ALPHA_2 , DESCR , LST_COST , PRC_1 , TAX_CATEG_COD , CATEG_COD , ACCT_COD , ITEM_VEND_NO , PROF_COD_4 , PROF_ALPHA_3 , PROF_DAT_1 , QTY , ImageUrl , ImageUrl2 , Description , ProductType , Collection , OptionName , OptionType , OptionDescription
    output_header       =   ['handleId','fieldType','name','description','productImageUrl','collection','sku','ribbon','price','surcharge','visible','discountMode','discountValue','inventory','weight','productOptionName1','productOptionType1','productOptionDescription1']
    output              =   [output_header]
    #===============================================
    # underneath each line have the autosuggestions printed on a number of lines below each change
    for i,row in enumerate(working_rows):
        
        for ii,column in enumerate(row):
            if column=="None": row[ii]=""


       

        percent_complete    =   (working_rows.index(row)/len(working_rows))
        dpg.configure_item(title,show=True,default_value=percent_complete,overlay=f"{int(percent_complete*100)}%")
        #-------------------------------
        _name = row[output_header.index('name')]
        _sku = row[output_header.index('handleId')]
        #-------------------------------
        # OPEN AI
        '''
        try:
             _dept = int(row[output_header.index('ribbon')])

            if i>0 and i%3==0: 
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                print("circumventing rate limit; waiting 60seconds")
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                time.sleep(60)

            gpt = OpenAI.chatGPTClient()
            kwargs = {"productName": _name,"dept":_dept}
            _desc = gpt.submitProduct(**kwargs)

            if _desc !="":
                _temp_autofills=['' for x in output_header]

                _temp_autofills[output_header.index('description')] = _desc
                output.append(_temp_autofills)
        except:
            print("OpenAI is mad at us.... skipping!")
        '''
        #-------------------------------
        # Check if prod already exists
        alreadyExistingProds = checkifProdAlreadyExists(_sku)
        if alreadyExistingProds != []:
            print(f'{_name} already exists on website! Removing from AUTOFILLED file')
            for i,product in enumerate(alreadyExistingProds):
                _next_autofills = ['' for x in output_header]
                _next_autofills[output_header.index('handleId')]        = product["sku"]
                _next_autofills[output_header.index('fieldType')]       = f'{product["fidelity"]}%'
                _next_autofills[output_header.index('name')]            = product["name"]
                _next_autofills[output_header.index('productImageUrl')] = product["mainMedia"]

                #output.append(_next_autofills)

        else:
            #-------------------------------
            output.append(row)

            try:
                sortableList    =   get_sortable_generatedList(_name)
                sortedList      =   []
                names_to_scores =   {}

                for i,prod in enumerate(sortableList):
                    names_to_scores.update({prod["name"]:prod["fidelity"]})

                from collections import Counter
                c           =   Counter(names_to_scores)
                sortedList  =   c.most_common()
   

                for i,pair in enumerate(sortedList):

                    for i,prod in enumerate(sortableList):
                        if prod["name"] == pair[0]:
                            product = sortableList[i]
                            break
                    
                    _next_autofills = ['' for x in output_header]
                    _next_autofills[output_header.index('handleId')]        = product["sku"]
                    _next_autofills[output_header.index('fieldType')]       = f'{product["fidelity"]}%'
                    _next_autofills[output_header.index('name')]            = product["name"]
                    _next_autofills[output_header.index('description')]            = product["description"]
                    _next_autofills[output_header.index('productImageUrl')] = product["mainMedia"]


                    cutoff = dpg.get_value('noURLCutoff')

                    if i==0:
                        output.append(_next_autofills) # always publishes the highest fidelity score
                    else:
                        if prod["fidelity"] >= cutoff:
                            output.append(_next_autofills)
                        else:
                            print(f"{product['name']}'s {product['fidelity']}% below cutoff! Skipping")

            except Exception as e:
                print (e)

    #===============================================
    dpg.configure_item(title,show=True,default_value=1,overlay="100%")
    File_Operations.list_to_excel(output,f'{fromFile[:-4]}_AUTOFILLED.xlsx')


def generate_gradedList(desc):
    #=============
    resp = None
    #=============
    try:
        #---------------------------------
        msg={'desc':str(desc)}
        #---------------------------------
        #---------------------------------
        url = "https://johnsonsflorists.com/_functions/GetSimilarProducts/"
        resp = requests.get(url,msg)
        #---------------------------------
        #---------------------------------
        if resp.status_code!=200:
            print("--------------------- BAD:\t",desc)
            print(resp.text)

        else:
            print("--------------------- GOOD:\t",desc)
            #print(resp.text)
        #---------------------------------
    except Exception as e:
        print(f'--------------------- ERROR:\t_{desc}_\t{e}')
        logger.info("\n***************   Error *********\n")
        logger.info(e)
    return resp


def generateFidelity(search,result):

    search = search.lower()
    result = result.lower()

    original_list1 = search.split(" ")
    original_list2 = result.split(" ")

    # Find the number of common elements in both lists
    common_elements = set(original_list1).intersection(set(original_list2))
    num_common_elements = len(common_elements)
 
    # Find the total number of unique elements in both lists
    total_elements = set(original_list1).union(set(original_list2))
    num_total_elements = len(total_elements)
 
    # Calculate the percentage similarity
    percentage_similarity = (num_common_elements / num_total_elements) * 100
    return int(percentage_similarity)


def get_sortable_generatedList(name):

    resp = generate_gradedList(name)
    respJson = resp.json()
    products = respJson.get("products",{})
    #print(products)

    sortable = []

    for x in products: 

        fidelity = generateFidelity(name,x["name"])

       
        try:
            _prod = {}
            _prod["fidelity"]   = fidelity
            _prod['mainMedia']  = x["mainMedia"]
            _prod["name"]       = x["name"]
            _prod["sku"]        = x["sku"]
            _prod["description"]= x["description"]
            sortable.append(_prod)
        except:
            print("IS VARIANT")
            for variant in x["variants"]:
                _prod = {}

                _variant_name = f'Variant of : {x["name"]} : {variant["choices"]}'
                _sku = variant["variant"]["sku"]

                _prod["fidelity"]   = fidelity
                _prod['mainMedia']  = x["media"]
                _prod["name"]       = _variant_name
                _prod["sku"]        = _sku
                _prod["description"]= "**PLEASE SEE MAIN PRODUCT FOR DESCRIPTION**"

                sortable.append(_prod)


    return sortable


def openAITest():
    token = "Japanese Holly"
    token = "Achillea 'Sassy Sum Taffy'"
    token = "Achillea 'Sassy Sum Taffy' PP 4 qt."


    token = "Achillea 'Sassy Sum Taffy' PP 4"
    token = "Achillea 'Sassy Sum Taffy' PP"
    token = "Achillea 'Sassy Sum Taffy'"
    token = "Achillea 'Sassy Sum"
    token = "Achillea 'Sassy"
    token = "Achillea"

    #token = "Japanese Beech Fern"
    #token = "Japanese Beech Fern #1"
    #token = "PLANT SAUCER" #   8\" PLANT SAUCER CLEAR VINYL

    resp = generate_gradedList(token)

    print (type(resp.json()))
    respJson = resp.json()
    products = respJson.get("products",{})
    #print(products)
    for x in products: 
        #print (x)


        try:
            print (f'{x["name"]}:\n\t{x["sku"]} with a score of {generateFidelity(token,x["name"])}%')

            _name = x["name"]
            _sku = x["sku"]

            print (f'\t{x["mainMedia"]}')
        except:
            print("IS VARIANT")
            for variant in x["variants"]:
                variant_name = f'Variant of : {x["name"]} : {variant["choices"]}'
                print (variant_name)
                print (f'{x["name"]}:\n\t{variant["variant"]["sku"]} with a score of {generateFidelity(token,x["name"])}%')
                print (f'\t{x["mainMedia"]}')


def checkifProdAlreadyExists(sku):

    resp = get_product(sku)
    respJson = resp.json()
    products = respJson.get("products",{})
    sortable=[]

    if products != "No product": # should be switched to empty list
        print(products)
        for product in products:
            try:
                _prod = {}
                _prod["fidelity"]   = 100
                _prod['mainMedia']  = product["mainMedia"]
                _prod["name"]       = product["name"]
                _prod["sku"]        = product["sku"]
                _prod["description"]= product["description"]

                sortable.append(_prod)
            except:
                print("IS VARIANT")
                # Because looking up SKU and not NAME, variant is merely returned, but not in list
                _prod = {}

                _prod["fidelity"]   = 100
                _prod['mainMedia']  = product["media"]
                _prod["name"]       = product["fullVariantName"]
                _prod["sku"]        = product["sku"]
                _prod["description"]= "**PLEASE SEE MAIN PRODUCT FOR DESCRIPTION**"
                sortable.append(_prod)
    return sortable

def main():
    a = '705876920901'
    a = '872142313429'
    a = 'VD38B' #variant
    
    prods = checkifProdAlreadyExists(a)
    print (prods)

if __name__=="__main__":
    main()