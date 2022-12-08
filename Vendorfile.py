from dataclasses import dataclass, field

@dataclass
class vendorfile:
    #==============================
    name: str 
    #==============================
    header: list = field(init=False)
    rows : list = field(init=False)
    #==============================
    department: int = field(init=False)
    extension: str  = field(init=False) 
    #==============================


class vendorfileOld:
    filename                =   ""
    header                  =   []
    rows                    =   []
    department              =   0
    filetype                =   ""

    filename_items          =   ["Vendor","Notes","Dept.","Extension"]
    filename_info           =   {}
    
    tax_code                =   ""
    vendor_code             =   0

    formatting_dict_name    =   ""
    formatting_dict         =   {}

    def parse_name(self):
        try:
            #--------------------
            #splits name into relevant sections
            temp            =   self.filename.split(".")
            temp_info       =   temp[0].split("-")
            file_extension  =   temp[1]
            #--------------------
            self.filetype   =   file_extension

            if self.filename.startswith("Inventory-format-"):
                temp_info   =   temp_info[2:]
            elif self.filename.startswith("Inventory-"):
                temp_info   =   temp_info[1:]
            else:
                temp_info   =   temp_info

            temp_info.append(file_extension)
            #--------------------
            # Separates the extension because its not clear how many notes there will be
            for item in self.filename_items:
                if item=="Extension":
                    self.filename_info.update({item:file_extension})
                elif item=="Dept.":

                    temp_dept = temp_info[self.filename_items.index(item)]

                    temp_dept = temp_dept.replace("Dept","")
                    temp_dept = temp_dept.replace(" ","")


                    self.filename_info.update({item:temp_dept})
                else:
                    self.filename_info.update({item:temp_info[self.filename_items.index(item)]})
            #--------------------
            # Removes all extraneous alphabetic characters from dept, isolating numeric
            temp_dept   =   self.filename_info["Dept."]
            temp_dept   =   ''.join(i for i in temp_dept if i.isdigit())
            self.filename_info.update({"Dept.":temp_dept})
            #--------------------
        except:
            print (f'{self.filename} cannot be read due to incorrect filename conventions.')

    def __init__(self, vendor_dict):


        self.filename       = list(vendor_dict.keys())[0]
        print (self.filename)
        print (type(self.filename))
        self.header         = vendor_dict[self.filename][0]
        self.rows           = vendor_dict[self.filename][1:]
        self.parse_name()
        #=================
        #import random
        #fixer = random.randint(1, 9999)
        #self.filename       = list(vendor_dict.keys())[0]+"_"+str(fixer)
        #print (self.filename)

    def set_manual_input(self,tax,code,dept):
        self.tax_code       =   tax
        self.vendor_code    =   code
        self.department     =   dept

    def visualize(self):
        pass

    def print_info(self):
        print ("Name:\t",self.filename)
        print ("Header:\t",self.header)
        print ("Rows:")
        for x in self.rows:
            print ("\t",x)

    def set_formatting_dict(self,name,format):
        self.formatting_dict_name   =   name
        self.formatting_dict        =   format

    def expandedView(self,sender):
        #parent = self.filename+"_expandTest"

        #borders_innerH (bool, optional) – Draw horizontal borders between rows.
        #borders_outerH (bool, optional) – Draw horizontal borders at the top and bottom.
        #borders_innerV (bool, optional) – Draw vertical borders between columns.
        #borders_outerV (bool, optional) – Draw vertical borders on the left and right sides

        with dpg.window(label=f"Expanded view of {self.filename}",id=self.filename+'_expandWindow',width=900,height=500):
            
            with dpg.table(header_row=True,borders_innerH=True,borders_outerH=True,borders_innerV=True,borders_outerV=True,no_clip=True,resizable=True,hideable =True):

                xx=0;    yy=0
                table_id=self.filename+f'_{xx},{yy}'

                for item in self.header:
                    #if item != 'None' and item != None:
                    dpg.add_table_column(label=item,no_reorder=False)
                    table_id=self.filename+f'_{xx},{yy}'
                    yy+=1

                table_id=self.filename+f'_{xx},{yy}'

                for row in self.rows:
                    yy=0
                    for item in row:
                        table_id=self.filename+f'_{xx},{yy}'
                        dpg.add_text(id=table_id,default_value=item)
                        dpg.add_table_next_column()
                        yy+=1
                    xx+=1