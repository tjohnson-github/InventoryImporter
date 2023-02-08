from dataclasses import dataclass, field
import pyodbc


from File_Operations import saveVariable,getVariable

class SQLClient:

    server      =   '192.168.4.13'
    driver      =   '{ODBC Driver 17 for SQL Server}'
    username    =   'sa'
    password    =   'CounterPoint8'

    def __init__(self):
        try:
            #----------------
            conn_str=(';DRIVER='+self.driver+';SERVER='+self.server+';UID='+self.username+';PWD='+self.password)        
            print(conn_str)
            cnxn = pyodbc.connect(conn_str)
            cursor = cnxn.cursor()
            #----------------
            self.cnxn   = cnxn
            self.cursor = cursor
        except Exception as e:
            print ("_____ERROR_____")
            print ("Cursor object not initialized correctly. Please run Setup and retry.")
   
           
@dataclass
class Department:
    code: int               = field(repr=True)
    name: str               = field(repr=True)
    margin: float           = field(repr=False,default=None)
    formatted_code: str     = field(init=False,repr=False)
    dptStr: str             = field(init=False,repr=False)

    def __post_init__(self):

        if len(str(self.code))==1:
            self.formatted_code = f'00{self.code}'
        else:
            self.formatted_code = f'0{self.code}'

        self.dptStr = f'{self.code} : {self.name}'

allDepartments: list = [
        Department(code=1,name="Cut Flowers",margin=65.2),
        Department(code=2,name="Ribbons & Bows",margin=59.0),
        Department(code=3,name="Design - Cut",margin=59.0),
        Department(code=4,name="Holiday Silk",margin=64.2),
        Department(code=5,name="Dried & Silk",margin=64.7),
        Department(code=6,name="Candles",margin=64.2),
        Department(code=7,name="Balloons",margin=64.7),
        #Department(code=8,name="",margin=),
        #Department(code=9,name="",margin=),
        Department(code=10,name="Green Houseplants",margin=69.5),
        Department(code=11,name="Bloom Houseplants",margin=69.5),
        Department(code=12,name="Potted Bulbs - Hp",margin=69.5),
        #Department(code=13,name="",margin=),
        Department(code=14,name="Pottery-Inside/Outside",margin=60.32),
        Department(code=15,name="Bedding Plants",margin=66.0),
        Department(code=16,name="Perennials",margin=69.27),
        Department(code=17,name="Vegetables",margin=66.0),
        #Department(code=18,name="",margin=),
        #Department(code=19,name="",margin=),
        Department(code=20,name="Woodies",margin=66.0),
        Department(code=21,name="Holiday Live Trees",margin=66.0),
        #Department(code=22,name="",margin=),
        Department(code=23,name="Bulbs & Tubers",margin=64.2),
        Department(code=24,name="Seeds - Flwr/Veg",margin=56.2),
        Department(code=25,name="Garden Supplies",margin=59.5),
        Department(code=26,name="Bagged Goods - Gs",margin=56.2),
        Department(code=27,name="Ponds & Supplies",margin=56.2),
        #Department(code=28,name="",margin=),
        Department(code=29,name="Patio Living",margin=64.0),
        Department(code=30,name="Contributions"),
        Department(code=31,name="Concrete - All",margin=61.0),
        Department(code=32,name="Bagged Goods - LS",margin=64.2),
        Department(code=33,name="Fashion",margin=64.0),
        Department(code=34,name="Propane",margin=64.49),
        Department(code=35,name="Nature/Gift",margin=62.5),
        Department(code=36,name="Cards & Gift Wrap",margin=63.0),
        Department(code=37,name="Seasonal Gift",margin=63.0),
        Department(code=38,name="Gift - Corp"),
        Department(code=39,name="Cookies/Candy/Food",margin=64.0),
        Department(code=40,name="Jewelry",margin=64.0),
        #Department(code=41,name="",margin=),
        #Department(code=42,name="",margin=),
        #Department(code=43,name="",margin=),
        #Department(code=44,name="",margin=),
        Department(code=45,name="Christmas Ornaments",margin=63.0),
        Department(code=46,name="Christmas Greens & Wreaths",margin=61.0),
        Department(code=47,name="Cut Christmas Trees",margin=62.2),
        #Department(code=48,name="",margin=),
        Department(code=49,name="Pumpkins",margin=66.0)]
    


