

import dearpygui.dearpygui as dpg
from dataclasses import dataclass, field,asdict
import pyodbc

import CustomPickler

from DPGStage import DPGStage,ObjTabPattern
from DefaultPathing import DefaultPathing,DefaultPaths
import asyncio
from typing import Optional
from File_Selector import FileSelector
from File_Operations import csv_to_list,excel_to_list,mkdirWrapper

from CustomPickler import get,set
from Schema_Extractor_FilenameConvention import FilenameConvention,FilenameExtractorManager,FilenameExtractor,setFixer
from Schema_Extractor_DirnameConvention import DirnameConvention,DirnameExtractor,setFixer

import time
from Rubric_Editor import RubricEditor


@dataclass
class Schema:
    #saveName: str = field(init= False)

    name: str = ''
    desc: str = ''
    color: tuple = (0,0,0,0)

    #schema_cols: list[str] = field(default_factory=lambda: [])
    #schema_tags: list[str] = field(default_factory=lambda: [])

    outputSchemaDict: dict[str:any] =  field(default_factory=lambda: {})

    rubrics: dict[str:dict] = field(default_factory=lambda: {}) # Name_of_RUBRIC
    filenameConventions: list[FilenameConvention] = field(default_factory=lambda: [])
    dirnameConvention: DirnameConvention = field(default_factory=lambda: DirnameConvention())

    height = 100


    def save(self,path):

        self.saveName = f'{path}\\{self.name}.schema'
        set(self.saveName,self)

    @classmethod
    def generate_key(cls):
        pass
        with dpg.child_window(height=int(cls.height/4)) as _key_id:
            
            with dpg.group(horizontal=True):

                dpg.add_color_button(label=f"Rubric Color",default_value=(0,0,0,0),height=dpg.get_item_height(_key_id)-16,width=50)

                with dpg.group():

                    dpg.add_input_text(
                        #label="Name",
                        default_value="Rubric Name",
                        enabled=False,
                        width=200)

    def generate_mini(self,openeditor: callable):
        with dpg.child_window(height=self.height) as self._id:

            with dpg.group(horizontal=True):

                dpg.add_color_button(label=f"{self.name}'s Color",default_value=self.color,height=self.height-16,width=50)

                with dpg.group():

                    dpg.add_input_text(
                        label="Name",
                        default_value=self.name,
                        enabled=False,
                        width=200)

                    dpg.add_input_text(
                        label="Subtitle",
                        default_value=self.desc,
                        enabled=False,
                        width=200)

                    dpg.add_button(
                        label="Edit",
                        callback=openeditor,
                        user_data=self)
                
                #=================================================
                _items = list(self.rubrics.keys())
                _items.sort()

                dpg.add_text("R\nU\nB\nR\nI\nC")
                ObjTabPattern(itemsDict=self.rubrics,addNewCallback=self.openRubricLinker,label="Link New Source Rubric")


    def listboxTest(self,sender,app_data,user_data):
        print(sender,app_data,user_data)

    def openRubricLinker(self,after:callable = None):
        # After is a function requested by the OBjTabPattern to be performed after the editor is closed/saved.
        RubricEditor(schema=self,onCloseAfter=after)


    
