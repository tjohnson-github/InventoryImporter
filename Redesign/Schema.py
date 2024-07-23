

import dearpygui.dearpygui as dpg
from dataclasses import dataclass, field,asdict
import pyodbc

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

    schema_cols: list[str] = field(default_factory=lambda: [])
    schema_tags: list[str] = field(default_factory=lambda: [])

    outputSchemaDict: dict[str:any] =  field(default_factory=lambda: {})

    rubrics: dict[str:dict] = field(default_factory=lambda: {}) # Name_of_RUBRIC
    filenameConventions: list[FilenameConvention] = field(default_factory=lambda: [])
    dirnameConvention: DirnameConvention = field(default_factory=lambda: DirnameConvention())

    height = 100

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
                
                with dpg.group():
                    dpg.add_text("Rubrics")
                    dpg.add_listbox(items=[])
                    
