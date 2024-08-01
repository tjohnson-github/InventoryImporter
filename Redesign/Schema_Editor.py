


import dearpygui.dearpygui as dpg
from dataclasses import dataclass, field,asdict,fields
import pyodbc
import os
import CustomPickler

from DPGStage import DPGStage
from DefaultPathing import DefaultPathing,DefaultPaths
import asyncio
from typing import Optional
from File_Selector import FileSelector
from File_Operations import csv_to_list,excel_to_list,mkdirWrapper

from CustomPickler import get,set
from Schema_Extractor_FilenameConvention import FilenameConvention,FilenameExtractorManager,FilenameExtractor,setFixer
from Schema_Extractor_DirnameConvention import DirnameConvention,DirnameExtractor,setFixer

import time
import Schema_Loader

from Rubric_Editor import RubricEditor

from Schema import Schema

default_settings_path = "Redesign\\Settings"
default_schema_path = "Redesign\\Schemas"


class SchemaEditor(DPGStage):

    label="Build Schema and add Input Rubrics"
    height       =  800
    width        =  1000
    spacer_width =  25

    items = {
        "Existing":Schema_Loader.SchemaFromBuilder,
        "Custom":Schema_Loader.SchemaFromBuilder,
        "From SQL":Schema_Loader.SchemaFromSQL,
        "From Spreadsheet File":Schema_Loader.SchemaFromFile
        }
    chosen = False

    scannableLocations = ["INPUT","STAGED"]

    schemaLoader: Schema_Loader.SchemaLoader

    def main(self,**kwargs):

        self.mainpage = kwargs.get("mainpage")
        self.schema = kwargs.get("schema",Schema())

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
                                    callback=self.openRubricEditor)

                        with dpg.group(horizontal=True):
                            dpg.add_text("*",color=(255,0,0))
                            dpg.add_text("Required")
                    
                    #with dpg.group(horizontal=True):
                    #    dpg.add_spacer(width=self.spacer_width)

            with dpg.collapsing_header(default_open=True,label="Input Directory Tag Extractor"):

                #============================================================================================
                # find a way to let extractors be None to equate not being in use::::
                '''if not self.schema.dirnameConvention:

                    self.dns = DirnameExtractor(color=dpg.get_value(self.color),editor=self)

                    dpg.configure_item(self.dns.doNOtUse,default_value=True)
                    self.dns.hide(sender=self.dns.doNOtUse,app_data=True)

                else: '''
                self.dns = DirnameExtractor(color=dpg.get_value(self.color),editor=self,dirnameConvention=self.schema.dirnameConvention)
                #============================================================================================
            with dpg.collapsing_header(default_open=True,label="Input File Tag Extractor"):
                self.fns = FilenameExtractorManager(color=dpg.get_value(self.color),editor=self,filenameConventions=self.schema.filenameConventions)

            with dpg.collapsing_header(default_open=True,label="Schema Editor"):
                #with dpg.group(horizontal=True):
                    #dpg.add_spacer(width=self.spacer_width)
                with dpg.group():
                    self.chooser = dpg.add_combo(items=[key for key,val in self.items.items()],default_value=[key for key,val in self.items.items()][0],label="Select how you want to build your converter schema.",callback=self.chooserCallback,width=140)
                    dpg.add_separator()
                    with dpg.group() as self.schemaGroup: 
                        self.schemaLoader = self.items["Custom"](schema=self.schema,filenameExtractorManager = self.fns,dirnameExtractor = self.dns)#,color=dpg.get_value(self.color))
  
    def changeColor(self,sender,app_data):
        
        def propColors(sender,app_data):

            _newColor = tuple(i*255 for i in app_data)

            dpg.configure_item(self.color,default_value=_newColor)
            dpg.configure_item(self.fns.color,default_value=_newColor)
            dpg.configure_item(self.dns.color,default_value=_newColor)
            dpg.configure_item(self.schemaLoader.colEditor.color,default_value=_newColor)

            self.schema.color = _newColor

        with dpg.window(popup=True):
            dpg.add_color_picker(
                no_small_preview=False,
                no_side_preview = True,
                callback=propColors)
        
             
    def saveSchema(self):
        #+=========================================
        # Base check:
        if dpg.get_value(self.nameInput)=="":
            with dpg.window(popup=True): dpg.add_text("Name not selected!")
            return
        #+=========================================
        # GATHER DIRNAME CONVENTIONS
        #self.dirnameConvention=None
        #if not dpg.get_value(self.dns.doNOtUse):
        _dncs = self.dns.attemptToSave()
        self.dirnameConvention = _dncs

        #+=========================================
        # GATHER FILENAME CONVENTIONS
        self.filenameConventions=[]
        if not dpg.get_value(self.fns.doNOtUse):
            _fncs = self.fns.attemptToSave()
            if not _fncs:
                pass

            self.filenameConventions = _fncs
        #+=========================================
        schema_dict = {}

         #"Column Name",
         #"Tag",
         #"Necessary?",
         #"Derived from Filename?",
         #"Operations",
        
        # GATHER SCHEMA HERE
        for editorRow in self.schemaLoader.colEditor.rows:

            _items = list(dpg.get_values(editorRow.items))

            #+--------------------------------------------------------
            if editorRow.name == "Tag":
                _schema_tags = [x.rstrip() for x in _items]
            elif editorRow.name == "Column Name":
                _schema_cols = [x.rstrip() for x in _items]
            #+--------------------------------------------------------
            schema_dict.update({editorRow.name:_items})

        #+=============================================================
        # BUILD RUBRIC
        _r = Schema(
             name               =   dpg.get_value(self.nameInput),
             desc               =   dpg.get_value(self.desc),
             color              =   dpg.get_value(self.color),
             filenameConventions=   self.filenameConventions,
             dirnameConvention  =   self.dirnameConvention,

             outputSchemaDict   =   schema_dict,
             rubrics            =   {}
        )

        #+=============================================================
        # Save
        mkdirWrapper(default_schema_path)
        _r.save(path=default_schema_path)
        #+=============================================================
        # Refresh mainpage

        try: # to replace the old one if it exists
            _old_schema = self.mainpage.schemas[self.mainpage.schemas.index(self.schema)]
            
            if _old_schema.saveName != _r.saveName:
                os.remove(_old_schema.saveName)
                print(f"{_old_schema.saveName} Removed!")

            self.mainpage.schemas[self.mainpage.schemas.index(self.schema)] = _r
            print(f"{_r.saveName} Added!")

        except Exception as e:
            print(e)
            self.mainpage.schemas.append(_r) 

        self.mainpage.refreshSchemas()
        self.schema = _r
        #+=============================================================
        # Close this window
        dpg.delete_item(self._id)

    def openRubricEditor(self):
        self.saveSchema()
        self.testSchema = RubricEditor(schema=self.schema)

    def chooserCallback(self,sender,app_data,user_data):

        def filterChoice(sender,app_data,user_data):

            try:
                self.deletePopup(sender,app_data,user_data)
            except:
                # does not yet exist
                pass

            dpg.delete_item(self.schemaGroup,children_only=True)
            dpg.push_container_stack(self.schemaGroup)

            self.schemaLoader = self.items[user_data](filenameExtractor = self.fns,dirnameExtractor = self.dns,color=dpg.get_value(self.color))

            self.chosen = True

        if self.chosen:
            with dpg.window(popup=True,width=300,height=50) as self.confirmationPopup:
                dpg.add_text("Are you sure? This will reset your current schema.")
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Yes",callback=filterChoice,user_data=app_data)
                    dpg.add_spacer(width=30)
                    dpg.add_button(label="No",callback=self.deletePopup)
        else:
            filterChoice(sender,app_data,user_data=app_data)

    def deletePopup(self,sender,app_data,user_data):
        dpg.delete_item(self.confirmationPopup)

    