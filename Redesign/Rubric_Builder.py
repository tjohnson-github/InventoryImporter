

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

default_path = "Redesign//Settings//"

import time

@dataclass
class Rubric:
    name: str
    subname: str
    outputSchema: tuple[str]
    correspondenceDict: dict


@dataclass
class DesiredFormat:
    name: str
    headersAKAColumns: list[str]
    correspondenceDict: dict
    # will be something like:
    # { column1: 1, column2: 2, ...
    #   or
    # { column1: IMPORTANTCONCEPT1, column4: IMPORTANTCONCEPT2, ...


class RubricTypeSelector(DPGStage):

    height=540
    width=1000

    items = ["Custom","From SQL","From Spreadsheet File",]
    chosen = False

    def generate_id(self,**kwargs):
        with dpg.window(width=self.width,height=self.height):

            with dpg.group():
                dpg.add_text("Build Schema")

                dpg.add_separator()
                self.nameInput = dpg.add_input_text(label="Name of Rubric",width=300)
                self.subtitleInput = dpg.add_input_text(label="Subtitle",width=300)

                with dpg.collapsing_header(default_open=False,label="Tutorial"):
                    dpg.add_text("When defining a rubric, we assume that the target schema may not be used in its entirety.")
                    dpg.add_text("For each column, check which fields are necessary for bare minimum transformation.")
                    dpg.add_text("You can give these necessary fields tags to better track their importance/purpose especially if the target and source schemas are not intuitively named.")
                    dpg.add_text("If more fields than naught are important, check the following box and then start unchecking which ones will not be used.")
                    
            self.chooser = dpg.add_combo(items=self.items,default_value=self.items[0],label="Select how you want to build your converter schema.",callback=self.chooserCallback,width=140)
            dpg.add_separator()
            with dpg.group() as self.rubricGroup: 
                self.rubricEditor = RubricBuilderCustom()


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

        dpg.delete_item(self.rubricGroup,children_only=True)
        dpg.push_container_stack(self.rubricGroup)

        if user_data=="Custom":
            self.rubricEditor = RubricBuilderCustom()
        elif user_data=="From SQL":
            self.rubricEditor = RubricBuilderSQL()
        elif user_data=="From Spreadsheet File":
            self.rubricEditor = RubricBuilderFile()
        self.chosen = True


class RubricBuilderFile(DPGStage):

    def generate_id(self,**kwargs):

        with dpg.group() as self._id:
            dpg.add_button(label="Load File",callback=self.loadFile)
            dpg.add_text("Imported File Header")
            with dpg.child_window() as self.tableEditor:
                pass

    def loadFile(self):
        self.fs = FileSelector(label="Load Spreadsheet file for column schema import",nextStage=self.manipulateFile)

    def manipulateFile(self):
        _filepath = self.fs.selectedFile 

        print (_filepath)
        readArray = []
        error = ''

        if _filepath[-4:] == 'csv':
            readArray,error = csv_to_list(_filepath)
        elif _filepath[-4:] == 'xlsx':
            readArray,error = excel_to_list(_filepath)

        if readArray:
            for row in readArray: print(row)
            dpg.push_container_stack(self.tableEditor)
            self.colEditor = ColumnEditor(schema=readArray[0])
            asyncio.run(self.colEditor.populateTable())
        else:
            with dpg.window(popup=True):
                dpg.add_text(error)

class RubricBuilderSQL(DPGStage):

    def generate_id(self,**kwargs):

        with dpg.group() as self._id:
            dpg.add_button(label="Link SQL",callback=self.linkSQL)
            dpg.add_text("Imported File Header")
            with dpg.child_window() as self.tableEditor:
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

        self.editor = ColumnEditor(schema=headers)
        #self.editor = ColumnEditor(schema=headers)
        asyncio.run(self.editor.populateTable())


        #with dpg.group(horizontal=True):

        #    for i,columnName in enumerate(headers):
        ##        print(i,"\t",columnName)
        #        dpg.add_input_text(default_value=columnName,enabled=False,width=(len(columnName)*10))

    

        #for i,x in enumerate(self.sqlLinker.cursor):
        #    print(i,"\t",x)
        #    dpg.add_input_text(default_value=x,enabled=False)
    

    def linkSQL(self,sender,app_data,user_data):
        self.sqlLinker = SQLLinker(after = self.displayAllTables)

