

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
from dataclasses import dataclass, field,asdict
import pyodbc
import os

import CustomPickler

from SQLInterface import SQLLinker
from DPGStage import DPGStage
from Settings_DefaultPathing import DefaultPathing,DefaultPaths
import asyncio

from File_Selector import FileSelector
from File_Operations import csv_to_list,excel_to_list
from CustomPickler import get,set

from Schema_Editor import SchemaEditor
from Schema import Schema

from dataclasses import dataclass
import fnmatch

from Vendorfile import InputFile
from JSONtoDataclass import DataManager 

from Settings_General import SettingsManager, Settings

default_settings_path = "Redesign\\Settings"  
default_schema_path = "Redesign\\Schemas"


@dataclass
class UserDataJSON:
    secondary_callback: callable
    on_close: callable
    after_good: callable
    after_bad: callable


class MainPage(DPGStage):

    label="Johnson's Consulting VendorFile Conversion Manager"

    # CHOOSE DESIRED OUTPUT FIRST
    # THEN DISPLAY INCOMMING FORMAT and ASK FOR CORRELATION TABLE; CREATE IF NOT EXIST; DISPLAY IF EXIST; LET EDIT
    
    # LATER, UPON LOAD, WHEN VERIFYING A TABLE WITH THAT SCHEMA, CAN SUGGEST OR EVEN AUTO-RUN FORMATTER
    #   BUT THIS NEEDS TO ASK IF 

    height: int  = 500
    width: int   = 830

    settingsName = f'{default_settings_path}\\generalSettings.txt'

    '''@dataclass
    class Settings:
        tutorials: bool = False
        setDefaultFirst: bool = False'''

    def main(self,**kwargs):
    
        #self.settings_dc_instance = SettingsManager.getSettings()# Settings() # default on arrival

        '''def loadSettings():
            try:

                for field in SettingsManager.getSettings():

                #settingsDict = get(self.settingsName)

                #print(settingsDict)

                #for key,val in settingsDict.items():
                    #self.settings[key]=val
                #    setattr(self.settings_dc_instance,key,val)
            except Exception as e:
               print ("Probably doesnt exist yet:\t",e)'''

        #loadSettings()

    '''@classmethod
    def getSettings(cls):

        return get(cls.settingsName)'''

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

                with dpg.menu(label="Data"): 
                    dpg.add_menu_item(label="Manage User Data",callback=self.manageData)

                with dpg.menu(label="View"):
                    dpg.add_checkbox(label="Pick Me", callback=self.print_me)
                    dpg.add_button(label="Press Me", callback=self.print_me)
                    dpg.add_color_picker(label="Color Me", callback=self.print_me)

                with dpg.menu(label="Help"):
                    _tut = dpg.add_checkbox(label="Tutorials",default_value = getattr(SettingsManager.getSettings(),"tutorials",True),callback=SettingsManager.updateSettings,user_data="tutorials")
                    
                    #self.alt_settings: dict    = {_tut:self.tutorials}
                    #self.dc_settings: dict    = {_tut:self.settings_dc_instance.tutorials}

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

            
            def bringAttentionToDirectories():

                paths = DefaultPathing.getPaths()

                pathingVals = list(asdict(paths).values())

                def hide_if_dirs():
                    if [os.path.exists(path) for path in pathingVals].count(False)==0:
                        dpg.delete_item(self.dirAttention)

                # If they do not exist: 
                if [os.path.exists(path) for path in pathingVals].count(False)>0:
                    with dpg.group() as self.dirAttention:
                        dpg.add_separator()
                        dpg.add_text("~~~~~ Attention ~~~~~")
                        dpg.add_text("This program has a particular file system you will need to grow accustomed to.")
                        dpg.add_text("It requires folders for")
                        dpg.add_text("pre-processed input files",bullet=True)
                        dpg.add_text("post-processed files",bullet=True)
                        dpg.add_text("the desired output files",bullet=True)
                        dpg.add_text("as well as a staging folder where you can verify things are okay between processing steps.",bullet=True)
                        dpg.add_separator()
                        dpg.add_button(label="Take me to the Default Directory Organizer",callback=self.setDirs)
                        dpg.add_text("\tOR")
                        dpg.add_button(label="Make the defaults and explore later.",callback=paths.makeDirectories,user_data=hide_if_dirs)
                        dpg.add_text("This option will be available under 'File>Set Default Directories' at any time.")
                        dpg.add_separator()

            bringAttentionToDirectories()

            with dpg.collapsing_header(label="Schemas",default_open=True):
                dpg.add_separator()
                with dpg.group(horizontal=True):
                    _scanAll = dpg.add_button(label="Scan\nAll",width=30,callback=self.beginScan)
                    with dpg.tooltip(_scanAll): dpg.add_text("Scan all input folders and generate outputs for each schema and rubric below")
                    Schema.generate_key()
                with dpg.group() as self.schemaViewer:
                    pass

        self.loadSchemas()
        self.refreshSchemas()
        dpg.set_item_user_data(_scanAll,self.schemas)

    def manageData(self,sender):

        DataManager(mainpage=self)

    def loadSchemas(self):

        self.schemas = []

        for filename in os.listdir(default_schema_path):
            f = os.path.join(default_schema_path, filename)

            if os.path.isfile(f):

                try:
                    name,ext = f.split(".")

                    if ext == "schema":
                        self.schemas.append(get(f))
                except Exception as e:
                    print(f"Something wrong with file:{f}")
                    print(e)

    def refreshSchemas(self):

        # Called when there are changes to any schemas, so we need to re-render them all; some with new info, many with the same info

        # Reset parent
        dpg.delete_item(self.schemaViewer,children_only=True)
        dpg.push_container_stack(self.schemaViewer)

        # Display the mini schemas
        for i,s in enumerate(self.schemas):
            with dpg.group(horizontal=True) as _:

                dpg.add_button(label="S\nC\nA\nN",user_data=[s],height=Schema.height,width=30,callback=self.beginScan)
                s.generate_mini(openeditor=self.openSchemaEditor,deleteSchema=self.deleteSchema,index=i)
            dpg.push_container_stack(self.schemaViewer)


    def beginScan(self,sender,app_data,user_data):
        
        schemas_selected:list = user_data


        print("============================")
        print(f"Scanning: {[x.name for x in schemas_selected]}")
        print("============================")
        #print (DefaultPathing.getPaths())

        paths = DefaultPathing.getPaths()
        #print (paths.input)

        if not os.path.exists(paths.input):
            with dpg.window(popup=True):
                dpg.add_text(f"'{paths.input}' not found!\nAre you sure your directories exist?")
                dpg.add_button(label="Go to Defult Directory Manager",callback=self.setDirs)
            return
        # Show errors if default paths do not exist!
        # make the paths upon start 

        '''
            2. check to make sure the file extensions match the schema

            3. for each of them, display similarly to the RUBRIC IMPORTER:
               the tag/name preview 

            4. if a new file type: make a button that opens the editor
                AND saves it to schema
                AND applies the rules immediately to that run through.
        '''

        inputFileObjs = []

        def getFiles(allowedExtensions=["xlsx","csv"]):

            # generates a list of scanned files as vendorfile.py objects to be attached per schema
            # check to make sure the file extensions match the schema

            _files = []

            for extension in allowedExtensions:
                _to_process = fnmatch.filter(os.listdir(paths.input), f'*.{extension}')
                
                for file in _to_process:
                    _files.append(InputFile(f'{paths.input}\\{file}'))

            #====================================================
            #pdf_files_to_process    =   fnmatch.filter(os.listdir(pathingDict['input_filepath']), '*.pdf') if automatePDF else []
   
            #for file in pdf_files_to_process:
            #    print (f'Cannot convert {file} to CSV in the same step as processing CSVs.\tPDFs too often require manual validation.')
            #====================================================
            return _files


        #====================================================
        filesToProcessDict={}
        #====================================================
        for schema in schemas_selected:
            #print(f"Schema:\t{schema.name}")

            if not schema.filenameConventions:
                print("No filename conventions found; attaching all files to this schema's editing process")
                filesToProcessDict.update({schema.name:getFiles()})
            else:

                # maybe it is silly to have more than 1 filename convention per schema....
                filesToProcessDict.update({schema.name:getFiles(allowedExtensions=schema.filenameConventions[0].supportedExtensions)})

                for fnc in schema.filenameConventions:
                    #print (f"{fnc.name}")
                    print(f'Filename Convention Found!')
                    print(f'Supported Input Extensions: {fnc.supportedExtensions}')
        #====================================================

        #====================================================
        # Now generate the window!!!

        from Converter_SchemaFiddler_Window import FiddlerWindow

        FiddlerWindow(schemas=schemas_selected,filesToProcessDict=filesToProcessDict)

 

    def deleteSchema(self,sender,app_data,user_data):

        # Displays a popup to confirm if you really want to delete the schema @ index <user_data>

        index = user_data

        def back():
            dpg.delete_item(_pop)

        def proceed():

            s = self.schemas.pop(index)
            dpg.delete_item(s._id)
            self.refreshSchemas()
            
            os.remove(s.saveName)

            back()

        with dpg.window(popup=True) as _pop:
            with dpg.group():
                dpg.add_text(f"Are you sure you wish you delete ")
                
                with dpg.group(horizontal=True):
                    dpg.add_input_text(default_value=f"{self.schemas[index].name}",enabled=False)
                    dpg.add_text(f"?")
            
                dpg.add_separator()

                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=40)
                    dpg.add_button(label="Yes",callback = proceed)
                    dpg.add_button(label="No",callback = back)

    def openSchemaEditor(self,sender,app_data,user_data):
       
        _schema = user_data

        # delete previous schemas????

        self.sss = SchemaEditor(mainpage=self,schema=_schema)

    def setDirs(self,sender,app_data,user_data):

        DefaultPathing(mainPage = self)

    def newBuild(self,sender,app_data,user_data):

        SchemaEditor(mainpage=self)

    '''def updateSettings(self,sender,app_data,user_data):
        
        settingName = user_data

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
        setattr(self.settings_dc_instance,user_data,app_data)
        #----------------------------------
        #----------------------------------
        # Save as pickle
        
        try:
            set(self.settingsName,self.settings_dc_instance)
            print("saved")
            with dpg.window(popup=True): dpg.add_text("Settings Updated!")
        except Exception as e:
            with dpg.window(popup=True): dpg.add_text(f"Settings Failed to Update!\nError:\t{e}")'''
        



def main():
   
    MainPage()

    dpg.create_viewport(title='Custom Title', width=1300, height=900)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__=="__main__":
    main()