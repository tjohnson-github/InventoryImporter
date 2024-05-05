

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
    

    def displayTableSchema(self,tableName):

        dpg.push_container_stack(self.tableEditor)
        dpg.add_separator()

        cursorStr = f'SELECT * FROM JFGC.dbo.{tableName}'
        #cursorStr = "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'"

        self.sqlLinker.cursor.execute(cursorStr)

        headers                 =   [i[0] for i in self.sqlLinker.cursor.description]

        print (headers)
        rows = []
 
        dpg.add_text("IM_ITEM")
        with dpg.group(horizontal=True):

            for i,columnName in enumerate(headers):
                print(i,"\t",columnName)
                dpg.add_input_text(default_value=columnName,enabled=False,width=(len(columnName)*10))

    

        #for i,x in enumerate(self.sqlLinker.cursor):
        #    print(i,"\t",x)
        #    dpg.add_input_text(default_value=x,enabled=False)
    

    def linkSQL(self,sender,app_data,user_data):
        self.sqlLinker = SQLLinker(after = self.displayAllTables)

class RubricBuilderCustom(DPGStage):

    columns: int  = 5
    maxCols = 98

    def generate_id(self,**kwargs):

        with dpg.group() as self._id:
            dpg.add_text("Built Schema")
            self._columns = dpg.add_input_int(
                label="Columns",
                default_value=self.columns,
                callback=self.change_columns,
                on_enter =True,
                max_value=self.maxCols,max_clamped=True,
                min_value=1,min_clamped =True)

            self.error = dpg.add_text("Column Schema caps at 99 due to limitations of the UI.",show=False)


        with dpg.child_window():
            with dpg.table(header_row=True,scrollX=True) as self.tableEditor:

                for column in range(0,dpg.get_value(self._columns)):
                    dpg.add_table_column(label=f'{column}',tag=f'{self._id}_c{column}')



    def change_columns(self,sender,app_data):
        
        if app_data>=self.maxCols:
            dpg.configure_item(self.error,show=True)
        else:
            dpg.configure_item(self.error,show=False)

        try:

            time.sleep(0.01)


            if app_data > self.columns:
                for column in range(self.columns,app_data):
                    dpg.push_container_stack(self.tableEditor)
                    dpg.add_table_column(label=f'{column}',tag=f'{self._id}_c{column}')
            elif app_data < self.columns:
                for column in range(app_data,self.columns):
                    dpg.push_container_stack(self.tableEditor)
                    dpg.delete_item(f'{self._id}_c{column}')

            self.columns = app_data
        except Exception as e:
            print(e)

    def add_column(self,index):
        pass

class FileFormatter(DPGStage):

    # CHOOSE DESIRED OUTPUT FIRST
    # THEN DISPLAY INCOMMING FORMAT and ASK FOR CORRELATION TABLE; CREATE IF NOT EXIST; DISPLAY IF EXIST; LET EDIT
    
    # LATER, UPON LOAD, WHEN VERIFYING A TABLE WITH THAT SCHEMA, CAN SUGGEST OR EVEN AUTO-RUN FORMATTER
    #   BUT THIS NEEDS TO ASK IF 


    height = 550
    width =1250

    def print_me(sender):
        print(f"Menu Item: {sender}")

    def generate_id(self,**kwargs):
        
        with dpg.window(height=self.height,width=self.width) as self._id:

            with dpg.menu_bar():
                with dpg.menu(label="File"):
                    #dpg.add_menu_item(label="New Transfer Format",callback=self.newBuild)
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


            with dpg.child_window(height=100,width=self.width-55):
                dpg.add_text("""This program builds and saves file formatters.\n
When creating new formatters, you are picking an input and an output format.\n
These will be represented best as columns in a spreadsheet, or a table schema.\n
\tAlthough this program can support a 1 to Many file converter format, it will be most effecient\n
\tto instead presuppose a Many to 1 conversion. That is, messy files being standardized.\n
Each format will have within it saved micro-formats that identify and save where a file is coming in from.
                                """)

            with dpg.child_window(height=100,width=self.width-55,parent=self._id,horizontal_scrollbar=True) as self.SQLtables:
                
                RubricBuilderSQL()
                

            with dpg.child_window(height=300,width=self.width-55,parent=self._id,horizontal_scrollbar=True) as self.newTables:
                
                self.rbc = RubricBuilderCustom()
                

    def newBuild(self,sender,app_data,user_data):

        with dpg.child_window(height=self.height-15,width=self.width-15,parent=self._id):
            pass

    

def main():
   
    FileFormatter()

    dpg.create_viewport(title='Custom Title', width=1300, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__=="__main__":
    main()