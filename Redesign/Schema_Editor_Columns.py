
from dearpygui import dearpygui as dpg
from Schema_Extractor_FilenameConvention import FilenameExtractor,FilenameExtractorManager
from Schema_Extractor_DirnameConvention import DirnameExtractor
from Operations import OperationEditor

import copy
import random
from DPGStage import DPGStage
from dataclasses import dataclass, field
import asyncio

def getMinimalTags(tags: list):

    _allTags = [x.rstrip() for x in tags if x !="" and x.count(" ")!=len(x)]
    _allTags.sort()
    minItems = list(set(_allTags))

    return minItems

# THings we can do:
'''

SOURCES:
    - in file name
    - given from file location (folder)
    - found in file somewhere (target cell somehow)
    - chosen manually

SOURCE CORRESPONDENCE
    - value in name doesn't need to go straight to output file; it can be filtered through a DICT
        just like we do for 

    1. populate columns with a single value predetermined by value from SOURCES
        - or from a correspondence dataset:
            whereby the value 
    2. 

Create correspondence dict for TAG
: if something in the INPUT file's column that is tagged
: matches a correspondence dict NAMED the tag name
: instead of sending the original values in the tag:


# determined base don 

'''

@dataclass
class EditorRow(DPGStage):
    name        :   str
    type        :   type
    tooltip     :   str
    items       :   list[str] = field(init=False)
    callback    :   callable = None


