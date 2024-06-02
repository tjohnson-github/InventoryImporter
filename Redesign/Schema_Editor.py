

import dearpygui.dearpygui as dpg
dpg.create_context()
from dataclasses import dataclass, field
import pyodbc

import CustomPickler

from DPGStage import DPGStage
from DefaultPathing import DefaultPathing,DefaultPaths
import asyncio
from typing import Optional
from File_Selector import FileSelector
from File_Operations import csv_to_list,excel_to_list


from CustomPickler import get,set
from FilenameConventionExtractor import FilenameExtractor,FilenameConvention

default_settings_path = "Redesign\\Settings"

import time

import Schema_Loader

@dataclass
class Rubric:
    name: str
    subname: str
    col_to_tag_correspondence: dict
    color: tuple

@dataclass
class Schema:
    name: str
    subname: str
    color: tuple
    outputSchemaDict: dict[str:any]
    rubrics: dict[str:dict] # Name_of_RUBRIC
    filenameConventions: list[FilenameConvention]

@dataclass
class DesiredFormat:
    name: str
    headersAKAColumns: list[str]
    correspondenceDict: dict
    # will be something like:
    # { column1: 1, column2: 2, ...
    #   or
    # { column1: IMPORTANTCONCEPT1, column4: IMPORTANTCONCEPT2, ...

import random
def randomColor():
    r = random.randrange(0,255)
    g = random.randrange(0,255)
    b = random.randrange(0,255)
    y = random.randrange(0,255)

    return (r,g,b,y)


class SchemaEditor(DPGStage):

    label="Build Schema and add Input Rubrics"

    height=800
    width=1000
    spacer_width = 25

    items = {
        "Custom":Schema_Loader.SchemaFromScratch,
        "From SQL":Schema_Loader.SchemaFromSQL,
        "From Spreadsheet File":Schema_Loader.SchemaFromFile
        }
    chosen = False

    scannableLocations = ["INPUT","STAGED"]

    filenameConventions: list[FilenameConvention]

    schemaEditor: Schema_Loader.SchemaLoader

    def generate_id(self,**kwargs):
        with dpg.window(label=self.label,width=self.width,height=self.height):

            with dpg.group():

                dpg.add_separator()

                with dpg.group(horizontal=True):
                    with dpg.group():
                        with dpg.group(horizontal=True):
                            self.nameInput = dpg.add_input_text(label="Name of Schema",width=300)
                            dpg.add_text("*",color=(255,0,0))
                        self.desc = dpg.add_input_text(label="Description",width=300,height=80,multiline=True)
                        with dpg.group(horizontal=True):
                            self.color = dpg.add_color_button(width=300,default_value=randomColor(),callback=self.changeColor)
                            dpg.add_text("Color")
                        self.scansFrom = dpg.add_combo(label="Scans From",items = self.scannableLocations,default_value=self.scannableLocations[0],width=300)

                    #with dpg.collapsing_header(default_open=False,label="Tutorial"):
                    with dpg.group():
                        with dpg.child_window(height=120):
                            #with dpg.group(horizontal=True):
                                #dpg.add_spacer(width=self.spacer_width)
                            with dpg.group():
                                dpg.add_button(
                                    label="Save Schema and add input->output schema correspondence later.\nFiles will be considered for this converter based on filename conventions.",
                                    width=300,
                                    callback=self.saveSchema)

                                dpg.add_text("OR")

                                dpg.add_button(
                                    label="Load a file right now to begin adding input->output schema correspondence rubric",
                                    width=300,
                                    callback=self.goToTestSchema)
                        with dpg.group(horizontal=True):
                            dpg.add_text("*",color=(255,0,0))
                            dpg.add_text("Required")
                    
                    #with dpg.group(horizontal=True):
                    #    dpg.add_spacer(width=self.spacer_width)
            with dpg.collapsing_header(default_open=True,label="Input File Tag Extractor"):
                self.fns = FilenameExtractor(color=dpg.get_value(self.color),editor=self)

            with dpg.collapsing_header(default_open=True,label="Schema Editor"):
                #with dpg.group(horizontal=True):
                    #dpg.add_spacer(width=self.spacer_width)
                with dpg.group():
                    self.chooser = dpg.add_combo(items=[key for key,val in self.items.items()],default_value=[key for key,val in self.items.items()][0],label="Select how you want to build your converter schema.",callback=self.chooserCallback,width=140)
                    dpg.add_separator()
                    with dpg.group() as self.schemaGroup: 
                        self.schemaEditor = self.items["Custom"](filenameExtractor = self.fns,color=dpg.get_value(self.color))

            

           
    def changeColor(self,sender,app_data):
        
        with dpg.window(popup=True):
            dpg.add_color_picker(
                no_small_preview=False,
                no_side_preview = True,
                callback=self.propColors)
             
    def propColors(self,sender,app_data):

        _newColor = tuple(i*255 for i in app_data)

        dpg.configure_item(self.color,default_value=_newColor)
        dpg.configure_item(self.fns.color,default_value=_newColor)
        dpg.configure_item(self.schemaEditor.colEditor.color,default_value=_newColor)

    def saveSchema(self):

        # Base check:
        if dpg.get_value(self.nameInput)=="":
            with dpg.window(popup=True): dpg.add_text("Name not selected!")
            return

        self.filenameConventions=[]

        # GATHER FILENAME CONVENTIONS
        if not dpg.get_value(self.fns.doNOtUse):
            _fncs = self.fns.attemptToSave()
            if not _fncs:
                # There is no naming convention. Skipping rest of code
                return

            for fnc in _fncs:
                self.filenameConventions.append(fnc)

        schema_dict = {}

         #"Column Name",
         #"Tag",
         #"Necessary?",
         #"Derived from Filename?",
         #"Operations",

        # GATHER SCHEMA HERE
        for editorRow in self.schemaEditor.colEditor.rows:
            schema_dict.update({editorRow.name:dpg.get_values(editorRow.items)})

        # BUILD RUBRIC
        _r = Schema(
             name=dpg.get_value(self.nameInput),
             subname=dpg.get_value(self.desc),
             color = tuple(i*255 for i in dpg.get_value(self.color)),
             filenameConventions=self.filenameConventions,
             outputSchemaDict=schema_dict,
             rubrics={}
        )


        self.schema = _r

    def goToTestSchema(self):
        # okay here it is
        # give ability to make multiple compatible conventions?
        #self.schema = self.saveSchema()
        self.saveSchema()
        # NOW you need to EDIT AND SAVE RUBRICS
        self.testSchema = TestSchema(schema=self.schema)


    def saveRubric(self):

        self.filenameConvention = self.fns.attemptToSave()

    def chooserCallback(self,sender,app_data,user_data):

        if self.chosen:
            with dpg.window(popup=True,width=300,height=50) as self.confirmationPopup:
                dpg.add_text("Are you sure? This will reset your current schema.")
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Yes",callback=self.filterChoice,user_data=app_data)
                    dpg.add_spacer(width=30)
                    dpg.add_button(label="No",callback=self.deletePopup)
        else:
            self.filterChoice(sender,app_data,user_data=app_data)

    def deletePopup(self,sender,app_data,user_data):
        dpg.delete_item(self.confirmationPopup)

    def filterChoice(self,sender,app_data,user_data):

        print(user_data)
        try:
            self.deletePopup(sender,app_data,user_data)
        except:
            # does not yet exist
            pass

        dpg.delete_item(self.schemaGroup,children_only=True)
        dpg.push_container_stack(self.schemaGroup)

        self.schemaEditor = self.items[user_data](filenameExtractor = self.fns,color=dpg.get_value(self.color))

        self.chosen = True

