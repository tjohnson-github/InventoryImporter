from dataclasses import dataclass, field
import File_Operations
import dearpygui.dearpygui as dpg


@dataclass
class vendorfile:
    #==============================
    # Clerical
    fullPath: str   = field(repr=False)
    name: str       = field(init=False) 
    extension: str  = field(init=False,repr=False) 
    #==============================
    # Contents
    header: list    = field(init=False,repr=True)
    rows : list     = field(init=False,repr=False)
    #==============================
    # User Input
    vendorName: str = field(init=False,repr=False)
    vendorCode: str = field(init=False,repr=False)
    department: int = field(init=False)
    taxCode: str    = field(init=False,repr=False)
    #==============================
    note: str                   = field(init=False,repr=False)
    formatting_dict_name: str   = field(init=False,repr=False)
    formatting_dict: dict       = field(init=False,repr=False)

    def __post_init__(self):
        splitFullPath   = self.fullPath.split("\\")
        self.name       = splitFullPath[-1]
        splitName       = self.name.split(".")
        temp_name       = splitName[0]
        self.extension  = splitName[-1]
        # =================================================
        self.taxCode = "TX" #Default
        # =================================================
        '''match self.extension:
            case "csv":
                output_array,errorMsg    =   File_Operations.csv_to_list(self.fullPath)

            case "xlsx":
                output_array,errorMsg    =   File_Operations.excel_to_list(self.fullPath)'''

        
        try:

            if(self.extension=="csv"):
                output_array,errorMsg    =   File_Operations.csv_to_list(self.fullPath)
            elif(self.extension=="xlsx"):
                output_array,errorMsg    =   File_Operations.excel_to_list(self.fullPath)
        except Exception as e:
            print(f"Failure reading {self.fullPath}\t:\t{e}")

        try:
            if output_array==False: 
                print("\t"+errorMsg+"\n")
                self.header = []
                self.rows   = []
                return

            #print("-----------------------------")
            #print(self.name)
            #print (f"OUTPUT ARRAY [0]:\t{output_array[0]}")
            self.header = output_array[0]
            #print (f"OUTPUT ARRAY [0]:\t{self.header}")
            self.rows   = output_array[1:]
        except UnboundLocalError as e:
            #with dpg.window(popup=True):
            #    dpg.add_text(f"{self.fullPath} could not be read! Be sure you saved it with correct extension instead of manually changing.")
            self.note = "COULD NOT READ"
            return
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

        #print("---------NAME format begin------")
        #print (temp_info)

        try:
            self.vendorName = temp_info[0]
            self.vendorCode = ""
            self.note       = f'{self.vendorName}_{temp_info[1]}'

            self.department = temp_info[2]
            self.department = self.department.replace("Dept","")
            self.department = self.department.replace(" ","")
            self.department = ''.join(i for i in self.department if i.isdigit())
        except Exception as e:
            print (f'Error formatting {self.name}:\t{e}')
            self.vendorName = "None Found"
            self.vendorCode = ""
            self.note       = ""
            self.department = 0

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