
from dearpygui import dearpygui as dpg
from Column_Editor import SchemaColumnEditor
from SQLInterface import SQLLinker

from File_Selector import FileSelector
from File_Operations import csv_to_list,excel_to_list
from DPGStage import DPGStage

import asyncio


class SchemaLoader(DPGStage):
    default_color: tuple
    colEditor: SchemaColumnEditor
    tableEditor: int

    def main(self,**kwargs):
        self.default_color = kwargs.get("color")
        print(f"{self.default_color=}")


class SchemaFromFile(SchemaLoader):

    def generate_id(self,**kwargs):

        with dpg.group() as self._id:
            dpg.add_button(label="Load File",callback=self.loadFile)
            with dpg.group() as self.tableEditor:
                pass

    def loadFile(self):
        self.fs = FileSelector(
            label="Load Spreadsheet file for column schema import",
            nextStage=self.manipulateFile)

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
            for row in readArray: print(row)
            dpg.push_container_stack(self.tableEditor)
            self.colEditor = SchemaColumnEditor(schema=readArray[0],color=self.default_color)
            asyncio.run(self.colEditor.populateTable())
        else:
            with dpg.window(popup=True):
                dpg.add_text(error)

class SchemaFromSQL(SchemaLoader):

    def generate_id(self,**kwargs):

        with dpg.group() as self._id:
            dpg.add_button(label="Link SQL",callback=self.linkSQL)
            with dpg.group() as self.tableEditor:
                pass


    def displayAllTables(self):

        dpg.push_container_stack(self.tableEditor)
        dpg.add_separator()

        cursorStr = "SELECT * FROM INFORMATION_SCHEMA.TABLES"
        self.sqlLinker.cursor.execute(cursorStr)

        headers                 =   [i[0] for i in self.sqlLinker.cursor.description]
        rows = [x for x in self.sqlLinker.cursor]

        dpg.add_text(headers)
        dpg.add_combo(items=rows)

        dpg.add_separator()
        self.displayTableSchema(tableName="IM_ITEM")

    def displayTableSchema(self,tableName):

        dpg.push_container_stack(self.tableEditor)
        dpg.add_separator()

        cursorStr = f'SELECT * FROM JFGC.dbo.{tableName}'
        #cursorStr = "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'"

        self.sqlLinker.cursor.execute(cursorStr)

        headers                 =   [i[0] for i in self.sqlLinker.cursor.description]

        print (headers)
        print(len(headers))
        rows = []
 
        dpg.add_text(tableName)

        self.colEditor = SchemaColumnEditor(schema=headers,color=self.default_color)
        #self.editor = ColumnEditor(schema=headers)
        asyncio.run(self.colEditor.populateTable())


        #with dpg.group(horizontal=True):

        #    for i,columnName in enumerate(headers):
        ##        print(i,"\t",columnName)
        #        dpg.add_input_text(default_value=columnName,enabled=False,width=(len(columnName)*10))

    

        #for i,x in enumerate(self.sqlLinker.cursor):
        #    print(i,"\t",x)
        #    dpg.add_input_text(default_value=x,enabled=False)
    

    def linkSQL(self,sender,app_data,user_data):
        self.sqlLinker = SQLLinker(after = self.displayAllTables)

class SchemaFromScratch(SchemaLoader):

    columns: int  = 5
    maxCols = 98
    tableColumnDefaultWidth = 115

    allColumns = []

    def gatherInfo(self):

        _newRubric = Rubric(
            name=dpg.get_item_value(self.name),
            subname=dpg.get_item_value(self.subtitleInput),)

    def generate_id(self,**kwargs):

        #self.filenameExtractor = kwargs.get("filenameExtractor")

        with dpg.group() as self._id:
            with dpg.group() as self.tableEditor:
                self.colEditor = SchemaColumnEditor(**kwargs)

            # display the columns
            asyncio.run(self.colEditor.populateTable())
     