class TestSchema(DPGStage):

    label="Test Adding a Rubric"

    height = 500
    width=1000

    schema: Schema

    def main(self,**kwargs):

        self.schema=kwargs.get("schema")
        self.allSupportedinputTypes = []
        if self.schema.filenameConventions:
            for fnc in self.schema.filenameConventions:
                self.allSupportedinputTypes.extend(supported_extensions)
        
        # TAGS
        _uncleanedTags = self.schema.outputSchemaDict["Tag"]
        _cleanedTags = [t for t in _uncleanedTags if t!=""]
        self.tags = _cleanedTags
        self.tags.insert(0,"~")

        _necessary = self.schema.outputSchemaDict["Necessary?"]
        print (zip(_uncleanedTags,_necessary))

    def generate_id(self,**kwargs):

        with dpg.window(height=self.height,width=self.width,label=self.label):

             self.generateCells()
             #"Column Name",
             #"Tag",
             #"Necessary?",
             #"Derived from Filename?",
             #"Operations",

    def generateCells(self):
        

        with dpg.group(horizontal=True):
            dpg.add_text("Adding an Input File to the Rubric: ")
            dpg.add_text(self.schema.name)
        dpg.add_separator
        with dpg.group():
            with dpg.group(horizontal=True):
                self.nameInput = dpg.add_input_text(label="Name of Rubric",width=300)
                dpg.add_text("*",color=(255,0,0))
            self.desc = dpg.add_input_text(label="Description",width=150,height=80,multiline=True)
            with dpg.group(horizontal=True):
                self.color = dpg.add_color_button(width=300,default_value=randomColor(),callback=self.changeColor)
                dpg.add_text("Color")
            self.scansFrom = dpg.add_combo(label="Scans From",items = self.scannableLocations,default_value=self.scannableLocations[0],width=300)
        dpg.add_separator


        dpg.add_combo(items=self.tags)
        self.suggest = dpg.add_checkbox(label="Suggest Tags based on Input?",default_value=True)
        dpg.add_separator
        dpg.add_button(label="Load File",callback=self.loadFile)
        dpg.add_text("Imported File Header")
        with dpg.child_window(border=False) as self.rubricEditor:
            pass

    def loadFile(self):

        if self.allSupportedinputTypes:
            self.fs = FileSelector(
                label="Load Spreadsheet file to begin column correspondence with desired output schema",
                nextStage=self.manipulateFile,
                inputTypes = self.allSupportedinputTypes)
        else:
            self.fs = FileSelector(
                label="Load Spreadsheet file to begin column correspondence with desired output schema",
                nextStage=self.manipulateFile)


    def populateCols(self,readArray):

        header = readArray.pop(0)    
        rows = readArray
            
        dpg.push_container_stack(self.rubricEditor)

        headerGroup = dpg.add_group(horizontal=True)
        TagGroup = dpg.add_group(horizontal=True)

        for item in header:

            component_width=8*len(f"{item}")
            
            dpg.add_input_text(default_value=f"{item}", readonly=True,parent=headerGroup,width=component_width)

            default_tag = self.tags[0]

            if self.suggest:
                if item in self.tags:
                    default_tag = self.tags[self.tags.index(item)]
                else:
                    pass
                    # do other suggest mechanics here
    
            dpg.add_combo(items=self.tags,default_value = default_tag,parent=TagGroup,width=component_width)


    def manipulateFile(self):

        dpg.delete_item(self.fs._id)
        _filepath = self.fs.selectedFile 

        readArray = []
        error = ''

        if _filepath[-3:] == 'csv':
            readArray,error = csv_to_list(_filepath)
        elif _filepath[-4:] == 'xlsx':
            readArray,error = excel_to_list(_filepath)

        if readArray:
            self.populateCols(readArray)
           

        else:
            with dpg.window(popup=True):
                dpg.add_text(error)