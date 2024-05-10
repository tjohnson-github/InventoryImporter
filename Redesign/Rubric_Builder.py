

import dearpygui.dearpygui as dpg
dpg.create_context()
from dataclasses import dataclass, field
import pyodbc

import CustomPickler

from SQLInterface import SQLLinker
from DPGStage import DPGStage

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

    height=500
    width=1000

    items = ["Custom","From SQL"]
    chosen = False


    def generate_id(self,**kwargs):
        with dpg.window(width=self.width,height=self.height):

            self.chooser = dpg.add_combo(items=self.items,default_value=self.items[0],label="Select how you want to build your converter schema.",callback=self.chooserCallback,width=100)
            dpg.add_separator()
            with dpg.group() as self.rubricGroup: 
                RubricBuilderCustom()

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
            RubricBuilderCustom()
        elif user_data=="From SQL":
            RubricBuilderSQL()

        self.chosen = True

class RubricBuilderSQL(DPGStage):

    def generate_id(self,**kwargs):

        with dpg.group() as self._id:
            dpg.add_button(label="Link SQL",callback=self.linkSQL)
            dpg.add_text("Imported SQL Tables")
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

        self.editor = ColumnEditor(schema=headers[0:15])


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
    tableColumnDefaultWidth = 100

    allColumns = []

    def gatherInfo(self):

        _newRubric = Rubric(
            name=dpg.get_item_value(self.name),
            subname=dpg.get_item_value(self.subtitleInput),)

    def generate_id(self,**kwargs):

        with dpg.group() as self._id:
            dpg.add_text("Build Schema")

            self.nameInput = dpg.add_input_text(label="Name of Rubric",width=300)
            self.subtitleInput = dpg.add_input_text(label="Subtitle",width=300)

            with dpg.child_window(height=130):
                dpg.add_text("When defining a rubric, we assume that the target schema may not be used in its entirety.")
                dpg.add_text("For each column, check which fields are necessary for bare minimum transformation.")
                dpg.add_text("You can give these necessary fields tags to better track their importance/purpose especially if the target and source schemas are not intuitively named.")
                dpg.add_text("If more fields than naught are important, check the following box and then start unchecking which ones will not be used.")
                _checkAll = dpg.add_checkbox(default_value=False,label="Check All Boxes")


            self.columnSetter = dpg.add_input_int(
                label="Columns",
                default_value=self.columns,
                callback=self.change_columns,
                on_enter =True,
                max_value=self.maxCols,max_clamped=True,
                min_value=1,min_clamped =True)
             
            self.error = dpg.add_text("Column Schema caps at 99 due to limitations of the UI.",show=False)

        self.editor = ColumnEditor()
        dpg.set_item_callback(_checkAll,self.editor.checkAll)
    

    def change_columns(self,sender,app_data):
        
        # Determine if user is requesting more than max columns
        if app_data>=self.maxCols:
            dpg.configure_item(self.error,show=True)
        else:
            dpg.configure_item(self.error,show=False)

        # WORK ON A DECELLERATOR HERE
        time.sleep(0.01)

        # Fixed Width Setter for expanding columns
        if app_data >= 9:
            defaultFixedWidth=True
            for column in self.editor.columns:
                dpg.configure_item(column,width_fixed=True)
        else:
            defaultFixedWidth=False
            for column in self.editor.columns:
                dpg.configure_item(column,width_fixed=False)

        # Adding Columns
        if app_data > self.columns:
            for column in range(self.columns,app_data):
                self.editor.add_column(column,defaultFixedWidth)
             
        # Subtracting Columns
        elif app_data < self.columns:
            for column in range(app_data,self.columns):
                self.editor.delete_column(column)

        self.columns = app_data

class EditorRow(DPGStage):

    name: str
    type: any
    rowObj: str # will be _id
    items: list[str]

class ColumnEditor(DPGStage):
       
    tableColumnDefaultWidth = 100
    fixedWidthCutoff = 9
    fixedWidth = False
    columns = []
    rows = {"Column Name":{"type":str},
            "Necessary?":{"type":bool},
            "Tag":{"type":str}}

    def generate_id(self,**kwargs):
        self.schema = kwargs.get("schema",[f'Test Name {x}' for x in range(0,5)])
        self.numColumns = len(self.schema)

        with dpg.child_window(horizontal_scrollbar=True) as self._id:

            with dpg.group(horizontal=True):

                with dpg.child_window(width=120,border=False):
                    with dpg.table(header_row=True):

                        rowLabels = dpg.add_table_column(label=f'Index',width_fixed=True,width=self.tableColumnDefaultWidth)
                        for i,(key,value) in enumerate(self.rows.items()):
                            with dpg.table_row():
                                dpg.add_text(key)

                with dpg.child_window(border=False,horizontal_scrollbar=True):

                    with dpg.table(header_row=True,scrollX=True,resizable=True,) as self.tableEditor:

                        if self.numColumns > self.fixedWidthCutoff:
                            self.fixedWidth=True

                        for column in range(0,self.numColumns):
                            _newCol = dpg.add_table_column(label=f'{column}',tag=f'{self._id}_c{column}',width_fixed=self.fixedWidth,width=self.tableColumnDefaultWidth)
                            self.columns.append(_newCol)

                        for i,(key,value) in enumerate(self.rows.items()):
                            with dpg.table_row() as _newRow:
                                #dpg.add_spacer(width=self.tableColumnDefaultWidth)
                                _newRowItems = []
                                for j in range(0,self.numColumns):
                                    _newItem = self.generateInputByType(type=self.rows[key]["type"],columnIndex=j)
                                    _newRowItems.append(_newItem)

                            self.rows[key].update({"rowList":_newRowItems})
                            self.rows[key].update({"rowObj":_newRow})

    def generateInputByType(self,type,columnIndex):

        if type==str:
            _ = dpg.add_input_text(width=self.tableColumnDefaultWidth,default_value=self.schema[columnIndex])
        elif type==bool:
            _ = dpg.add_checkbox()

        return _   

    def add_column(self,columnId,fixedWidth=True):
        dpg.push_container_stack(self.tableEditor)
        _newCol = dpg.add_table_column(label=f'{columnId}',tag=f'{self._id}_c{columnId}',width_fixed=fixedWidth,width=self.tableColumnDefaultWidth)
        self.columns.append(_newCol)
        self.schema.append('')
        self.numColumns+=1

        for i,(key,value) in enumerate(self.rows.items()):
            dpg.push_container_stack(self.rows[key]["rowObj"])
            _newItem = self.generateInputByType(self.rows[key]["type"],columnIndex=columnId)
            self.rows[key]["rowList"].append(_newItem)

    def delete_column(self,columnId):
        # if deleting from end:
        dpg.push_container_stack(self.tableEditor)
        dpg.delete_item(f'{self._id}_c{columnId}')
        self.columns = self.columns[:-1]
        self.numColumns-=1
        # if deleting from any other index:
        pass

    def checkAll(self,sender,app_data,user_data):
        for checkbox in self.rows["Necessary?"]["rowList"]:
            dpg.configure_item(checkbox,default_value=app_data)

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

    def newBuild(self,sender,app_data,user_data):

        RubricTypeSelector()

    

def main():
   
    FileFormatter()

    dpg.create_viewport(title='Custom Title', width=1300, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__=="__main__":
    main()