class RubricBuilderCustom(DPGStage):

    columns: int  = 5
    maxCols = 98
    tableColumnDefaultWidth = 115

    allColumns = []

    def gatherInfo(self):

        _newRubric = Rubric(
            name=dpg.get_item_value(self.name),
            subname=dpg.get_item_value(self.subtitleInput),)

    def generate_id(self,**kwargs):

        with dpg.group() as self._id:
           
            self.colEditor = ColumnEditor()

            # display the columns
            asyncio.run(self.colEditor.populateTable())
        
            dpg.add_button(
                label="Save Rubric and add input->output schema correspondence later",
                width=dpg.get_item_width(self.colEditor._id))

            dpg.add_text("OR")

            dpg.add_button(
                label="Load a file right now to begin adding input->output schema correspondence",
                width=dpg.get_item_width(self.colEditor._id))

@dataclass
class EditorRow(DPGStage):

    name: str
    type: type
    tooltip: str
    items: list[str] = field(init=False)

class ColumnEditor(DPGStage):
       
    tableColumnDefaultWidth = 100
    fixedWidthCutoff = 9
    fixedWidth = False

    rows: list[EditorRow]

    deceleratorCutoff = 50
    decelerator = 0.00001

    def main(self,**kwargs):

        print("here")

        self.rows = [
            EditorRow(
                name = "Column Name",
                type = str,
                tooltip = "This is what will be displayed in the header of the output file."),
            EditorRow(name = "Tag",
                type = str,                
                tooltip = "The shorthand name of what kinds of values this column contains.\nFor example:\n\t- UPC\n\t- Quantity\n\t- Description"),
             EditorRow(name = "Necessary?",
                type = bool,
                tooltip = "If checked, new input schemas will be required to provide a column which contains values matching the above tag."),
            EditorRow(name = "Operations",
                type = list,                
                tooltip = "This section provides an editor allowing us to populate columns in the output schema which are DERIVED from:\n\t- a combination of input columns\n\t- additional calculations made to individual input columns\n\t- or a combination of both"),
            ]

        self.schema = kwargs.get("schema",[f'Test Name {x}' for x in range(0,5)])
        self.numColumns = len(self.schema)

        if self.numColumns > self.deceleratorCutoff:
            self.decelerator = .2

    def generate_id(self,**kwargs):

        with dpg.group() as self._id:
       


            with dpg.child_window(horizontal_scrollbar=True,height=200):

                with dpg.group(horizontal=True):

                    self.columnSetter = dpg.add_input_int(
                        label="Specify Columns Requested OR Add column before index",
                        default_value=self.numColumns,
                        callback=self.change_columns,
                        on_enter =True,
                        min_value=1,min_clamped =True,
                        width=200)

                    self.columnIndexSetter = dpg.add_input_int(
                        label="",
                        width=150,
                        #@default_value=self.numColumns-1,
                        on_enter=True,
                        step=0,
                        min_value=0,min_clamped =True,
                        max_value=self.numColumns-1,max_clamped=True,
                        callback=self.addColumn,show=False)

                with dpg.group(horizontal=True):

                    # Row Names Key
                    with dpg.child_window(width=120,border=False):
                        with dpg.table(header_row=True):

                            rowLabels = dpg.add_table_column(label=f'Index',width_fixed=True,width=self.tableColumnDefaultWidth)
                            for row in self.rows:

                                with dpg.table_row():
                                    with dpg.group(horizontal=True):
                                        _rowLabel = dpg.add_text(row.name)
                                        if row.name=="Necessary?":
                                            _check = dpg.add_checkbox(default_value=False,callback=self.checkAll)
                                            with dpg.tooltip(_check):
                                                dpg.add_text("Check all boxes?")

                                    with dpg.tooltip(_rowLabel):
                                        dpg.add_text(row.tooltip)



                    # Actual Schema Builder Table
                    with dpg.child_window(border=False,horizontal_scrollbar=True):

                        with dpg.group(horizontal=True) as self.columnEditor:
                            for row in self.rows:
                                row.items = []     


    def generateInputByType(self,row: EditorRow,columnIndex):

        parent=self.columns[columnIndex]

        #if self.rows[key]["type"]==str:
        if row.type==str:
            if row.name == "Column Name":
                _default_value = self.schema[columnIndex]
            else: 
                _default_value = ""

            _ = dpg.add_input_text(width=self.tableColumnDefaultWidth,default_value=_default_value,parent=parent)
        #elif self.rows[key]["type"]==bool:
        elif row.type==bool:
            _ = dpg.add_checkbox(parent=parent)
        elif row.type==list:
           with dpg.child_window(width=self.tableColumnDefaultWidth-16,height=50,parent=parent) as _:
               pass
           #_ = dpg.add_button(label="<>")

        return _   

    async def populateTableCols(self):

        self.columns = []

        for columnIndex in range(0,self.numColumns):
            _newCol = dpg.add_child_window(width=self.tableColumnDefaultWidth,parent=self.columnEditor,border=False)
            self.columns.append(_newCol)

    async def populateTableRows(self):

        self.columnAdd = []
        self.columnHeaders = []
        self.columnRemove = []

        for columnIndex in range(0,self.numColumns):

            parent=self.columns[columnIndex]

            with dpg.group(horizontal=True,parent=parent):
                _bf = dpg.add_button(arrow=True,direction=0,callback=self.addColumn,user_data=columnIndex)
                with dpg.tooltip(_bf): dpg.add_text(f"Add new column before Index {columnIndex}.")
                self.columnAdd.append(_bf)
                _= dpg.add_text(f"Index {columnIndex}")
                self.columnHeaders.append(_)
                _x= dpg.add_button(label='X',callback=self.delete_column,user_data=columnIndex)
                self.columnRemove.append(_x)

            for row in self.rows:
                _newItem = self.generateInputByType(row=row,columnIndex=columnIndex)
                row.items.append(_newItem)

    async def populateTable(self):

        await self.populateTableCols()
        await self.populateTableRows()

    def addColumn(self,sender,app_data,user_data):
        # Whether through a pattern, or an input int for adding a column to a special index: 
        # add column @ that index
          #parent = self.columnEditor

        index_to_add_before = user_data
        print(f'B:\t{self.columns=}')
        print(f"inserting @:\t{app_data}")

        _newCol = dpg.add_child_window(width=self.tableColumnDefaultWidth,parent=self.columnEditor,before=self.columns[index_to_add_before],border=False)
        self.columns.insert(index_to_add_before,_newCol)
        self.schema.insert(index_to_add_before,'new')
        self.numColumns+=1
        print(f'A:\t{self.columns=}')
        print("------------")
        dpg.configure_item(self.columnSetter,default_value=self.numColumns)
        dpg.configure_item(self.columnIndexSetter,default_value=self.numColumns-1,max_value=self.numColumns-1)

        _newColIndex =self.columns.index(_newCol)


        with dpg.group(horizontal=True,parent=_newCol):
            _bf = dpg.add_button(arrow=True,direction=0,callback=self.addColumn,user_data=_newColIndex)
            with dpg.tooltip(_bf): dpg.add_text(f"Add new column before Index {_newColIndex}.")
            self.columnAdd.append(_bf)
            _= dpg.add_text(f"Index {0}")
            self.columnHeaders.insert(index_to_add_before,_)
            _x= dpg.add_button(label='X',callback=self.delete_column,user_data=_newColIndex)
            self.columnRemove.insert(index_to_add_before,_x)

            for row in self.rows:
                _newItem = self.generateInputByType(row=row,columnIndex=_newColIndex)
                row.items.insert(index_to_add_before,_newItem)

        # Now change the index labels of everything ahead of it: 
        for column in self.columns[index_to_add_before:]:
      
            _currentIndex = self.columns.index(column)

            dpg.configure_item(self.columnHeaders[_currentIndex],default_value=f"Index {_currentIndex}")
            dpg.set_item_user_data(self.columnRemove[_currentIndex],user_data=_currentIndex)

        if self.numColumns>=1:
            dpg.configure_item(self.columnRemove[0],show=True)


    def delete_column(self,sender,app_data,user_data):

        print(f'{sender=}')
        print(f'{app_data=}')
        print(f'{user_data=}')

        try:
            self.schema.remove(self.schema[user_data])
        except Exception as e:
            print("greater than schema index:",e)

        for column in self.columns[user_data:]:
      
            columnIndex =  self.columns.index(column)

            dpg.configure_item(self.columnHeaders[columnIndex],default_value=f"Index {columnIndex-1}")
            dpg.set_item_user_data(self.columnRemove[columnIndex],user_data=columnIndex-1)

        dpg.delete_item(self.columns[user_data])
        self.columnHeaders.remove(self.columnHeaders[user_data])
        self.columnRemove.remove(self.columnRemove[user_data])

        self.columns.remove(self.columns[user_data])
        self.numColumns-=1
        dpg.configure_item(self.columnSetter,default_value=dpg.get_value(self.columnSetter)-1)
        dpg.configure_item(self.columnIndexSetter,default_value=self.numColumns-1,max_value=self.numColumns-1)

        if self.numColumns==1:
            dpg.configure_item(self.columnRemove[0],show=False)


    def checkAll(self,sender,app_data,user_data):

        for row in self.rows:
            if row.name=="Necessary?":
                for checkbox in row.items:
                    dpg.configure_item(checkbox,default_value=app_data)

    def change_columns(self,sender,app_data):
        
        def add_columnToEnd(self,columnId):

            #parent = self.columnEditor

            _newCol = dpg.add_child_window(width=self.tableColumnDefaultWidth,parent=self.columnEditor,border=False)
            self.columns.append(_newCol)
            self.schema.append('new')
            self.numColumns+=1
            dpg.configure_item(self.columnIndexSetter,default_value=self.numColumns-1,max_value=self.numColumns-1)
            _newColIndex =self.columns.index(_newCol)

            with dpg.group(horizontal=True,parent=_newCol):
                _bf = dpg.add_button(arrow=True,direction=0,callback=self.addColumn,user_data=_newColIndex)
                with dpg.tooltip(_bf): dpg.add_text(f"Add new column before Index {_newColIndex}.")
                self.columnAdd.append(_bf)
                _= dpg.add_text(f"Index {_newColIndex}")
                self.columnHeaders.append(_)
                _x= dpg.add_button(label='X',callback=self.delete_column,user_data=_newColIndex)
                self.columnRemove.append(_x)

                for row in self.rows:
                    _newItem = self.generateInputByType(row=row,columnIndex=_newColIndex)
                    row.items.append(_newItem)

            if self.numColumns>=1:
                dpg.configure_item(self.columnRemove[0],show=True)

        def delete_columnFromEnd(self,columnId):

            try:
                self.schema.remove(self.schema[columnId])
            except:
                print("greater than schema index")

            dpg.delete_item(self.columns[columnId])

            self.columnHeaders.remove(self.columnHeaders[columnId])
            self.columnRemove.remove(self.columnRemove[columnId])
            self.columns.remove(self.columns[columnId])

            self.numColumns-=1
            dpg.configure_item(self.columnIndexSetter,default_value=self.numColumns-1,max_value=self.numColumns-1)
            #dpg.configure_item(self.columnSetter,default_value=dpg.get_value(self.columnSetter)-1)
            if self.numColumns==1:
                    dpg.configure_item(self.columnRemove[0],show=False)


        # Adding Columns
        if app_data > self.numColumns:
            for columnIndex in range(self.numColumns,app_data):
                add_columnToEnd(self,columnIndex)
             
        # Subtracting Columns
        elif app_data < self.numColumns:
            for columnIndex in range(app_data,self.numColumns):
                delete_columnFromEnd(self,columnIndex)

        self.numColumns = app_data

