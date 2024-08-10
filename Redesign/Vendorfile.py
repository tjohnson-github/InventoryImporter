from dataclasses import dataclass, field
import File_Operations
import dearpygui.dearpygui as dpg


@dataclass
class InputFile:
    #==============================
    # Clerical
    fullPath: str   = field(repr=False)
    #==============================
    name: str       = field(init=False) 
    extension: str  = field(init=False,repr=False) 
    #==============================
    # Contents
    header: list    = field(init=False,repr=True)
    rows : list     = field(init=False,repr=False)
    #==============================
    # User Input
    #vendorName: str = field(init=False,repr=False)
    #vendorCode: str = field(init=False,repr=False)
    #department: int = field(init=False)
    #taxCode: str    = field(init=False,repr=False)
    #==============================
    #note: str                   = field(init=False,repr=False)
    #formatting_dict_name: str   = field(init=False,repr=False)
    #formatting_dict: dict       = field(init=False,repr=False)

    def __post_init__(self):

        def naming():

            splitFullPath   = self.fullPath.split("\\")
            self.name       = splitFullPath[-1]

            splitName       = self.name.split(".")
            temp_name       = splitName[0]

            self.extension  = splitName[-1]
        # =================================================
        
        # =================================================
        '''match self.extension:
            case "csv":
                output_array,errorMsg    =   File_Operations.csv_to_list(self.fullPath)

            case "xlsx":
                output_array,errorMsg    =   File_Operations.excel_to_list(self.fullPath)'''


        def contents():
            try:

                if(self.extension=="csv"):
                    output_array    =   File_Operations.csv_to_list(self.fullPath)
                elif(self.extension=="xlsx"):
                    output_array    =   File_Operations.excel_to_list(self.fullPath)

            except Exception as e:
                print(f"Failure reading {self.fullPath}:\n\t{e}")

            try:

                if output_array==False: 
                    self.header = []
                    self.rows   = []
                    return

                self.header = output_array[0]
                self.rows   = output_array[1:]
            except UnboundLocalError as e:
                #with dpg.window(popup=True):
                #    dpg.add_text(f"{self.fullPath} could not be read! Be sure you saved it with correct extension instead of manually changing.")
                self.note = "COULD NOT READ"
                return


        def OLDtagger():
            # =================================================
            # Try to populate rest using our common naming conventions
            #if temp_name.count("-") > temp_name.count("_"):
            #    delim = '-'
            #else:
            #    delim = '_'
            delim       =   '-'
            temp_name   =   temp_name.split(delim)

            if self.name.startswith("Inventory-format-"):
                temp_info   =   temp_name[2:]
            elif self.name.startswith("Inventory-"):
                temp_info   =   temp_name[1:]
            else:
                temp_info   =   temp_name


            index_offset = 1

            try:
                self.vendorName = temp_info[0+index_offset]
                self.vendorCode = ""
                self.note       = f'{self.vendorName}_{temp_info[1+index_offset]}'

                self.department = temp_info[-1]
                self.department = self.department.replace("Dept","")
                self.department = self.department.replace(" ","")
                self.department = ''.join(i for i in self.department if i.isdigit())
            except Exception as e:
                print (f'Error formatting {self.name}:\t{e}')
                self.vendorName = "None Found"
                self.vendorCode = ""
                self.note       = ""
                self.department = 0

        naming()
        contents()

        #self.taxCode = "TX" #Default
        # ^ ^ ^ ^ ^ ^ ^
        # THIS IS GOING TO BE REPLACED WITH THE ABILITY TO IMPORT YOUR OWN
        # "DATA" JSON OBJECTS
        # WHEREBY EACH KEY LEADS TO NESTED DICT
        # KEY = tag name
        # subkey = field name
        # subval = field value... like 
        # TAX CODE = [
        # "TX",
        # "ED",
        # ]
        # Vendor ID = {
        # arett : 0154341,
        # etc.

    def displayContents(self):
        print (self.header)
        for row in self.rows:
            print (row)

    def set_formatting_dict(self,name,format):
        self.formatting_dict_name   =   name
        self.formatting_dict        =   format
    
    def set_manual_input(self,tax,code,dept):
        self.taxCode       =   tax
        self.vendorCode    =   code
        self.department     =   dept

if __name__=="__main__":

    dir = "C:\\Users\\Andrew\\source\\repos\\VENDOR_FILES\\INPUT"
    file = "Inventory-twoscompany-288c-35.xlsx"

    testfile = vendorfile(f'{dir}\\{file}')
    print (testfile.displayContents())