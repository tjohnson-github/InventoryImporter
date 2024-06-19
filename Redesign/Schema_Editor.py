

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
from File_Operations import csv_to_list,excel_to_list,mkdirWrapper


from CustomPickler import get,set
from FilenameConventionExtractor import FilenameExtractor,FilenameConvention,DirnameExtractor,DirnameConvention,setFixer



default_settings_path = "Redesign\\Settings"
default_schema_path = "Redesign\\Schemas"

import time

import Schema_Loader

@dataclass
class Rubric:
    name: str
    description: str
    color: tuple
    col_to_tag_correspondence: dict

@dataclass
class Schema:
    name: str = ''
    desc: str = ''
    color: tuple = (0,0,0,0)
    outputSchemaDict: dict[str:any] =  field(default_factory=lambda: {})
    rubrics: dict[str:dict] = field(default_factory=lambda: {}) # Name_of_RUBRIC
    filenameConventions: list[FilenameConvention] = field(default_factory=lambda: [])
    dirnameConvention: DirnameConvention = field(default_factory=lambda: [])

    height = 100

    def generate_mini(self,openeditor: callable):
        with dpg.child_window(height=self.height) as self._id:

            with dpg.group(horizontal=True):
                dpg.add_color_button(label=f"{self.name}'s Color",default_value=self.color,height=self.height-16,width=50)
                with dpg.group():
                    dpg.add_input_text(label="Name",default_value=self.name,enabled=False,width=200)
                    dpg.add_input_text(label="Subtitle",default_value=self.desc,enabled=False,width=200)
                    #dpg.add_input_text(label="Name",default_value=self.name,enabled=False)
                with dpg.group():
                    dpg.add_button(label="Edit",callback=openeditor,user_data=self)



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
    dirnameConvention: DirnameConvention

    schemaLoader: Schema_Loader.SchemaLoader

    def main(self,**kwargs):

        self.mainpage = kwargs.get("mainpage")
        self.schema = kwargs.get("schema",Schema())
        # NEED TO ALSO DO THIS FOR THE CONVENTIONS!!!

    def generate_id(self,**kwargs):
        with dpg.window(label=self.label,width=self.width,height=self.height) as self._id:

            with dpg.group():

                dpg.add_separator()

                with dpg.group(horizontal=True):
                    with dpg.group():
                        with dpg.group(horizontal=True):
                            self.nameInput = dpg.add_input_text(label="Name of Schema",width=300,default_value=self.schema.name)
                            dpg.add_text("*",color=(255,0,0))
                        self.desc = dpg.add_input_text(label="Description",width=300,height=80,multiline=True,default_value=self.schema.desc)
                        with dpg.group(horizontal=True):
                            self.color = dpg.add_color_button(width=300,callback=self.changeColor,default_value=self.schema.color)
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

            with dpg.collapsing_header(default_open=True,label="Input Directory Tag Extractor"):
                self.dns = DirnameExtractor(color=dpg.get_value(self.color),editor=self)

            with dpg.collapsing_header(default_open=True,label="Input File Tag Extractor"):
                self.fns = FilenameExtractor(color=dpg.get_value(self.color),editor=self)

            with dpg.collapsing_header(default_open=True,label="Schema Editor"):
                #with dpg.group(horizontal=True):
                    #dpg.add_spacer(width=self.spacer_width)
                with dpg.group():
                    self.chooser = dpg.add_combo(items=[key for key,val in self.items.items()],default_value=[key for key,val in self.items.items()][0],label="Select how you want to build your converter schema.",callback=self.chooserCallback,width=140)
                    dpg.add_separator()
                    with dpg.group() as self.schemaGroup: 
                        self.schemaLoader = self.items["Custom"](filenameExtractor = self.fns,dirnameExtractor = self.dns,color=dpg.get_value(self.color))
  
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
        dpg.configure_item(self.dns.color,default_value=_newColor)
        dpg.configure_item(self.schemaLoader.colEditor.color,default_value=_newColor)

        #self.color = _newColor

    def saveSchema(self):

        # Base check:
        if dpg.get_value(self.nameInput)=="":
            with dpg.window(popup=True): dpg.add_text("Name not selected!")
            return

        # GATHER DIRNAME CONVENTIONS
        self.dirnameConvention=None
        if not dpg.get_value(self.dns.doNOtUse):
            _dncs = self.dns.attemptToSave()
            self.dirnameConvention = _dncs


        # GATHER FILENAME CONVENTIONS
        self.filenameConventions=[]
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
        for editorRow in self.schemaLoader.colEditor.rows:
            if editorRow.name == "Tag":

                _tempItems = [x.rstrip() for x in list(dpg.get_values(editorRow.items))]
                #print(_tempItems)
                #print(f"GETTING _tempItems:: {_tempItems}")
                #_tempItems = set()

                _setted = setFixer(_tempItems)

                schema_dict.update({editorRow.name:_setted})
            else:
                schema_dict.update({editorRow.name:list(dpg.get_values(editorRow.items))})

        # BUILD RUBRIC
        _r = Schema(
             name               =   dpg.get_value(self.nameInput),
             desc            =   dpg.get_value(self.desc),
             color              =   dpg.get_value(self.color),
             filenameConventions=   self.filenameConventions,
             dirnameConvention  =   self.dirnameConvention,

             outputSchemaDict   =   schema_dict,
             rubrics            =   {}
        )


        self.schema = _r

        mkdirWrapper(default_schema_path)

        set(f'{default_schema_path}\\{_r.name}.schema',_r)
        self.mainpage.refreshSchemas()

    def goToTestSchema(self):
        # okay here it is
        # give ability to make multiple compatible conventions?
        #self.schema = self.saveSchema()
        self.saveSchema()
        # NOW you need to EDIT AND SAVE RUBRICS
        self.testSchema = TestSchema(schema=self.schema)
        dpg.delete_item(self._id)

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

        self.schemaLoader = self.items[user_data](filenameExtractor = self.fns,dirnameExtractor = self.dns,color=dpg.get_value(self.color))

        self.chosen = True

