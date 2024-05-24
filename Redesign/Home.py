

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

from Rubric_Builder import RubricControl

default_settings_path = "Redesign\\Settings"


class FileFormatter(DPGStage):

    # CHOOSE DESIRED OUTPUT FIRST
    # THEN DISPLAY INCOMMING FORMAT and ASK FOR CORRELATION TABLE; CREATE IF NOT EXIST; DISPLAY IF EXIST; LET EDIT
    
    # LATER, UPON LOAD, WHEN VERIFYING A TABLE WITH THAT SCHEMA, CAN SUGGEST OR EVEN AUTO-RUN FORMATTER
    #   BUT THIS NEEDS TO ASK IF 
    tutorials: bool  = False

    height: int  = 240
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
        
        with dpg.window(height=self.height,width=self.width) as self._id:

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


            with dpg.child_window(height=180,width=self.width-20):
                dpg.add_text("""This program builds and saves file formatters.\n
When creating new formatters, you are picking an input and an output format.\n
These will be represented best as columns in a spreadsheet, or a table schema.\n
\tAlthough this program can support a 1 to Many file converter format, it will be most effecient\n
\tto instead presuppose a Many to 1 conversion. That is, messy files being standardized.\n
Each format will have within it saved micro-formats that identify and save where a file is coming in from.
       """)

    def setDirs(self,sender,app_data,user_data):

        DefaultPathing()

    def newBuild(self,sender,app_data,user_data):

        RubricControl()

    def updateSettings(self,sender,app_data,user_data):
        
        _label = dpg.get_item_label(sender).lower()
        self.settings[_label] = app_data

        set(self.settingsName,self.settings)


def main():
   
    FileFormatter()

    dpg.create_viewport(title='Custom Title', width=1300, height=670)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__=="__main__":
    main()