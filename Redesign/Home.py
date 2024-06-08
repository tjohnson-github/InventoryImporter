

##### WHAT HAPPENS IF THERE ARE 2 RUBRICS
### WITH THE SAME INPUT SCHEMA, BUT DIFFERENT NAMES?




import dearpygui.dearpygui as dpg
dpg.create_context()
from dataclasses import dataclass, field
import pyodbc

import CustomPickler

from SQLInterface import SQLLinker
from DPGStage import DPGStage
from DefaultPathing import DefaultPathing,DefaultPaths
import asyncio

from File_Selector import FileSelector
from File_Operations import csv_to_list,excel_to_list
from CustomPickler import get,set

from Schema_Editor import SchemaEditor

default_settings_path = "Redesign\\Settings"


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
    settings: dict = {"tutorials":False}

    def print_me(sender):
        print(f"Menu Item: {sender}")

    def loadSettings(self):
        try:
            settingsDict = get(self.settingsName)
            for key,val in settingsDict.items():
                self.settings[key]=val
        except Exception as e:
           print ("Probably doesnt exist yet:\t",e)

    def main(self,**kwargs):
    
        self.loadSettings()

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
                    _ = dpg.add_checkbox(label="Tutorials",default_value = self.settings["tutorials"],callback=self.updateSettings)

            dpg.add_text("Welcome to our Many:One EZ Spreadsheet Converter")
            with dpg.child_window(height=500):
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


    def setDirs(self,sender,app_data,user_data):

        DefaultPathing()

    def newBuild(self,sender,app_data,user_data):

        SchemaEditor()

    def updateSettings(self,sender,app_data,user_data):
        
        _label = dpg.get_item_label(sender).lower()
        self.settings[_label] = app_data

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