class SchemaColumnEditor(DPGStage):
       
    height: int  = 400
    tableColumnDefaultWidth = 100
    fixedWidthCutoff = 9
    fixedWidth = False

    rows: list[EditorRow]

    filenameExtractorManager:   FilenameExtractorManager
    dirnameExtractor        :   DirnameExtractor

    def getNumColumns(self):

        return len(self.schemaColNames)

    def main(self,**kwargs):

        self.schema = kwargs.get("schema")# NO DEFAULT HERE AS ITS ALREADY POPULATED BY SCHEMAEDITOR

        # Turn the complex dict obj into ez lists, which then save over the dict object in save
        self.schemaColNames = self.schema.outputSchemaDict.get("Column Name",[f'Test Name {x}' for x in range(1,6)])
        self.tags           = self.schema.outputSchemaDict.get("Tag",[f'Example {i}' for i,colName in enumerate(self.schemaColNames,1)])
        self.necessaryBox   = self.schema.outputSchemaDict.get("Necessary?",[False for i,colName in enumerate(self.schemaColNames,1)])
        self.manualCheckBox   = self.schema.outputSchemaDict.get("Manual Check?",[False for i,colName in enumerate(self.schemaColNames,1)])

        self.operations     = copy.deepcopy(self.schema.outputSchemaDict.get("Operations",[[] for i,colName in enumerate(self.schemaColNames,1)]))
        self.opDisplay     = [None for i,colName in enumerate(self.operations,1)]

        print(f'{self.operations=}')

        self.numColumns     = len(self.schemaColNames)

        self.filenameExtractorManager = kwargs.get("filenameExtractorManager")
        self.dirnameExtractor = kwargs.get("dirnameExtractor")

        self.rows = [
            EditorRow(
                name = "Column Name",
                type = str,
                tooltip = "This is what will be displayed in the header of the output file.",
                ),
            EditorRow(name = "Tag",
                type = str,                
                tooltip = "The shorthand name of what kinds of values this column contains.\nFor example:\n\t- UPC\n\t- Quantity\n\t- Description",
                callback = self.updateTags), 
            EditorRow(name = "Manual Check?",
                type = bool,
                tooltip = "If checked, the user will be required to validate the input during processing.\nUse this is the column is prone to formatting errors.\nKeep in mind that this will happen automatically for TAGs specified in Manual_Input_Tags.JSON"),
            EditorRow(name = "Necessary?",
                type = bool,
                tooltip = "If checked, new input schemas will be required to provide a column whose tag matches the rubric schema tag\neven if other operations will be done to the input column's values."),
            #EditorRow(name = "Derived from Filename?",
            #    type = bool,                
            #    tooltip = "If checked, this column's output will be populated by values derived from:\n\t - the file's name\n\t - the file's source directory\n\t - or a value manually chosen during the processing step"),
            EditorRow(name = "Operations",
                type = list,                
                tooltip = "This section provides an editor allowing us to populate columns in the output schema which are DERIVED from:\n\t- a combination of input columns\n\t- additional calculations made to individual input columns\n\t- or a combination of both"),
            ]

    def generate_id(self,**kwargs):

        with dpg.group(horizontal=True):

            self.color = dpg.add_color_button(height=self.height,width=30,default_value=self.schema.color)

            with dpg.group() as self._id:
      
                with dpg.child_window(horizontal_scrollbar=True,border=False,height=self.height):

                    with dpg.group():
                        dpg.add_text("When defining a rubric, we assume that:")
                        dpg.add_text("TAGs allow disparately and/or unintuitively named input and ouput columns to point to eachother via a proxy\n\t(This is computationally convenient even if column names happen to be identical and/or intuitive)",bullet=True)
                        dpg.add_text("the ouput schema may not be used in its entirety.\n\t(Certain fields will have no Tags and therefore no values -- at least generated by this program)",bullet=True)
                        dpg.add_text("certain tagged fields may be necessary for the converter to run.\n\t(Input rubrics will not be able to be saved without each necessary field being accounted for.)",bullet=True)
                        dpg.add_separator()
                        dpg.add_spacer(height=30)

                    with dpg.group(horizontal=True):

                        self.columnSetter = dpg.add_input_int(
                            label="Specify Columns Requested", # OR Add column before index
                            default_value=self.numColumns,
                            callback=self.change_columns,
                            on_enter =True,
                            min_value=1,min_clamped =True,
                            width=200)

                        '''self.columnIndexSetter = dpg.add_input_int(
                            label="",
                            width=150,
                            #@default_value=self.numColumns-1,
                            on_enter=True,
                            step=0,
                            min_value=0,min_clamped =True,
                            max_value=self.numColumns-1,max_clamped=True,
                            callback=self.addColumn,show=False)'''

                    with dpg.group(horizontal=True):

                        # Row Names Key
                        with dpg.child_window(width=120,border=False):
                            dpg.add_separator()
                            with dpg.table(header_row=True):

                                rowLabels = dpg.add_table_column(label=f'Index',width_fixed=True,width=self.tableColumnDefaultWidth)
                                for i,row in enumerate(self.rows):

                                    with dpg.table_row():
                                        with dpg.group(horizontal=True):
                                            #if i==0: dpg.add_separator()
                                            _rowLabel = dpg.add_text(row.name)
                                            
                                            if row.name=="Tag":
                                                _clear = dpg.add_button(label="x",callback=self.clearTags)
                                                with dpg.tooltip(_clear):
                                                    dpg.add_text("Reset all Tag inputs.")

                                            elif row.name=="Necessary?":
                                                _check = dpg.add_checkbox(default_value=False,callback=self.checkAll)
                                                with dpg.tooltip(_check):
                                                    dpg.add_text("If more fields than naught are important, check the following box and then start unchecking which ones will not be used.")

                                        with dpg.tooltip(_rowLabel):
                                            dpg.add_text(row.tooltip)

                        # Actual Schema Builder Table
                        with dpg.child_window(border=False,horizontal_scrollbar=True):

                            with dpg.group(horizontal=True) as self.columnEditor:
                                for row in self.rows:
                                    row.items = []     
    
    #def disableFilename(self,disabledState:bool):
    #    for item in self.rows[3].items:
    #        dpg.configure_item(item,default_value=False)

    def clearTags(self,sender):

        for row in self.rows:
            if row.name=="Tag":
                for item in row.items:
                    dpg.configure_item(item,default_value="")


        self.updateTags()

   
    # Updates
    def updateTags(self):

        _allTags = []

        for row in self.rows:
            if row.name=="Tag":

                _minItems = getMinimalTags(dpg.get_values(row.items))
                #_allTags = [x.rstrip() for x in dpg.get_values(row.items) if x !="" and x.count(" ")!=len(x)]
                #_allTags.sort()
                #minItems = list(set(_allTags))

                self.filenameExtractorManager.updateTagList(_minItems)
                self.dirnameExtractor.updateTagList(_minItems)
                # propogate to operation editors


    def checkAll(self,sender,app_data,user_data):

            for row in self.rows:
                if row.name=="Necessary?":
                    for checkbox in row.items:
                        dpg.configure_item(checkbox,default_value=app_data)

    #def notifyDerived(self,tagName: str):
        #for i,item in enumerate(self.rows[3].items):
        #    if dpg.get_value(self.rows[1].items[i])==tagName:
        #        dpg.configure_item(item,default_value=True)
    
    
    def openOperationEditor(self,sender,app_data,user_data):
        
        columnIndex = user_data["columnIndex"]
        op = user_data.get("operation",None)

        # What is best way to prevent people from opening up tabs of things that already exist?
        # 1. make a dict of {object.name : dpgwindow} and delete the old window if it exists before opening the new one?

        for row in self.rows:
            if row.name=="Tag":
                _minItems = getMinimalTags(dpg.get_values(row.items))

        if op: # if it already exists
            print("----- Operation already exists!@")
            _ = OperationEditor(schemaColumnEditor = self,columnIndex=columnIndex,operation=op,editingExisting=True,tags=_minItems)
        else:
            _ = OperationEditor(schemaColumnEditor = self,columnIndex=columnIndex,tags=_minItems)
        
        #self.singularWindows.update({"operation":_)

    def generateInputByFieldName(self,row: EditorRow,columnIndex):

        parent=self.columns[columnIndex]

        #======================================================
        if row.name == "Column Name":

            _default_value = self.schemaColNames[columnIndex]
            _callback = None
            _ = dpg.add_input_text(width=self.tableColumnDefaultWidth,default_value=_default_value,parent=parent,callback=_callback)
        #======================================================
        elif row.name =="Tag":
            try:
                _default_value = self.tags[columnIndex]
            except:
                _default_value=""
            _callback = row.callback
            _ = dpg.add_input_text(width=self.tableColumnDefaultWidth,default_value=_default_value,parent=parent,callback=_callback)
        #======================================================
        elif row.name=="Manual Check?":
            with dpg.group(horizontal=True,parent=parent):
                dpg.add_spacer(width=40)
                _default_value= self.manualCheckBox[columnIndex]#self.schema.outputSchemaDict.get("Necessary?")[columnIndex]
                _ = dpg.add_checkbox(default_value=_default_value)
        #======================================================
        elif row.name=="Necessary?":
            with dpg.group(horizontal=True,parent=parent):
                dpg.add_spacer(width=40)
                _default_value= self.necessaryBox[columnIndex]#self.schema.outputSchemaDict.get("Necessary?")[columnIndex]
                _ = dpg.add_checkbox(default_value=_default_value)
        #======================================================
        elif row.name=="Operations":

            with dpg.group(parent=parent) as _:
                _expandOps = dpg.add_button(label="+",width=self.tableColumnDefaultWidth,callback = self.openOperationEditor,user_data={"columnIndex":columnIndex})

                with dpg.group() as _opDisplay:
                    self.populateOps(columnIndex)

                self.opDisplay[columnIndex] = _opDisplay
            
        return _

    def populateOps(self,columnIndex):

        # WHY IS THIS NOT POPULATING CORRECTLY ON RE-OPEN?

        for i,op in enumerate(self.operations[columnIndex]):
            with dpg.group(horizontal=True):

                dpg.add_text(f"{i+1}",bullet=True)
                dpg.add_button(label="Edit",callback=self.openOperationEditor,user_data={"columnIndex":columnIndex,"operation":op})
                _x = dpg.add_button(label="X",callback=self.deleteOp,user_data={"columnIndex":columnIndex,"opIndex":i})

    def deleteOp(self,sender,app_data,user_data):
        columnIndex = user_data["columnIndex"]
        opIndex     = user_data["opIndex"]

        print(f'{self.operations=}')
        print(f'{user_data=}')

        # add confirmation

        #self.operations[columnIndex][opIndex] = []
        
        #self.operations[columnIndex].remove(self.operations[columnIndex][opIndex])
        
        #print(f'{self.operations=}')
        #print(f'{user_data=}')

        #dpg.delete_item(self.opDisplay[columnIndex])
        #dpg
        del self.operations[columnIndex][opIndex]

        dpg.delete_item(self.opDisplay[columnIndex],children_only=True)
        #print("deleted")
        #self.opDisplay[columnIndex]=None
        dpg.push_container_stack(self.opDisplay[columnIndex])
        self.populateOps(columnIndex=columnIndex)

    def oneColumn(self,columnIndex,**kwargs):

        parent=self.columns[columnIndex]

        insertion_index = kwargs.get("insertion_index",len(self.columns))

        with dpg.group(horizontal=True,parent=parent):

            _bf = dpg.add_button(arrow=True,direction=0,callback=self.addColumn,user_data=columnIndex)
            self.columnAdd.insert(insertion_index,_bf)

            with dpg.tooltip(_bf) as _tt: dpg.add_text(f"Add new column before Index {columnIndex}.")
            self.columnTooltips.insert(insertion_index,_tt)

            _= dpg.add_text(f"Index {columnIndex}")
            self.columnHeaders.insert(insertion_index,_)

            _x= dpg.add_button(label='X',callback=self.delete_column,user_data=columnIndex)
            self.columnRemove.insert(insertion_index,_x)

        dpg.add_separator(parent=parent)
            
        for row in self.rows:
            _newItem = self.generateInputByFieldName(row=row,columnIndex=columnIndex)
            row.items.insert(insertion_index,_newItem)


    async def populateTable(self):

        async def populateTableCols():

            self.columns = []

            for columnIndex in range(0,self.numColumns):
                _newCol = dpg.add_child_window(width=self.tableColumnDefaultWidth,parent=self.columnEditor,border=False)
                self.columns.append(_newCol)

        async def populateTableRows():

            self.columnAdd = []
            self.columnTooltips =[] #tooltips
            self.columnHeaders = []
            self.columnRemove = []

            for columnIndex in range(0,self.numColumns):

                self.oneColumn(columnIndex)

        await populateTableCols()
        await populateTableRows()
        self.updateTags()

    def addColumn(self,sender,app_data,user_data):
        # Whether through a pattern, or an input int for adding a column to a special index: 
        # add column @ that index

        index_to_add_before = user_data

        print(f"======================================= addColumn({user_data=}):")
        print(f'Before:\t{self.columns=}')
        print(f'Before:\t{self.schemaColNames=}')


        # create new column window
        _newCol = dpg.add_child_window(width=self.tableColumnDefaultWidth,parent=self.columnEditor,before=self.columns[index_to_add_before],border=False)
        
        # add to given lists
        self.columns.insert(index_to_add_before,_newCol)
        self.schemaColNames.insert(index_to_add_before,f'New_@_{index_to_add_before}')
        self.tags.insert(index_to_add_before,f'New_@_{index_to_add_before}')
        self.manualCheckBox.insert(index_to_add_before,False)
        self.necessaryBox.insert(index_to_add_before,False)
        self.operations.insert(index_to_add_before,[])
        self.opDisplay.insert(index_to_add_before,None)

        self.numColumns+=1

        print(f'After :\t{self.columns=}')
        print(f'After :\t{self.schemaColNames=}')

        # Update value displayed in column setter
        dpg.configure_item(self.columnSetter,default_value=self.numColumns)

        _newColIndex =self.columns.index(_newCol)
        print(f'Added @ {_newColIndex=}')
        self.oneColumn(_newColIndex,insertion_index=index_to_add_before)


        print(f'{self.columns[index_to_add_before:]}')
        print(f'{self.columns[_newColIndex:]}')

        # Now change the index labels of everything ahead of it: 
        #for i,column in enumerate(self.columns[index_to_add_before:],index_to_add_before):
        for i,column in enumerate(self.columns):
        
            # Add
            dpg.configure_item(self.columnAdd[i],user_data=i)

            # TT
            dpg.delete_item(self.columnTooltips[i])
            with dpg.tooltip(self.columnAdd[i]) as _tt: dpg.add_text(f"Add new column before Index {i}.")
            self.columnTooltips[i] = _tt

            # Headers
            dpg.configure_item(self.columnHeaders[i],default_value=f"Index {i}")

            # Remove
            dpg.set_item_user_data(self.columnRemove[i],user_data=i)


        if self.numColumns>=1:
            dpg.configure_item(self.columnRemove[0],show=True)

    def delete_column(self,sender,app_data,user_data):

        #print(f'{sender=}')
        #print(f'{app_data=}')
        #print(f'{user_data=}')

        try:
            self.schemaColNames.remove(self.schemaColNames[user_data])
            self.tags.remove(self.tags[user_data])
            self.manualCheckBox.remove(self.manualCheckBox[user_data])
            self.necessaryBox.remove(self.necessaryBox[user_data])
            self.operations.remove(self.operations[user_data])
            self.opDisplay .remove(self.opDisplay[user_data])

        except Exception as e:
            print("greater than schema index:",e)


        #print (f'{self.columnAdd=}')
        #print (f'{self.columnTooltips=}')

        # Move all things down
        for column in self.columns[user_data:]:
      
            columnIndex =  self.columns.index(column)

            dpg.configure_item(self.columnHeaders[columnIndex],default_value=f"Index {columnIndex-1}")
            dpg.set_item_user_data(self.columnRemove[columnIndex],user_data=columnIndex-1)

            #tooltip
            dpg.delete_item(self.columnTooltips[columnIndex])
            with dpg.tooltip(parent=self.columnAdd[columnIndex]) as _tt: dpg.add_text(f"Add new column before Index {columnIndex-1}.")
            self.columnTooltips[columnIndex] = _tt


        for row in self.rows:
            row.items.pop(user_data)

        # delete the item @ the chosen index
        dpg.delete_item(self.columns[user_data])

        self.columnAdd.remove(self.columnAdd[user_data])
        self.columnTooltips.remove(self.columnTooltips[user_data])
        self.columnHeaders.remove(self.columnHeaders[user_data])
        self.columnRemove.remove(self.columnRemove[user_data])

        self.columns.remove(self.columns[user_data])
        self.numColumns-=1
        dpg.configure_item(self.columnSetter,default_value=dpg.get_value(self.columnSetter)-1)
        #dpg.configure_item(self.columnIndexSetter,default_value=self.numColumns-1,max_value=self.numColumns-1)

        if self.numColumns==1:
            dpg.configure_item(self.columnRemove[0],show=False)
  
    def change_columns(self,sender,app_data):
        
        def add_columnToEnd(self,columnId):

            _newCol = dpg.add_child_window(width=self.tableColumnDefaultWidth,parent=self.columnEditor,border=False)
            self.columns.append(_newCol)
            _newColIndex =self.columns.index(_newCol)

            self.schemaColNames.append(f'New_@_{_newColIndex}')
            self.tags.append(f'New_@_{_newColIndex}')
            self.manualCheckBox.append(False)
            self.necessaryBox.append(False)
            self.operations.append([])
            self.opDisplay.append(None)


            self.numColumns+=1
            self.oneColumn(_newColIndex)

            if self.numColumns>=1:
                dpg.configure_item(self.columnRemove[0],show=True)

        def delete_columnFromEnd(self,columnId):

            try:
                self.schemaColNames.remove(self.schemaColNames[columnId])
                self.tags.remove(self.tags[columnId])
                self.manualCheckBox.remove(self.manualCheckBox[columnId])
                self.necessaryBox.remove(self.necessaryBox[columnId])
                self.operations.remove(self.operations[columnId])
                self.opDisplay .remove(self.opDisplay[columnId])
            except:
                print("greater than schema index")

            dpg.delete_item(self.columns[columnId])

            self.columnHeaders.remove(self.columnHeaders[columnId])
            self.columnRemove.remove(self.columnRemove[columnId])
            self.columns.remove(self.columns[columnId])

            self.numColumns-=1
            #dpg.configure_item(self.columnIndexSetter,default_value=self.numColumns-1,max_value=self.numColumns-1)
            #dpg.configure_item(self.columnSetter,default_value=dpg.get_value(self.columnSetter)-1)
            if self.numColumns==1:
                dpg.configure_item(self.columnRemove[0],show=False)

            for row in self.rows:
                row.items.pop()

        # Adding Columns
        if app_data > self.numColumns:
            for columnIndex in range(self.numColumns,app_data):
                add_columnToEnd(self,columnIndex)
             
        # Subtracting Columns
        elif app_data < self.numColumns:
            for columnIndex in range(app_data,self.numColumns):
                delete_columnFromEnd(self,columnIndex)

        self.numColumns = app_data

