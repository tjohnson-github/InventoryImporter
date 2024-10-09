

import dearpygui.dearpygui as dpg
from dataclasses import dataclass, field,asdict
import pyodbc

import CustomPickler

from DPGStage import DPGStage,ObjTabPattern
from Settings_DefaultPathing import DefaultPathing,DefaultPaths
import asyncio
from typing import Optional
from Selector_File import FileSelector
from File_Operations import csv_to_list,excel_to_list,mkdirWrapper

from CustomPickler import get,set
from Schema_Extractor_FilenameConvention import FilenameConvention,FilenameExtractorManager,FilenameExtractor,setFixer
from Schema_Extractor_DirnameConvention import DirnameConvention,DirnameExtractor,setFixer

import time
from Rubric_Editor import RubricEditor
from Rubric import RubricDisplayForSchema

default_settings_path = "Redesign\\Settings"
default_schema_path = "Redesign\\Schemas"

from Operations import Operation


@dataclass
class Schema:
    #saveName: str = field(init= False)

    name: str = ''
    desc: str = ''
    color: tuple = (0,0,0,0)

    #schema_cols: list[str] = field(default_factory=lambda: [])
    #schema_tags: list[str] = field(default_factory=lambda: [])

    @dataclass
    class EditorInputs:
        colNames    : list[str]     = field(default_factory=lambda: [])
        tags        : list[str]     = field(default_factory=lambda: [])
        necessary   : list[bool]    = field(default_factory=lambda: []) 
        operations  : list[Operation] = field(default_factory=lambda: [])  

    outputSchemaDict: dict[str:any] =  field(default_factory=lambda: {})
    # 
    #"Column Name"
    #"Tag"
    #"Necessary?"
    #"Operations"
    
             

    rubrics: dict[str:dict] = field(default_factory=lambda: {}) # Name_of_RUBRIC
    filenameConventions: list[FilenameConvention] = field(default_factory=lambda: [])
    dirnameConvention: DirnameConvention = field(default_factory=lambda: DirnameConvention())
    supported_formats: dict[str:bool] = field(default_factory=lambda: {'xlsx':True,'csv':False,'gsheet':False})

    height = 100
    width = 730

    #scansFrom: str = 'default'

    def save(self,path):

        self.saveName = f'{path}\\{self.name}.schema'
        set(self.saveName,self)

    @classmethod
    def generate_key(cls):
        pass
        with dpg.child_window(height=int(cls.height/4)+20) as _key_id:
            
            with dpg.group(horizontal=True):
                
                dpg.add_color_button(label=f"Rubric Color",default_value=(0,0,0,0),height=dpg.get_item_height(_key_id)-16,width=50)

                with dpg.child_window(border=False):

                    dpg.add_separator()
                    dpg.add_input_text(
                        #label="Name",
                        default_value="Rubric Name",
                        enabled=False,
                        width=200)
                    dpg.add_separator()

    def generate_mini(self,openeditor: callable,deleteSchema: callable, index: int):
        
        with dpg.group(horizontal=True) as self._id:

            with dpg.child_window(height=self.height,width=self.width):

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
                    dpg.add_button(label="+",callback=self.linkNewRubric,height=self.height-16)

                    with dpg.child_window() as self.rubricChildWindow:
                        pass

                    #ObjTabPattern(itemsDict=self.rubrics,addNewCallback=self.linkNewRubric,label="Link New Source Rubric")


            dpg.add_button(label="D\nE\nL\nE\nT\nE",callback=deleteSchema,user_data=index,height=self.height,width=30)
        self.refreshRubrics()


    def listboxTest(self,sender,app_data,user_data):
        print(sender,app_data,user_data)

    def refreshRubrics(self):
        
        dpg.delete_item(self.rubricChildWindow,children_only=True)
        dpg.push_container_stack(self.rubricChildWindow)

        for rubricName,rubric in self.rubrics.items():

            RubricDisplayForSchema(
                rubric = rubric,
                openEditor = self.editExistingRubric,
                deleteRubric=self.deleteRubric)

            #rubric.generate_mini(openEditor = self.editExistingRubric,deleteRubric=self.deleteRubric)

    def linkNewRubric(self,after:callable = None):
        # After is a function requested by the OBjTabPattern to be performed after the editor is closed/saved.
        RubricEditor(schema=self,onCloseAfter=self.refreshRubrics)

    def editExistingRubric(self,sender,app_data,user_data):
        
        _rubric = user_data


        RubricEditor(schema=self,rubric=_rubric)

    def deleteRubric(self,sender,app_data,user_data):

        _rubric = user_data

        def back():
            dpg.delete_item(_pop)

        def proceed():

            del self.rubrics[_rubric.name]

            self.save(path=default_schema_path)

            #dpg.push_container_stack(self.rubricChildWindow)
            self.refreshRubrics()
            back()

        with dpg.window(popup=True) as _pop:
            with dpg.group():
                dpg.add_text(f"Are you sure you wish you delete ")
                
                with dpg.group(horizontal=True):
                    dpg.add_input_text(default_value=f"{_rubric.name}",enabled=False)
                    dpg.add_text(f"?")
            
                dpg.add_separator()

                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=40)
                    dpg.add_button(label="Yes",callback = proceed)
                    dpg.add_button(label="No",callback = back)

        

    
