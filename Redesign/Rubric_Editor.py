
from DPGStage import DPGStage
from dearpygui import dearpygui as dpg
from File_Operations import csv_to_list,excel_to_list,mkdirWrapper
from File_Selector import FileSelector
from Vendorfile import InputFile

from Operations import Operation, OperationEditor
from Schema_Editor_Columns import getMinimalTags

from typing import Type
import string
import copy

from Rubric import Rubric
from dataclasses import dataclass

from Color_Manager import randomColor

default_settings_path = "Redesign\\Settings"
default_schema_path = "Redesign\\Schemas"

@dataclass
class RubricOp:
    tag: str
    calc: str
    combos: list[int]

class RubricEditor(DPGStage): 
 
    label="Test Adding a Rubric"

    height = 700
    width=1000

    schema: Type["Schema"]
    rubric: Rubric

    names: list[str]
    items: list[int]

    null_item = '~'

    def main(self,**kwargs):

        self.schema=kwargs.get("schema")

        self.rubric = kwargs.get("rubric",Rubric())

        self.fromFiddlerCell = kwargs.get("fromFiddlerCell",None)

        self.names = []
        self.tag_combos = []
        self.overrides = []
        self.overrideDict = {}
        #self.overrideValues = []

        self.dncOverride = None
        self.fncOverride = None

        self.rubricOps = []
        self.rubricCalcs = []
        self.rubricOpsCombos=[[]]
        self.rubricGroups = []
        self.rubricDeleteBtns = []

        #=====================================================================
        # Look into how to make supported types separate from FilenameConventions
        self.allSupportedinputTypes = []
        if self.schema.filenameConventions:
            # defaulting to [0]
            for fnc in self.schema.filenameConventions:
                self.allSupportedinputTypes.extend(fnc.supportedExtensions)

    
        #=====================================================================
        # TAGS
        _uncleanedTags = self.schema.outputSchemaDict["Tag"]
        _cleanedTags = getMinimalTags(_uncleanedTags)
        #_cleanedTags = [t for t in _uncleanedTags if t!=""]
        self.all_tags = _cleanedTags
        self.tags = copy.deepcopy(self.all_tags)
        self.tags.insert(0,self.null_item)

        self.overrideDirnameConventionTags(sender=None,app_data=self.rubric.dncOverride)
        self.overrideFilenameConventionTags(sender=None,app_data=self.rubric.fncOverride)

        # Necessary
        _necessary = self.schema.outputSchemaDict["Necessary?"]
        print (zip(_uncleanedTags,_necessary))
        self.necessaryTagsReminder = zip(_uncleanedTags,_necessary)
        #=====================================================================

    def generate_id(self,**kwargs):

        with dpg.window(height=self.height,width=self.width,label=self.label) as self._id:
             #"Column Name",
             #"Tag",
             #"Necessary?",
             #"Derived from Filename?",
             #"Operations",
             #def generateCells(self):
        
            with dpg.group(horizontal=True):
                dpg.add_text("Adding an Input File to the Rubric: ")
                dpg.add_input_text(default_value=self.schema.name,enabled=False)
            dpg.add_separator

            with dpg.group(horizontal=True):
                with dpg.group():
                    with dpg.group(horizontal=True):
                        self.nameInput = dpg.add_input_text(label="Name of Rubric",default_value=self.rubric.name,width=150)
                        dpg.add_text("*",color=(255,0,0))
                    self.desc = dpg.add_input_text(label="Description",width=150,height=80,multiline=True,default_value=self.rubric.description)
                    with dpg.group(horizontal=True):
                        _c = dpg.add_color_button(width=50,default_value=self.schema.color,enabled=False)
                        with dpg.tooltip(_c): dpg.add_text(f"{self.schema.name}'s Color")
                        self.color = dpg.add_color_button(width=92,default_value=self.rubric.color,callback=self.changeColor)
                        with dpg.tooltip(self.color): dpg.add_text(f"This Rubric's Color")
                        dpg.add_text("Color")
                with dpg.group():
                    dpg.add_button(label="Save",callback=self.addRubricToSchema)
                #self.scansFrom = dpg.add_combo(label="Scans From",items = self.scannableLocations,default_value=self.scannableLocations[0],width=300)
            dpg.add_separator()
            #===============================================
            # Display DirnameConvention here
            #   does the imported file come from this dirname? y/n
            if self.schema.dirnameConvention:
                dpg.add_text("DirnameConvention Found!")
                self.dncOverride = dpg.add_checkbox(label="Allow rubric to override Dirname Convention-sourced tags?",default_value=self.rubric.dncOverride,callback=self.overrideDirnameConventionTags)
                if self.rubric.dncOverride:
                    self.overrideDirnameConventionTags(sender=None,app_data=self.rubric.dncOverride)
            else:
                dpg.add_text("No Dirname Convention used in this Schema")

            #===============================================
            dpg.add_separator()
            # Display Filenme Convention:
            #   based on filename: show its breakdown into the tag list:
            if self.schema.filenameConventions:
                dpg.add_text(f"{len(self.schema.filenameConventions)} Filename Conventions Found!")
                self.fncOverride = dpg.add_checkbox(label="Allow rubric to override Filename Convention-sourced tags?",default_value=self.rubric.fncOverride,callback=self.overrideFilenameConventionTags)
                if self.rubric.fncOverride:
                    self.overrideFilenameConventionTags(sender=None,app_data=self.rubric.fncOverride)
            else:
                dpg.add_text("No Filename Conventions used in this Schema")

            #===============================================
            dpg.add_separator()
            dpg.add_text("Necessary Fields")
            dpg.add_text(list(self.necessaryTagsReminder))
            #===============================================
            dpg.add_separator()
            self.suggest = dpg.add_checkbox(label="Suggest Tags based on Input?",default_value=True)
            #===============================================
            dpg.add_separator()

            if not self.fromFiddlerCell:
                dpg.add_button(label="Load File",callback=self.loadFile) 
                dpg.add_button(label="Build Input File Schema") 
            else:
                self.rubric.editorNames = self.fromFiddlerCell.inputFile.header
            #===============================================
            dpg.add_separator()
        
            with dpg.child_window(border=False,horizontal_scrollbar=True) as self.rubricEditor:
                pass
                try:
                    if self.rubric.editorNames:
                        self.populateCols(header=self.rubric.editorNames)
                except Exception as e:
                    print("Probably loading new")
                    print(e)

    def populateCols(self,header):

        dpg.push_container_stack(self.rubricEditor)

        #=====================================================
        # INPUT FILE HEADER
        with dpg.group(horizontal=True) as headerGroup:
            with dpg.child_window(border=False,no_scrollbar=True,no_scroll_with_mouse=False,width=150,height=25) as self.widthFixer:
                dpg.add_text("Imported File Header:")
            dpg.add_spacer(width=20)
            dpg.add_text("|")
        
        #=====================================================
        # TAG SELECTION
        with dpg.group(horizontal=True) as TagGroup:
            with dpg.child_window(border=False,no_scrollbar=True,no_scroll_with_mouse=False,width=150,height=25):
                dpg.add_text("Available Tags ::::::")
            dpg.add_spacer(width=20)
            dpg.add_text("|")
        
        dpg.add_separator()
        with dpg.group(horizontal=True) as self.overrideGroup:
            pass

        for colName in header:

            component_width=8*len(f"{colName}")
            if component_width < 50: component_width+=40
            
            _name = dpg.add_input_text(default_value=f"{colName}", readonly=True,parent=headerGroup,width=component_width)
            self.names.append(_name)

            with dpg.group(horizontal=True,parent=headerGroup):
                dpg.add_spacer(width=20)
                dpg.add_text("|")
                dpg.add_spacer(width=20)
            #===================================================================
            default_tag = self.tags[0]

            if self.suggest:
                if colName in self.tags:
                    default_tag = self.tags[self.tags.index(colName)]
                else:
                    pass
                    # do other suggest mechanics here
    
            _combo = dpg.add_combo(items=self.tags,default_value = default_tag,parent=TagGroup,width=component_width,callback=self.displayDerivedOps)
            self.tag_combos.append(_combo)

            try:
                print(f'{self.rubric.col_to_tag_correspondence=}')
                print(f'{colName=}')
                print(f'{self.rubric.col_to_tag_correspondence[colName]=}')
                dpg.configure_item(_combo,default_value=self.rubric.col_to_tag_correspondence[colName])
            except Exception as e:
                print("Prob loading new")
                print(e)

            with dpg.group(horizontal=True,parent=TagGroup):
                dpg.add_spacer(width=20)
                dpg.add_text("|")
                dpg.add_spacer(width=20)
            #===================================================================
            
        self.displayDerivedOps()
        
        dpg.push_container_stack(self.rubricEditor)
        dpg.add_separator()
        dpg.add_text("Calculate Output Schema tags as derived from two or more input Rubric columns")


        with dpg.group() as self.rubricOpGroup:
            pass
            
            '''with dpg.group(horizontal=True):
                _ro = dpg.add_combo(items=self.tags,default_value=self.tags[0],width=dpg.get_item_width(self.widthFixer),callback=self.craftRubricOp,user_data=header)
            _calc = dpg.add_input_text(width=dpg.get_item_width(self.widthFixer))

            self.rubricOps.append(_ro)
            self.rubricCalcs.append(_calc)'''


        _addOpBtn = dpg.add_button(label="+",width=dpg.get_item_width(self.widthFixer),callback=self.addOp,user_data={"header":header})
        
        if getattr(self.rubric,"ops",None):
            for i,op in enumerate(self.rubric.ops):
                self.addOp(sender=_addOpBtn,app_data=None,user_data={"header":header,"op":op})
        else:
            self.addOp(sender=_addOpBtn,app_data=None,user_data={"header":header})

                    
    def overrideDirnameConventionTags(self,sender,app_data,user_data=True):
        # This function removes the tags sourced by the FILENAME convention from the available tags.
        # Can be rerun with app_data as TRUE to override, whereby the rubric's tags will override the CONVENTION's tags

        if not self.schema.dirnameConvention: return


        override = app_data
       
        _removed = []

        # Determine if its overridden
        if not override:

            _dirConventionTags = self.schema.dirnameConvention.tags

            for i,tag in enumerate(_dirConventionTags):
                if tag in self.tags:
                    _removed.append(tag)
                    del self.tags[self.tags.index(tag)]
        else:
            self.tags = copy.deepcopy(self.all_tags)
            self.tags.insert(0,self.null_item)

            if self.fncOverride and user_data: # if the box exists, get its value
                self.overrideFilenameConventionTags(sender=None,app_data=dpg.get_value(self.fncOverride),user_data=False)
        
                
        # now update all the combos
        # ------------- RESET TAG COMBOS
        _indexes = []
        for i,combo in enumerate(self.tag_combos):

            _val = dpg.get_value(combo)

            if _val in _removed:
                _indexes.append(i)
                dpg.configure_item(combo,items=self.tags,default_value=self.tags[0])
            else:
                dpg.configure_item(combo,items=self.tags)
        # ------------- RESET TAG COMBOS
        _rubricIndexes = []
        for i,combo in enumerate(self.rubricOps):

            _val = dpg.get_value(combo)

            if _val in _removed:
                _rubricIndexes.append(i)
                dpg.configure_item(combo,items=self.tags,default_value=self.tags[0])
            else:
                dpg.configure_item(combo,items=self.tags)

        if _indexes or _rubricIndexes:
            with dpg.window(popup=True):
                if _indexes:
                    dpg.add_text("Tags changed at column index(es):",color=(255,0,0))
                    for i in _indexes:
                        dpg.add_text(f'{i+1}',bullet=True)
                if _rubricIndexes:
                    dpg.add_text("Tags changed at rubric index(es):",color=(255,0,0))
                    for i in _rubricIndexes:
                        dpg.add_text(f'{i+1}',bullet=True)

        try:
            self.displayDerivedOps()
        except:
            pass

    def overrideFilenameConventionTags(self,sender,app_data,user_data=True):
        # This function removes the tags sourced by the FILENAME convention from the available tags.
        # Can be rerun with app_data as TRUE to override, whereby the rubric's tags will override the CONVENTION's tags

        # As we currently expect a list, but want to change to 1, defaulting to [0]

        if not self.schema.filenameConventions[0]: return

        override = app_data
       
        _removed = []

        # Determine if its overridden
        if not override:

            _fileConventionTags = self.schema.filenameConventions[0].tags

            for i,tag in enumerate(_fileConventionTags):
                if tag in self.tags:
                    _removed.append(tag)
                    del self.tags[self.tags.index(tag)]
        else:
            self.tags = copy.deepcopy(self.all_tags)
            self.tags.insert(0,self.null_item)

            if self.fncOverride and user_data: # if the box exists, get its value
                self.overrideDirnameConventionTags(sender=None,app_data=dpg.get_value(self.dncOverride),user_data=False)
        
                
        # now update all the combos
        # ------------- RESET TAG COMBOS
        _indexes = []
        for i,combo in enumerate(self.tag_combos):

            _val = dpg.get_value(combo)

            if _val in _removed:
                _indexes.append(i)
                dpg.configure_item(combo,items=self.tags,default_value=self.tags[0])
            else:
                dpg.configure_item(combo,items=self.tags)
        # ------------- RESET TAG COMBOS
        _rubricIndexes = []
        for i,combo in enumerate(self.rubricOps):

            _val = dpg.get_value(combo)

            if _val in _removed:
                _rubricIndexes.append(i)
                dpg.configure_item(combo,items=self.tags,default_value=self.tags[0])
            else:
                dpg.configure_item(combo,items=self.tags)

        if _indexes or _rubricIndexes:
            with dpg.window(popup=True):
                if _indexes:
                    dpg.add_text("Tags changed at column index(es):",color=(255,0,0))
                    for i in _indexes:
                        dpg.add_text(f'{i+1}',bullet=True)
                if _rubricIndexes:
                    dpg.add_text("Tags changed at rubric index(es):",color=(255,0,0))
                    for i in _rubricIndexes:
                        dpg.add_text(f'{i+1}',bullet=True)

        try:
            self.displayDerivedOps()
        except:
            pass


    

    def changeColor(self,sender,app_data):
        
        def propColors(sender,app_data):

            _newColor = tuple(i*255 for i in app_data)
            dpg.configure_item(self.color,default_value=_newColor)

        with dpg.window(popup=True):
            dpg.add_color_picker(
                no_small_preview=False,
                no_side_preview = True,
                callback=propColors)

    


    def loadFile(self):

        # Loads a file for populating the columns
        # maybe need to do the same thing as SchemaEditor

        def manipulateFile():

            dpg.delete_item(self.fs._id)
            _filepath = self.fs.selectedFile 

            readArray = []
            error = ''

            try:
                if _filepath[-3:] == 'csv':
                    readArray = csv_to_list(_filepath)
                elif _filepath[-4:] == 'xlsx':
                    readArray = excel_to_list(_filepath)
        
            except Exception as e:
                with dpg.window(popup=True):
                    dpg.add_text(e)

            header = readArray.pop(0)    
            self.populateCols(header)
   


        if self.allSupportedinputTypes:
            self.fs = FileSelector(
                label="Load Spreadsheet file to begin column correspondence with desired output schema",
                nextStage=manipulateFile,
                inputTypes = self.allSupportedinputTypes)
        else:
            self.fs = FileSelector(
                label="Load Spreadsheet file to begin column correspondence with desired output schema",
                nextStage=manipulateFile)

    def setGetOverrideVals(self):

        self.overrideDict = {}

        #self.overrideValues = []

        for i, box in enumerate(self.overrides):

            # will be either a DPG ITEM or NONE

            if box:
                #self.overrideValues.append(dpg.get_value(box))
                self.overrideDict.update({dpg.get_value(self.tag_combos[i]):dpg.get_value(box)})
            #else:
                #self.overrideValues.append(None)

        return self.overrideDict

    def displayDerivedOps(self):
        #----------------------------
        def peek(sender,app_data,user_data):
            
            _opName = app_data
            _ops = user_data

            for op in _ops: 
                if op.name==_opName:
                    OperationEditor(operation=op,tags=self.schema.outputSchemaDict["Tag"],enabled=False)
                    #_operation = self.schema.outputSchemaDict["Operations"][]
            
            #
        #----------------------------
        # See if the values already exist
        #self.setGetOverrideVals()
        self.overrideDict = self.rubric.tag_to_override_correspondence
        #----------------------------
        # Reset group
        dpg.delete_item(self.overrideGroup,children_only=True)
        dpg.push_container_stack(self.overrideGroup)
        #----------------------------
        # generate row info
        with dpg.child_window(border=False,no_scrollbar=True,no_scroll_with_mouse=False,width=dpg.get_item_width(self.widthFixer),height=25):
            dpg.add_text("Derived Value Override")
        dpg.add_spacer(width=20)
        dpg.add_text("|")

        #----------------------------
        # populate override boxes if the tags are seen
        for i,tagCombo in enumerate(self.tag_combos):


            print("<><><><><><><><><><><><>")
            _tag = dpg.get_value(tagCombo)
            #print(f'{_tag=}')

            _indexes_where_there_are_operations = []

            # This to make sure if one has operation, we get both
            for ii,tag in enumerate(self.schema.outputSchemaDict["Tag"]):
                if tag==_tag:

                    if self.schema.outputSchemaDict["Operations"][ii]:
                        _indexes_where_there_are_operations.append(ii)

            with dpg.child_window(width=dpg.get_item_width(tagCombo)+20,height=25,border=False):

                #print(f'{self.schema.outputSchemaDict["Operations"]=}')

                #print(f'{_indexes_where_there_are_operations=}')

                if _indexes_where_there_are_operations:

                    _ops = self.schema.outputSchemaDict["Operations"][_indexes_where_there_are_operations[0]]

                    with dpg.group(horizontal=True):

                        _opPeeker = dpg.add_combo(items=[op.name for op in _ops],default_value="~",callback=peek,width=40,user_data=_ops)
                        with dpg.tooltip(_opPeeker): dpg.add_text("Peek")

                        try:
                            _default = self.overrideDict.get(_tag,None)#self.overrideValues[i]
                            if _default == None: 
                                # AKA if there's no value here before, but there is one now; override is TRUE by default
                                _default = True
                        except:
                            _default = True

                        _overrideBox = dpg.add_checkbox(default_value=_default)
                        with dpg.tooltip(_overrideBox):
                            dpg.add_text("If checked, this will override the calculations used to\ngenerate the values in the output schema.")
                            dpg.add_separator()
                            dpg.add_text("If checked, the values in this column will be used first.",bullet=True)
                            dpg.add_text("If un-checked, the values in this column will be used second.",bullet=True)
                            dpg.add_text("If no values are found, it will be left blank OR with an error\nif the box is checked 'Necessary'.",bullet=True)
                        self.overrides.append(_overrideBox)
                else:
                    self.overrides.append(None) # needed to keep indexes the same
            
            dpg.add_spacer(width=0)
            dpg.add_text("|")
            dpg.add_spacer(width=20)


    
    def saveOp(self,index):

        if dpg.get_value(self.rubricOps[index]) == self.null_item:
            return None

        _formatted_combos = dpg.get_values(self.rubricOpsCombos[index])

        for i, combo in enumerate(_formatted_combos):
            if combo==self.null_item:
                _formatted_combos[i]=None

        print(_formatted_combos)

        #_formatted_combos = list(map(lambda x: x.replace(self.null_item, None), _formatted_combos))
        
        _ = RubricOp(
            tag=dpg.get_value(self.rubricOps[index]),
            calc=dpg.get_value(self.rubricCalcs[index]),
            combos=_formatted_combos)

        return _


    def deleteOp(self,sender,app_data,user_data):

        index = user_data.get("index")

        # Delete the UI
        dpg.delete_item(self.rubricGroups[index])

        # Delete the data
        self.rubricOps.pop(index)
        self.rubricDeleteBtns.pop(index)
        self.rubricCalcs.pop(index)
        self.rubricOpsCombos.pop(index)
        self.rubricGroups.pop(index)

        for i,op in enumerate(self.rubricOps):

            dpg.set_item_user_data(self.rubricDeleteBtns[i],user_data={"index":i})

    def addOp(self,sender,app_data,user_data):

        header = user_data.get("header")
        op = user_data.get("op",None)

        dpg.push_container_stack(self.rubricOpGroup)
        
        with dpg.group() as _rubGroup:

            with dpg.group(horizontal=True):
                _ro = dpg.add_combo(
                    items           =   self.tags,
                    default_value   =   op.tag if op else self.null_item,
                    width           =   dpg.get_item_width(self.widthFixer),
                    callback        =   self.craftRubricOp,
                    user_data       =   {"header":header})

            self.rubricOps.append(_ro)

            with dpg.group(horizontal=True):

                _deleteOp = dpg.add_button(label="X",callback=self.deleteOp,user_data={"index":self.rubricOps.index(_ro)},width=30)
                with dpg.tooltip(_deleteOp): dpg.add_text("Delete this operation?")
                _calcDF = op.calc if op else ''
                _calc = dpg.add_input_text(width=dpg.get_item_width(self.widthFixer)-35,default_value=_calcDF)
                with dpg.tooltip(_calc): dpg.add_text("Write your calculation here using algebraic expressions.\tThe value will be calculated using this field, populated\nby the terms to the right.")

        self.rubricDeleteBtns.append(_deleteOp)
        self.rubricCalcs.append(_calc)
        self.rubricOpsCombos.append([])
        self.rubricGroups.append(_rubGroup)

        if op:
            self.craftRubricOp(sender=_ro,app_data=op.tag,user_data={"header":header,"op":op})

    def craftRubricOp(self,sender,app_data,user_data):

        header = user_data.get("header")
        op = user_data.get("op",None)

        # Check versus other column tags
        if app_data in dpg.get_values(self.tag_combos) and app_data!=self.null_item:
            with dpg.window(popup=True):
                with dpg.group(horizontal=True):
                    dpg.add_text(f"The tag <",color=(255,0,0))
                    dpg.add_text(f"{app_data}")
                    dpg.add_text(f"> is already selected as originating from the rubric column # <",color=(255,0,0))
                    dpg.add_text(f"{dpg.get_values(self.tag_combos).index(app_data)+1}")
                    dpg.add_text(f">.",color=(255,0,0))

            dpg.configure_item(sender,default_value=self.tags[0])
            return 

                
        # check vs other rubrics
        _tempRubrics = copy.deepcopy(self.rubricOps)
        print(type(_tempRubrics))
        print(_tempRubrics)
        del _tempRubrics[_tempRubrics.index(sender)]
        if app_data in dpg.get_values(_tempRubrics) and app_data!=self.null_item:
            with dpg.window(popup=True):
                with dpg.group(horizontal=True):
                    dpg.add_text(f"The tag <",color=(255,0,0))
                    dpg.add_text(f"{app_data}")
                    dpg.add_text(f"> is already selected as originating from the rubric operation # <",color=(255,0,0))
                    dpg.add_text(f"{dpg.get_values(_tempRubrics).index(app_data)+1}")
                    dpg.add_text(f">.",color=(255,0,0))

            dpg.configure_item(sender,default_value=self.tags[0])
            del _tempRubrics
            return 

        # If okay:
        dpg.push_container_stack(dpg.get_item_parent(sender))
        dpg.add_spacer(width=20)
        dpg.add_text("|")

        # For each column, let user choose
        for i,colName in enumerate(header):

            _items = list(string.ascii_lowercase[:len(header)])
            _combo = dpg.add_combo(items=_items,default_value = op.combos[i] if op and op.combos[i]!="None" else self.null_item,width=dpg.get_item_width(self.names[i]))
            self.rubricOpsCombos[self.rubricOps.index(sender)].append(_combo)
            dpg.add_spacer(width=20)
            dpg.add_text("|")
            dpg.add_spacer(width=20)



    def addRubricToSchema(self):
        #=========================================
        # Reset any schemas that were used to build this one
        try:
            # If the old rubric has a different name, save over it.
            del self.schema.rubrics[self.rubric.name]
        except Exception as e:
            print ("Probably new")
            print(e)

        #=========================================
        # Format and create correspondence dict for use in IMPORTER I/O column zipper

        _names = dpg.get_values(self.names)
        _items = dpg.get_values(self.tag_combos)
 
        for x in _items:
            if x==self.null_item: x = "" 

        _col_to_tag_correspondence = dict(zip(_names,_items))

        #=========================================

        def peekRubric(sender,app_data,user_data):
            rubric = user_data["rubric"]

            RubricEditor(schema=self.schema,rubric=rubric)

        for rubricName,rubric in self.schema.rubrics.items():

            if _names == rubric.editorNames and self.rubric.name!=rubric.name:
                with dpg.window(popup=True):
                    dpg.add_text("Warning",color=(255,0,0))
                    dpg.add_separator()
                    dpg.add_text("A rubric with this input header already exists inside of this schema!")
                    dpg.add_button(label="Go to this rubric.",callback=peekRubric,user_data={"rubric":rubric})

                return 

            elif self.rubric.name==rubric.name:
                with dpg.window(popup=True):
                    dpg.add_text("Warning",color=(255,0,0))
                    dpg.add_separator()
                    dpg.add_text("A rubric with this name already exists inside of this schema!")
                    dpg.add_button(label="Go to this rubric.",callback=peekRubric,user_data={"rubric":rubric})

                return 


        #=========================================
        # Update all fields.... in the future this would be automated with use of 
        #   unique I/O correspondence dict

        '''if self.rubric.name != dpg.get_value(self.nameInput):
            try:
                # If the old rubric has a different name, save over it.
                del self.schema.rubrics[self.rubric.name]
            except Exception as e:
                print ("Probably new")
                print(e)

        del self.schema.rubrics[self.rubric.name]'''

        self.rubric.name = dpg.get_value(self.nameInput)
        self.rubric.description = dpg.get_value(self.desc)
        self.rubric.color = dpg.get_value(self.color)
        self.rubric.col_to_tag_correspondence = _col_to_tag_correspondence
        self.rubric.editorNames = _names
        self.rubric.editorTags = _items
        self.rubric.dncOverride = dpg.get_value(self.dncOverride)
        self.rubric.fncOverride = dpg.get_value(self.fncOverride)
        self.rubric.tag_to_override_correspondence = self.setGetOverrideVals()
        #=========================================

        self.rubric.ops = []

        for i,op in enumerate(self.rubricOps):

            _savedOp = self.saveOp(i)
            
            if _savedOp:
                self.rubric.ops.append(_savedOp)

        
        #=========================================
        self.schema.rubrics.update({self.rubric.name:self.rubric})
        self.schema.save(default_schema_path)
        print("Rubric Saved!!!")

        dpg.delete_item(self._id)
        self.schema.refreshRubrics()

        if self.fromFiddlerCell:
            
            self.fromFiddlerCell.regenerate(sender=self._id)


if __name__=="__main__":
    x=10
    y=5
    z = eval("x + y")
    print(z)

    _items = string.ascii_lowercase[:28]
    print(list(_items))