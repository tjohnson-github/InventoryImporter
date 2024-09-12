


import dearpygui.dearpygui as dpg
dpg.create_context()
from dataclasses import dataclass, field
import pyodbc

import CustomPickler

from SQLInterface import SQLLinker
from DPGStage import DPGStage
from Settings_DefaultPathing import DefaultPathing,DefaultPaths
import asyncio
import time


class TableTest(DPGStage):

    tableColumnDefaultWidth = 100
    #numColumns = 90
    fixedWidth = True

    #columnObjs = []
    decelerator = 0.5

    #subtables

    def generate_id(self,**kwargs):

         self.numColumns = kwargs.get("numColumns")

         self.subtables =[]
         _chunks = self.getChunks()

         with dpg.child_window(border=True,horizontal_scrollbar=True,height=80) as self._id:

            dpg.add_button(label="populate table",callback=self.pop)

            with dpg.group(horizontal=True):

                for chunk in _chunks:

                    with dpg.table(header_row=True,scrollX=True,resizable=False,reorderable =True,width=80) as _tableEditor:
                        pass

                    self.subtables.append(_tableEditor)

                #with dpg.table(header_row=True,scrollX=True,resizable=False,reorderable =True,clipper=True) as self.tableEditor:
                #   pass

    def pop(self,sender,app_data,user_data):
    
        asyncio.run(self.populateTable())


    def getChunks(self):


        _cutoff = 64
        # break into chunks
        _chunks = []
        _tempChunk=[]
        for x in range(0,self.numColumns):
            _tempChunk.append(x)
            if x%_cutoff==0 and x!=0:
                _chunks.append(_tempChunk)
                _tempChunk = []

        if _tempChunk != []:
            _chunks.append(_tempChunk)

        print("----------------------")
        for chunk in _chunks:
            print(chunk)
        print("----------------------")
        
        return _chunks

    async def populateTableCols(self):

        self.columnObjs=[]

        _chunks = self.getChunks()
        for i,chunk in enumerate(_chunks):

            parent = self.subtables[i]

            for column in chunk:

                #if column > 120:
                #    time.sleep(4)                            
                #time.sleep(self.decelerator)                            
                _newCol = dpg.add_table_column(label=f'{column}',tag=f'{self._id}_c{column}',width_fixed=self.fixedWidth,width=self.tableColumnDefaultWidth,parent=parent)
                self.columnObjs.append(_newCol)
                #print(column)

            time.sleep(self.decelerator)                            


    async def populateTableRows(self):

        _chunks = self.getChunks()

        for chunk in _chunks:

            #for j in range(0,self.numColumns):
            for j in chunk:
                print(j)
                #if j>self.deceleratorCutoff:
                time.sleep(self.decelerator)

                dpg.configure_item(self.columns[j],width=self.tableColumnDefaultWidth)

                for row in self.rows:
                    print(f'{row.name=}')
                    print(f'{row.rowObj=}')

                    #time.sleep(self.decelerator)
                    #time.sleep(self.decelerator)
                    _newItem = self.generateInputByType(row=row,columnIndex=j)
                    row.items.append(_newItem)


        print("cols done")

    async def populateTable(self):

        await self.populateTableCols()
        #await self.populateTableRows()





def main():
   
    with dpg.window(height=800,width=1000):
        TableTest(numColumns=40)
        TableTest(numColumns=90)
        TableTest(numColumns=180)

    dpg.create_viewport(title='Custom Title', width=1300, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__=="__main__":
    main()