@dataclass
class JFGC_Data:
    #=====================================================
    # Dictionaries for this program should be of type:
    #   { READABLE DISPLAY VALUE : IM_INV-formatted-value }
    #=====================================================
    # The actual hardcoded info
    #tax_codes  = ["TX","DEL","NT","DE"]
    #tax_names  = ["Taxable","Delivery","Nontaxed","Edible"]

    taxDict   = {
        "Taxable"   :   "TX",
        "Delivery"  :   "DEL",
        "Nontaxed"  :   "NT",
        "Edible"    :   "DE"
        }

    allDepartments: list = field(default_factory=list)

    deptMargin =   {
        "1": 65.20,
        "1N": 65.20,
        "2": 59.00,
        "3": 59.00,
        "4": 64.20,
        "5": 64.70,
        "6": 64.20,
        "7": 64.70,
        #"8": ##,
        #"9": ##,
        "10": 69.50,
        "11": 69.50,
        "12": 69.50,
        #"13": ##,
        "14": 60.32,
        "15": 66.00,
        "16": 69.27,
        "17": 66.00,
        #"18": ##,
        #"19": ##,
        "20": 66.00,
        "21": 66.00,
        #"22": ##,
        "23": 64.20,
        "24": 56.20,
        "25": 59.50,
        "26": 56.20,
        "27": 56.20,
        #"28": ##,
        "29": 64.00,
        #"30": ##,
        "31": 61.00,
        "32": 64.20,
        "33": 64.00,
        "34": 64.49,
        "35": 62.50,
        "36": 63.00,
        "37": 63.00,
        #"38": ##,
        "39": 64.00,
        "40": 64.00,
        #"41": ##,
        #"42": ##,
        #"43": ##,
        #"44": ##,
        "45": 63.00,
        "46": 61.00,
        "47": 62.20,
        #"48": ##,
        "49": 66.00
       }
    deptNames  =   {
        1 :"Cut Flowers",
        2 :"Ribbons & Bows",
        3 :"Design - Cut",
        4 :"Holiday Silk",
        5 :"Dried & Silk",
        6 :"Candles",
        7 :"Balloons",
        #8: "",
        #9: "",
        10: "Green Houseplants",
        11: "Bloom Houseplants",
        12: "Potted Bulbs - Hp",
        #13: "",
        14: "Pottery-Inside/Outside",
        15: "Bedding Plants",
        16: "Perennials",
        17: "Vegetables",
        #18: "",
        #19: "",
        20: "Woodies",
        21: "Holiday Live Trees",
        #22: "",
        23: "Bulbs & Tubers",
        24: "Seeds - Flwr/Veg",
        25: "Garden Supplies",
        26: "Bagged Goods - Gs",
        27: "Ponds & Supplies",
        #28: Unused,
        29: "Patio Living",
        30: "Contributions",
        31: "Concrete - All",
        32: "Bagged Goods - LS",
        33: "Fashion",
        34: "Propane",
        35: "Nature/Gift",
        36: "Cards & Gift Wrap",
        37: "Seasonal Gift",
        38: "Gift - Corp",
        39: "Cookies/Candy/Food",
        40: "Jewelry",
        #41: "",
        #42: "",
        #43: "",
        #44: "",
        45: "Christmas Ornaments",
        46: "Christmas Greens & Wreaths",
        47: "Cut Christmas Trees",
        #48: "",
        49: "Pumpkins"
       }
    #=====================================================
    allDepartments: list    = field(init=False)

    dptByCode: dict         = field(init=False)
    dptByStr: dict          = field(init=False)
    dptByName: dict         = field(init=False)

    vendorDict: dict        = field(init=False)
    #=====================================================
    def get_vendor_codes(self):
        # Returns a dict object scraped from PO_VEND of the format: "Name":"00-padded vendor number"

        client = SQLClient()

        from_table              =   "PO_VEND"
        sort_by                 =   "NAM_UPR"
        client.cursor.execute(f'SELECT * FROM JFGC.dbo.{from_table} order by {sort_by} DESC;')
        headers                 =   [i[0] for i in client.cursor.description]

        vendor_nam_location     =   headers.index(sort_by)
        vendor_num_location     =   headers.index('VEND_NO')

        #vendorData             =   []
        #vendorNames            =   []
        vendorDict             =   {}

        for new_entry in client.cursor: 
            if new_entry[vendor_num_location].startswith("00"):
                vendorDict.update({str(new_entry[vendor_nam_location]):new_entry[vendor_num_location]})

        saveVariable("vendorDict.txt",vendorDict)
        self.vendorDict = vendorDict

    def __post_init__(self):
        #==============================
        # Other functions too long to post here
        self.get_vendor_codes()
        #==============================
        self.allDepartments =   []

        self.dptByCode      =   {}
        self.dptByStr       =   {}
        self.dptByName      =   {}

        for departmentCode in self.deptNames.keys():

            tempDept = Department(
                    code    = departmentCode,
                    name    = self.deptNames[departmentCode],
                    margin  = self.deptMargin.get(str(departmentCode),None)
                )

            self.allDepartments.append(tempDept)

            self.dptByCode.update({tempDept.code:tempDept})
            self.dptByStr.update({tempDept.dptStr:tempDept})
            self.dptByName.update({tempDept.name:tempDept})

    def getDptByCode(self,code):
        return self.dptByCode.get(int(code),f"No department found with code {code}!")
    
    def getDptByDptStr(self,dptStr):
        return self.dptByStr.get(dptStr,f"No department found with dptStr {dptStr}!")

    def getDptByName(self,name):
        return self.dptByName.get(name,f"No department found with name {name}!")

    