class FileFormatter(DPGStage):

    # CHOOSE DESIRED OUTPUT FIRST
    # THEN DISPLAY INCOMMING FORMAT and ASK FOR CORRELATION TABLE; CREATE IF NOT EXIST; DISPLAY IF EXIST; LET EDIT
    
    # LATER, UPON LOAD, WHEN VERIFYING A TABLE WITH THAT SCHEMA, CAN SUGGEST OR EVEN AUTO-RUN FORMATTER
    #   BUT THIS NEEDS TO ASK IF 


    height = 240
    width =800

    def print_me(sender):
        print(f"Menu Item: {sender}")

    def generate_id(self,**kwargs):
        
        with dpg.window(height=self.height,width=self.width) as self._id:

            with dpg.menu_bar():
                with dpg.menu(label="File"):
                    dpg.add_menu_item(label="New Converter",callback=self.newBuild)
                    dpg.add_menu_item(label="Set Default Directories",callback=self.setDirs)
                    dpg.add_menu_item(label="Save", callback=self.print_me)
                    dpg.add_menu_item(label="Save As", callback=self.print_me)

                    with dpg.menu(label="Settings"):
                        dpg.add_menu_item(label="Setting 1", callback=self.print_me, check=True)
                        dpg.add_menu_item(label="Setting 2", callback=self.print_me)

                dpg.add_menu_item(label="Help", callback=self.print_me)

                with dpg.menu(label="Widget Items"):
                    dpg.add_checkbox(label="Pick Me", callback=self.print_me)
                    dpg.add_button(label="Press Me", callback=self.print_me)
                    dpg.add_color_picker(label="Color Me", callback=self.print_me)

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

        RubricTypeSelector()

    

def main():
   
    FileFormatter()

    dpg.create_viewport(title='Custom Title', width=1300, height=670)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__=="__main__":
    main()