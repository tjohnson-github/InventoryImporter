from dataclasses import dataclass, field
import File_Operations
import dearpygui.dearpygui as dpg


@dataclass
class InputFile:
    #==============================
    fullPath: str   = field(repr=False)
    #==============================
    name: str       = field(init=False) 
    extension: str  = field(init=False,repr=False) 
    #==============================
    # Contents
    header: list    = field(init=False,repr=True)
    rows : list     = field(init=False,repr=False)
    #==============================


    def __post_init__(self):

        def naming():

            splitFullPath   = self.fullPath.split("\\")
            self.name       = splitFullPath[-1]

            splitName       = self.name.split(".")
            temp_name       = splitName[0]

            self.extension  = splitName[-1]
        
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
        naming()
        contents()


    def displayContents(self):
        print (self.header)
        for row in self.rows:
            print (row)

if __name__=="__main__":

    dir = "C:\\Users\\Andrew\\source\\repos\\VENDOR_FILES\\INPUT"
    file = "Inventory-twoscompany-288c-35.xlsx"

    testfile = vendorfile(f'{dir}\\{file}')
    print (testfile.displayContents())