class TestSchema(DPGStage):

    label="Test Adding a Rubric"

    height = 500
    width=1000

    schema: Schema

    names: list[str]
    items: list[int]

    null_item = '~'

    def main(self,**kwargs):

        self.schema=kwargs.get("schema")
        self.allSupportedinputTypes = []
        if self.schema.filenameConventions:
            for fnc in self.schema.filenameConventions:
                self.allSupportedinputTypes.extend(fnc.supported_extensions)
        
        # TAGS
        _uncleanedTags = self.schema.outputSchemaDict["Tag"]
        _cleanedTags = [t for t in _uncleanedTags if t!=""]
        self.tags = _cleanedTags
        self.tags.insert(0,self.null_item)

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

    def changeColor(self,sender,app_data):
        
        with dpg.window(popup=True):
            dpg.add_color_picker(
                no_small_preview=False,
                no_side_preview = True,
                callback=self.propColors)
             
    def propColors(self,sender,app_data):

        _newColor = tuple(i*255 for i in app_data)
        dpg.configure_item(self.color,default_value=_newColor)


    def generateCells(self):
        
        with dpg.group(horizontal=True):
            dpg.add_text("Adding an Input File to the Rubric: ")
            dpg.add_input_text(default_value=self.schema.name,enabled=False)
        dpg.add_separator

        with dpg.group(horizontal=True):
            with dpg.group():
                with dpg.group(horizontal=True):
                    self.nameInput = dpg.add_input_text(label="Name of Rubric",width=150)
                    dpg.add_text("*",color=(255,0,0))
                self.desc = dpg.add_input_text(label="Description",width=150,height=80,multiline=True)
                with dpg.group(horizontal=True):
                    _c = dpg.add_color_button(width=50,default_value=self.schema.color,enabled=False)
                    with dpg.tooltip(_c): dpg.add_text(f"{self.schema.name}'s Color")
                    self.color = dpg.add_color_button(width=92,default_value=randomColor(),callback=self.changeColor)
                    with dpg.tooltip(self.color): dpg.add_text(f"This Rubric's Color")
                    dpg.add_text("Color")
            with dpg.group():
                dpg.add_button(label="Save",callback=self.addRubricToSchema)
            #self.scansFrom = dpg.add_combo(label="Scans From",items = self.scannableLocations,default_value=self.scannableLocations[0],width=300)
        dpg.add_separator()


        dpg.add_combo(items=self.tags)
        self.suggest = dpg.add_checkbox(label="Suggest Tags based on Input?",default_value=True)
        dpg.add_separator

        dpg.add_button(label="Load File",callback=self.loadFile) 
        # can also build from scratch like before:::
        # make a decoupled column editor??
        dpg.add_separator()
        
        with dpg.child_window(border=False,horizontal_scrollbar=True) as self.rubricEditor:
            pass

    def addRubricToSchema(self):

        _names = dpg.get_values(self.names)
        _items = dpg.get_values(self.items)
        print("<><><><><><><>")
        print(_names)
        print(_items)
        print("<><><><><><><>")
        for x in _items:
            if x==self.null_item: x = "" 

        _col_to_tag_correspondence = dict(zip(self.names,_items))

        print(_col_to_tag_correspondence)

        _rubric = Rubric(
            name        =   dpg.get_value(self.nameInput),
            description =   dpg.get_value(self.desc),
            color       =   dpg.get_value(self.color),
            col_to_tag_correspondence = _col_to_tag_correspondence
            )

    def loadFile(self):

        def manipulateFile():

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


        if self.allSupportedinputTypes:
            self.fs = FileSelector(
                label="Load Spreadsheet file to begin column correspondence with desired output schema",
                nextStage=manipulateFile,
                inputTypes = self.allSupportedinputTypes)
        else:
            self.fs = FileSelector(
                label="Load Spreadsheet file to begin column correspondence with desired output schema",
                nextStage=manipulateFile)

  
    def populateCols(self,readArray):

        header = readArray.pop(0)    
        rows = readArray
            
        dpg.push_container_stack(self.rubricEditor)

        with dpg.group(horizontal=True) as headerGroup:
            dpg.add_text("Imported File Header:")
            dpg.add_spacer(width=20)
            dpg.add_text("|")

        with dpg.group(horizontal=True) as TagGroup:
            dpg.add_text("Available Tags ::::::")
            dpg.add_spacer(width=20)
            dpg.add_text("|")

        self.names = []
        self.items = []

        for colName in header:

            component_width=8*len(f"{colName}")
            if component_width < 50: component_width+=40
            
            _name = dpg.add_input_text(default_value=f"{colName}", readonly=True,parent=headerGroup,width=component_width)
            self.names.append(_name)

            with dpg.group(horizontal=True,parent=headerGroup):
                dpg.add_spacer(width=20)
                dpg.add_text("|")
                dpg.add_spacer(width=20)

            default_tag = self.tags[0]

            if self.suggest:
                if colName in self.tags:
                    default_tag = self.tags[self.tags.index(colName)]
                else:
                    pass
                    # do other suggest mechanics here
    
            _combo = dpg.add_combo(items=self.tags,default_value = default_tag,parent=TagGroup,width=component_width)
            self.items.append(_combo)

            with dpg.group(horizontal=True,parent=TagGroup):
                dpg.add_spacer(width=20)
                dpg.add_text("|")
                dpg.add_spacer(width=20)