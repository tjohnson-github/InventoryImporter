

##### WHAT HAPPENS IF THERE ARE 2 RUBRICS
### WITH THE SAME INPUT SCHEMA, BUT DIFFERENT NAMES?

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


#+++ TO DO 

#  1. make sure that when editing an EXISTING schema, you use the 'create schema' with the default.
#  2. Make sure new imports that change all the tags also change the extractors.availTags


# then need to add custom import of data; most likely via spreadsheet format
# if spreadsheet; can merely include math there?
# no; maybe can do more complex markups inside...

# VENDOR CODE:
# code : name



#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import dearpygui.dearpygui as dpg
dpg.create_context()
from dataclasses import dataclass, field
import pyodbc
import os

import CustomPickler

from SQLInterface import SQLLinker
from DPGStage import DPGStage
from DefaultPathing import DefaultPathing,DefaultPaths
import asyncio

from File_Selector import FileSelector
from File_Operations import csv_to_list,excel_to_list
from CustomPickler import get,set

from Schema_Editor import SchemaEditor

from dataclasses import dataclass

default_settings_path = "Redesign\\Settings"
default_schema_path = "Redesign\\Schemas"


class MainPage(DPGStage):

    label="Johnson's Consulting VendorFile Conversion Manager"

    # CHOOSE DESIRED OUTPUT FIRST
    # THEN DISPLAY INCOMMING FORMAT and ASK FOR CORRELATION TABLE; CREATE IF NOT EXIST; DISPLAY IF EXIST; LET EDIT
    
    # LATER, UPON LOAD, WHEN VERIFYING A TABLE WITH THAT SCHEMA, CAN SUGGEST OR EVEN AUTO-RUN FORMATTER
    #   BUT THIS NEEDS TO ASK IF 


    tutorials: bool  = False

    height: int  = 500
    width: int   = 800

    settingsName = f'{default_settings_path}\\generalSettings.txt'

    # ======================================
    # SEVERAL WAYS TO DO THIS
    # a
    settings: dict = {"tutorials":False}
    # b
    tutorials = False
    # see MAIN()

    @dataclass
    class Settings:
        tutorials: bool = False

    def main(self,**kwargs):
    
        self.settings_dc_instance = MainPage.Settings()

        def loadSettings():
            try:
                settingsDict = get(self.settingsName)
                for key,val in settingsDict.items():
                    self.settings[key]=val
            except Exception as e:
               print ("Probably doesnt exist yet:\t",e)

        loadSettings()

    def print_me(sender):
        print(f"Menu Item: {sender}")

    def generate_id(self,**kwargs):
        
        with dpg.window(height=self.height,width=self.width,label=self.label) as self._id:

            with dpg.menu_bar():
                with dpg.menu(label="File"): 

                    dpg.add_menu_item(label="New Converter",callback=self.newBuild)
                    dpg.add_menu_item(label="Set Default Directories",callback=self.setDirs)
                    #dpg.add_menu_item(label="Save", callback=self.print_me)
                    #dpg.add_menu_item(label="Save As", callback=self.print_me)

                    with dpg.menu(label="Settings"):
                        dpg.add_menu_item(label="Setting 1", callback=self.print_me, check=True)
                        dpg.add_menu_item(label="Setting 2", callback=self.print_me)

                with dpg.menu(label="View"):
                    dpg.add_checkbox(label="Pick Me", callback=self.print_me)
                    dpg.add_button(label="Press Me", callback=self.print_me)
                    dpg.add_color_picker(label="Color Me", callback=self.print_me)

                with dpg.menu(label="Help"):
                    _tut = dpg.add_checkbox(label="Tutorials",default_value = self.settings["tutorials"],callback=self.updateSettings)
                    
                    self.alt_settings: dict    = {_tut:self.tutorials}
                    self.dc_settings: dict    = {_tut:self.settings_dc_instance.tutorials}

            dpg.add_text("Welcome to our Many:One EZ Spreadsheet Converter")
            with dpg.collapsing_header(label="How to Use",default_open=False):
                #with dpg.child_window(height=500):
                dpg.add_text("This program shines in aiding businesses that have:")
                dpg.add_text(bullet=True,default_value="An array of invoices, each with different schemas, that need to be consistently reformatted into known schema.")
                dpg.add_text(bullet=True,default_value="The need to occasionally perform manual checks between conversion steps.")
                dpg.add_separator()
                dpg.add_text("To begin using it, go to File > New Converter")
                dpg.add_text("There you will build -- or import -- an output schema.")
                dpg.add_text("Input schemas will be attached to that output schema in the form of conversion rubrics.")
                dpg.add_text("This processes is aided by the use of column TAGs. These tags are shortnames you give to the nature of the data in a column.")
                dpg.add_text("In attaching a rubric: you will match an input column's TAG to the an output schema column's TAG.")
                dpg.add_separator()
                dpg.add_text("Each Converter you will build requires two things:")
                dpg.add_text(bullet=True,default_value="1) An Output Schema. This is the intended spreadsheet format you wish to create from values supplied by your input files.")
                dpg.add_text(bullet=True,default_value="2) Any number of Input Schema. For each input, we will aid you in creating a simple correspondence using TAGs") #, signifying which input columns correspond to which output columns.
                dpg.add_spacer(height=30)
                dpg.add_separator()
                dpg.add_text("We also provide you with two critical tools:")
                dpg.add_text(bullet=True,default_value="1) A Filename convention extractor, which allows you assign TAGs to consistently located slices of an inputfile's name.\n\tThis allows columns in the ouput to be populated by values not in the input columns.")
                dpg.add_text(bullet=True,default_value="2) A column operations handler, which allows you to perform transformations on TAGGED values before moving them to the output.")
                dpg.add_text(default_value="\tThese operations have two forms:")
                dpg.add_text(bullet=False,default_value="\tA) Simple arithmatic (+/-/*/÷) to either constants or user-supplied values that match other tags")
                dpg.add_text(bullet=False,default_value="\tB) Filtering through a correspondence list that you upload.")
               
                dpg.add_text(default_value="These can be things like custom departments, or store location codes, for example:")
                dpg.add_text(bullet=True,default_value="{'Johnsons':'004', 'Google':'006', ...}")
                dpg.add_text(bullet=True,default_value="{'Maryland: 'XXY', 'Virginia','ZZB', ...}")
                
                dpg.add_separator()

                # dpg.add_text(bullet=True,default_value="\tFor each column in the output schema you will be able to specify a TAG")
                # dpg.add_text(bullet=True,default_value="\tIn the Filename convention extractor, you will also be able to specify which input columns correspond to which TAGs")
                # dpg.add_text(bullet=True,default_value="\tInstead of letting the input column populate directly to the output column, you can specify which correspondence list the input values must go through")
                

                #dpg.add_separator()
                #dpg.add_text("Converter process has two modes:")
                #dpg.add_text("\tchoosing the converter you want and then scanning for files whose NAMING CONVENTIONS\n\tmatches that found in the name slices saved below",bullet=True)
                #dpg.add_text("\tscannng for files and then, for each file, identifies which converts accept that file's NAMING CONVENTIONS",bullet=True)
                #dpg.add_separator()

                dpg.add_separator()
                dpg.add_text("Converter process has two modes:")
                dpg.add_text("\tchoosing the converter you want and then scanning for files from the specified folder.",bullet=True),
                dpg.add_text("\t\tIf a Filename Extractor is provided, whose NAMING CONVENTIONS\n\tmatches that found in the name slices saved below")
                dpg.add_text("\tscannng for files and then, for each file, identifies which Output Schemas accept that file's NAMING CONVENTIONS",bullet=True)
                dpg.add_text("This allows for both a 1:Many and a Many:1 ")
                dpg.add_text("*NOTE: While we do filter for NAMING CONVETIONS if given, we do not filter for INPUT HEADERS because this program enables users create NEW correspondence rubrics between INPUT<->OUTPUT schemas on the go.")

            with dpg.collapsing_header(label="Schemas",default_open=True):
                dpg.add_separator()
                with dpg.group() as self.schemaViewer:
                    pass

        self.loadSchemas()
        self.refreshSchemas()

    def loadSchemas(self):

        self.schemas = []

        for filename in os.listdir(default_schema_path):
            f = os.path.join(default_schema_path, filename)
            # checking if it is a file
            if os.path.isfile(f):

                try:
                    name,ext = f.split(".")

                    if ext == "schema":
                        self.schemas.append(get(f))
                except Exception as e:
                    print(f"Something wrong with file:{f}")
                    print(e)

        print(f"{len(self.schemas)} schema found!")

    def refreshSchemas(self):

        dpg.delete_item(self.schemaViewer,children_only=True)

        dpg.push_container_stack(self.schemaViewer)

        for i,s in enumerate(self.schemas):
            with dpg.group(horizontal=True):
                dpg.add_button(label="Delete",callback=self.deleteSchema,user_data=i)

                s.generate_mini(openeditor=self.openEditor)

    def deleteSchema(self,sender,app_data,user_data):

        index = user_data

        def back():
            dpg.delete_item(_pop)

        def proceed():

            s = self.schemas.pop(index)
            dpg.delete_item(s._id)
            self.refreshSchemas()
            back()

        with dpg.window(popup=True) as _pop:
            with dpg.group(horizontal=True):
                dpg.add_text(f"Are you sure you wish you delete ")
                dpg.add_input_text(default_value=f"{self.schemas[index].name}",enabled=False)
                dpg.add_text(f"?")
            dpg.add_button(label="Y",callback = proceed)
            dpg.add_button(label="N",callback = back)

    def openEditor(self,sender,app_data,user_data):
       
        _schema = user_data

        SchemaEditor(mainpage=self,schema=_schema)

    def setDirs(self,sender,app_data,user_data):

        DefaultPathing()

    def newBuild(self,sender,app_data,user_data):

        SchemaEditor(mainpage=self)

    def updateSettings(self,sender,app_data,user_data):
        
        # Supposed to be easy way to change values sent in from menu items.
        # I have new functionlity for this in my dataclasses in private git.

        #----------------------------------
        # a
        _label = dpg.get_item_label(sender).lower() # some times the label itself has the secret!
        self.settings[_label] = app_data

        #----------------------------------
        # b
        # self.reversed_alt_settings: dict    = {_tut:self.tutorials}
        self.alt_settings[sender] = app_data

        #----------------------------------
        # c
        # self.dc_settings: dict    = {_tut:self.settings_dc.tutorials}
        self.dc_settings[sender] = app_data
        
        #----------------------------------
        # d
        # only if the label is equal to the field name!
        setattr(self.settings_dc_instance,_label,app_data)
        #----------------------------------
        # Save as pickle
        set(self.settingsName,self.settings)


def main():
   
    MainPage()

    dpg.create_viewport(title='Custom Title', width=1300, height=900)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__=="__main__":
    main()