
from DPGStage import DPGStage

from dearpygui import dearpygui as dpg
from Rubric_Editor import RubricEditor
from Rubric import Rubric

from dataclasses import dataclass,field

from JSONtoDataclass import getManualInputTags,getFormattedTags,getFncTags

from Converter_ColumnZipper import zipFile

import File_Operations

from Vendorfile import InputFile

from Settings_DefaultPathing import DefaultPathing
from Settings_General import SettingsManager

class FiddlerCell(DPGStage):

    #matchingRubric: Rubric

    height=400
    miniheight = 30

    @dataclass
    class cellData:
        correct: bool = False
        doNotBatch: bool = False

        #def setCustomAttr(self,key,value):

        #    setAttr()

    def main(self,**kwargs):
        
        self.inputFile = kwargs.get("inputfileObj")
        self.schemas = kwargs.get("schemas")

        #-----------------data
        self.cd = self.cellData()

    def updateData(self,sender,app_data,user_data):

        field = user_data

        setattr(self.cd,field,app_data)

        if field=="doNotBatch":
            dpg.configure_item(self.nonbatchedName_Input,show=app_data)

            if app_data:
                miniheight = self.miniheight*2
                if self.cd.correct:
                    dpg.configure_item(self._id,height=miniheight)
            else:
                miniheight = self.miniheight
                if self.cd.correct:
                    dpg.configure_item(self._id,height=miniheight)
    #============================================================================
    # when re-generating... can you ensure that all currently-chosen options do not get re-written?
    def regenerate(self,sender):

        dpg.delete_item(self._id,children_only=True)
        dpg.push_container_stack(self._id)
        self.populate_container()

    def establish_container_id(self,**kwargs):
        pass

    def populate_container(self,**kwargs):
        
        # do schema here!!!!!!!!!!!!!!!!
        # for i,schema in enumerate(self.schemas):

            with dpg.group(horizontal=True):

                #dpg.add_button(label="Refresh",callback=self.regenerate)

                _ = dpg.add_checkbox(callback=self.resize,default_value=self.cd.correct)
                with dpg.tooltip(_): dpg.add_text("Information correct?")

                dpg.add_spacer(width=10)

                '''with dpg.child_window(border=False,width=600,height=60):

                    with dpg.collapsing_header(label=self.inputFile.name) as self.collapsing:#,color=(60,200,100)):
                        pass'''

                with dpg.child_window(width=475,height=15,border=False,no_scrollbar=True,no_scroll_with_mouse=True):
                    _ = dpg.add_text(self.inputFile.name,color=(60,200,100))#(127, 255, 212)) #(238, 75, 43)
                    with dpg.tooltip(_): dpg.add_text(self.inputFile.fullPath)

                #dpg.add_spacer(width=100)
                dpg.add_checkbox(label="Do not Batch",default_value=self.cd.doNotBatch,callback=self.updateData,user_data="doNotBatch")

            _batchName = self.inputFile.name.split(".")[0]
            self.nonbatchedName_Input = dpg.add_input_text(default_value=_batchName,label="Non-Batched Name",show=False)

            dpg.add_separator()
            #==================================================================
            with dpg.collapsing_header(label="INPUT"):

                with dpg.group(horizontal=True):

                    dpg.add_text("Name    :")

                    for column in self.inputFile.header:
                        dpg.add_input_text(default_value=column,width=100,enabled=False)
                        dpg.add_spacer(width=10)
                        dpg.add_text("|")

                # does it match a rubric?
                # suggest nearest rubrics

            #==================================================================
            matchingRubric= None
            with dpg.collapsing_header(label="Matching RUBRICS"):
                for schema in self.schemas:

                    with dpg.group(horizontal=True):
                        dpg.add_color_button(default_value = schema.color,enabled=False,height=30,width=30)
                        dpg.add_text(f"For Schema:\t{schema.name}")
                    
                    
                    if self.inputFile.header not in [rubric.editorNames for rubric in list(schema.rubrics.values())]:
                        dpg.add_text("NO MATCH!!!")
                        dpg.add_button(label="Add input as rubric!",callback=self.openPrepopulatedRubricEditor,user_data=schema)

                    else:

                        matchingRubricIndex = [rubric.editorNames for rubric in list(schema.rubrics.values())].index(self.inputFile.header)

                        # ENSURE THAT THE INDEX IS THE SAME EACH TIME, PERHAPS BY SORTING?
                        #for i in range(0,15):
                        ##    a = list(schema.rubrics.values())
                        #    print (a)

                        
                        #print (f'Index of {matchingRubricIndex=}')

                        matchingRubric = list(schema.rubrics.values())[matchingRubricIndex]

                        #print(f'{matchingRubric=}')
                        #print(f'{schema.rubrics[matchingRubric.name]=}')
                        
                        self.showRubric(matchingRubric)

                        setattr(self,"matchingRubric",matchingRubric)
            
            #==================================================================
            if matchingRubric:

                self.tagCombos = {}

                with dpg.collapsing_header(label="Naming Convention Check"):
                    for schema in self.schemas:

                        dpg.add_text("TODO: This is hard, as incoming names are messy\nneed to find a way to have the system guess\nuse the field guesser i made, too\nmaybe write a correspondence system",color=(255,64,25))
                        dpg.add_text("Do I need to import the custom obj builder from tracker?",bullet=True,color=(255,64,25))

                        if schema.filenameConventions:
                            for fns in schema.filenameConventions:

                                with dpg.group() as fnsExtractor:

                                    fns.showExtraction(name=self.inputFile.name)

                with dpg.collapsing_header(label="MANUAL INPUT REQUIRED"):
                    
                    _defaultFirst = getattr(SettingsManager.getSettings(),"setDefaultFirst")

                    for schema in self.schemas:

                        with dpg.group(horizontal=True):

                            _manualTags = getManualInputTags()
                            _formatTags = getFormattedTags()
                            _fncTags    = getFncTags()
                            # v v v v v v v v v v v v v v v v v v v v v
                            # this isnt even true: a manual input tag should be one that's either from the manual
                            # OR ones that 
                            # i think it should JUST be ones that are manually input required
                            # maybe "Manual input check requested"


                            #for tag in matchingRubric.editorTags:
                            for i,tag in enumerate(schema.outputSchemaDict["Tag"]):
                            
                                if tag in list(_manualTags.keys()):

                                    with dpg.group():
                                        with dpg.group(horizontal=True):

                                            dpg.add_text(f'{tag}:')
                                            _valuePreview = dpg.add_text(
                                                default_value=getattr(self.cd,f'{tag}_preview',''),
                                                color=(160,160,250))

                                        _tagCombo = dpg.add_combo(
                                            items           =   list(_manualTags[tag].keys()),
                                            width           =   150,
                                            default_value   =   getattr(self.cd,tag,"~"),
                                            user_data       =   {"tag":tag,"tagDict":_manualTags[tag],"previewDestination":_valuePreview},
                                            callback        =   self.updateTagPreview)

                                        if _defaultFirst:

                                            dpg.configure_item(_tagCombo,default_value = list(_manualTags[tag].keys())[0])

                                            self.updateTagPreview(
                                                sender=_tagCombo,
                                                app_data = list(_manualTags[tag].keys())[0],
                                                user_data = dpg.get_item_user_data(_tagCombo)
                                                )

                                    #self.tagCombos.update({tag:_tagCombo})
                                    self.tagCombos.update({tag:_valuePreview})

                                    continue

                                #if schema.outputSchemaDict["Manual Check?"][i]: #if there is a check required
                                #for fns in schema.filenameConventions[0]:
                                if schema.filenameConventions:
                                
                                    fns = schema.filenameConventions[0]

                                    if tag in list(_fncTags.keys()): # HAVE THESE BE FORMATTING KEYS INSTEAD?

                                        if tag in list(self.tagCombos.keys()):
                                            # this will skip over duplicates... but how to ensure the formatted value for this one ends up there, too?
                                            continue

                                        with dpg.group():
                                            with dpg.group(horizontal=True):

                                                dpg.add_text(f'{tag}:')
                                                _valuePreview = dpg.add_text(
                                                    default_value=getattr(self.cd,f'{tag}_preview',''),
                                                    color=(160,160,250))

                                            _tagCombo = dpg.add_combo(
                                                items           =   list(_fncTags[tag].keys()), # can make thew full thing
                                                width           =   150,
                                                default_value   =   getattr(self.cd,tag,"~"),
                                                user_data       =   {"tag":tag,"tagDict":_fncTags[tag],"previewDestination":_valuePreview},
                                                callback        =   self.updateTagPreview)

                                                # try to predict default value

                                            _val_from_filename = fns.getVal(name=self.inputFile.name,tag=tag)

                                            dpg.configure_item(_tagCombo,default_value = _val_from_filename)

                                            if fns.getVal(name=self.inputFile.name,tag=tag) in list(_fncTags[tag].keys()):
                                                app_data = _val_from_filename
                                            else:
                                                app_data = "~Not found~"

                                            print(f'{app_data=}')

                                            self.updateTagPreview(
                                                sender      =   _tagCombo,
                                                app_data    =   app_data,
                                                user_data   =   dpg.get_item_user_data(_tagCombo)
                                                )


    
                                        self.tagCombos.update({tag:_valuePreview})
                                        continue

                    # does it match a rubric?
                    # suggest nearest rubrics
            #==================================================================
            '''with dpg.collapsing_header(label="ALL RUBRICS"):
                for schema in self.schemas:
                    for rubric_name in list(schema.rubrics.keys()):

                        rubric = schema.rubrics[rubric_name]

                        self.showRubric(rubric)'''
            #==================================================================
            with dpg.collapsing_header(label="OUTPUT"):
                
                for schema in self.schemas:
                    dpg.add_text(schema.name)

                    with dpg.group(horizontal=True):

                        dpg.add_text("Name    :")

                        for i,column in enumerate(schema.outputSchemaDict["Column Name"]):

                            dpg.add_input_text(default_value=column,width=100,enabled=False)
                            _ = dpg.add_checkbox(default_value=schema.outputSchemaDict["Necessary?"][i],enabled=False)
                            with dpg.tooltip(_):
                                dpg.add_text("Necessary?")
                                dpg.add_separator()
                                dpg.add_text("Rows in input file without this value will be skipped\nand instead added to an incomplete staged file.")
                            dpg.add_spacer(width=10)
                            dpg.add_text("|")

                    with dpg.group(horizontal=True):

                        dpg.add_text("Tag     :")

                        for column in schema.outputSchemaDict["Tag"]:

                            dpg.add_input_text(default_value=column,width=100,enabled=False)
                            dpg.add_spacer(width=10+dpg.get_item_width(_)+27)
                            dpg.add_text("|")

   
            #EditorRow(name = = "Column Name",
            #EditorRow(name = "Tag",
            #EditorRow(name = "Necessary?",
            #EditorRow(name = "Operations",



                dpg.add_separator()

    def generate_id(self,**kwargs):
        
        with dpg.child_window(height=self.height,horizontal_scrollbar=True) as self._id:

            self.populate_container(**kwargs)
    #============================================================================

    def updateTagPreview(self,sender,app_data,user_data):
        
        try:

            print(f'{user_data["tagDict"]=}')
            print(f'{app_data=}')

            setattr(self.cd,user_data["tag"],app_data)
            setattr(self.cd,f'{user_data["tag"]}_preview',user_data["tagDict"][app_data])


            dpg.configure_item(user_data["previewDestination"],default_value=user_data["tagDict"][app_data])

        except Exception as e:
             dpg.configure_item(user_data["previewDestination"],default_value="ERR")
        #print(getattr(self.cd,app_data))
        

    def showRubric(self,rubric):

        dpg.add_text(f"Rubric Name:\t{rubric.name}")

        with dpg.group(horizontal=True):
            dpg.add_text("Name    :")
                            
            for column_name in rubric.editorNames:
                dpg.add_input_text(default_value=column_name,width=100,enabled=False)
                dpg.add_spacer(width=10)
                dpg.add_text("|")

        with dpg.group(horizontal=True):
            dpg.add_text("Tag     :",color=(37, 150, 190))
                            
            for column_name in rubric.editorNames:
                dpg.add_input_text(default_value=rubric.col_to_tag_correspondence[column_name],width=100,enabled=False)
                dpg.add_spacer(width=10)
                dpg.add_text("|")

    def resize(self,sender,app_data,user_data):

        self.cd.correct = app_data

        if app_data:
            dpg.configure_item(
                self._id,
                height                  =   self.miniheight,
                no_scrollbar            =   True,
                no_scroll_with_mouse    =   True)
        else:
            dpg.configure_item(
                self._id,
                height                  =   self.height,
                no_scrollbar            =   False,
                no_scroll_with_mouse    =   False)

    def openPrepopulatedRubricEditor(self,sender,app_data,user_data):
        
        RubricEditor(schema = user_data, fromFiddlerCell = self)#,preScannedFile = self.inputFile)

class FiddlerWindow(DPGStage):
    
    filesToProcessDict: dict
    
    def main(self,**kwargs):

        self.schemas = kwargs.get("schemas")
        self.filesToProcessDict = kwargs.get("filesToProcessDict")

        self.fiddlerCells = [[] for schema in self.schemas]
        self.batchedNames = []

    def suggestName(self,schema):
        # Should be able to turn off! (add to settings)
        _name = ""

        for file in self.filesToProcessDict[schema.name]:

            #print(file)

            _extensionRemoved = file.name.split('.')[0]

            _name+=_extensionRemoved+"_"

        return _name

    def generate_id(self,**kwargs):

        #print(self.filesToProcess)

        with dpg.window(height=600,width=700,no_scrollbar=False):

            dpg.add_button(label="Process",width=150,height=75,callback=self.process)

            #with dpg.child_window(height=30) as key:
            #    dpg.add_text("Check boxes")


            with dpg.tab_bar():

                for i,schema in enumerate(self.schemas):

                    with dpg.tab(label=schema.name):

                        with dpg.group(horizontal=True):
                            _batchedName = dpg.add_input_text(default_value = self.suggestName(schema),width=500)
                            _ = dpg.add_input_text(default_value=".XXX",label="Save Name",enabled=False,width=75)
                            with dpg.tooltip(_):
                                for formatName,val in schema.supported_formats.items():
                                    if val:
                                        dpg.add_text(f'.{formatName}')
                        self.batchedNames.append(_batchedName)

                        _to_edit_items = self.filesToProcessDict[schema.name]

                        for inputfileObj in _to_edit_items:

                            _ = FiddlerCell(inputfileObj=inputfileObj,schemas=self.schemas)
                            self.fiddlerCells[i].append(_)



    def process(self):

        print("#==========================\nSaving Files::::\n")



        def validate_through_cells(i,schema):

            #for i,schema in enumerate(self.schemas):

            for cell in self.fiddlerCells[i]:

                # If it has been selected as complete
                if cell.cd.correct:
                    for tag,tagPreview in cell.tagCombos.items():
                        print(f'{tag}\t:\t{dpg.get_value(tagPreview)}')

                        #------------------------------------------------------------------
                        # If there is a manual input requested that has not been fulfilled
                        if not dpg.get_value(tagPreview):
                            with dpg.window(popup=True):
                                dpg.add_text("Error:")

                                with dpg.group(horizontal=True):
                                    dpg.add_text(f"Manual input for <",color = (255,64,25))
                                    dpg.add_text(f"{tag}")
                                    dpg.add_text(f"> is requested at <",color = (255,64,25))
                                    dpg.add_text(f"{cell.inputFile.name}")
                                    dpg.add_text(f">",color = (255,64,25))
                                return False


                        #------------------------------------------------------------------
                        # If there is no matching rubric

                        #print(getattr(cell.inputFile,"matchingRubric")

                        if not getattr(cell,"matchingRubric",False):
                            with dpg.window(popup=True):
                                dpg.add_text("Error:")

                                with dpg.group(horizontal=True):
                                    dpg.add_text(f"No rubric found for <",color = (255,64,25))
                                    dpg.add_text(f"{cell.inputFile.name}")
                                    dpg.add_text(f"> although its box was checked.",color = (255,64,25))
                                return False

            return True

        def processCells(i,schema):

            _files_as_2D_lists = {}

            #for i,schema in enumerate(self.schemas):
                # each schema will have its own output file(s)
                
            _batchedRows = [schema.outputSchemaDict["Column Name"]]
            _batchedNonExistent = True

            #--------------------------------------------
            for cell in self.fiddlerCells[i]:

                if cell.cd.correct:

                    _output_rows = zipFile(
                        schema          =   schema,
                        inputFile       =   cell.inputFile,
                        matchingRubric  =   cell.matchingRubric,
                        includeHeader   =   cell.cd.doNotBatch)

                    if cell.cd.doNotBatch:
                        #_files_as_2D_lists.append(_output_rows)
                        _files_as_2D_lists.update({dpg.get_value(cell.nonbatchedName_Input):_output_rows})
                    else:
                        _batchedRows.append(_output_rows)
                        if _batchedNonExistent: _batchedNonExistent = False
            #--------------------------------------------

            if not _batchedNonExistent:
                _files_as_2D_lists.update({dpg.get_value(self.batchedNames[i]):_batchedRows})
    
            return _files_as_2D_lists

        def saveOutput(i,schema,files: list[list]):

            _saveLocation = getattr(schema,"outputOverride",DefaultPathing.getPaths().output)
            
            for fileName,rows in files.items():

                #print(fileName)
                #print(rows)

                try:
                    print("------------ SO FAR SO GOOD")
                    print(f"Attempting to save file <{fileName}> @ <{_saveLocation}>")
                    print("------------------")

                    for saveFormat,val in schema.supported_formats.items():

                        _saveName = f'{_saveLocation}\\{fileName}.{saveFormat}'

                        if val:

                            print(f'Saving as:\t{_saveName}')

                            if saveFormat=='xlsx':

                                print("<><><><><><><><><><><><><><><><><><><><><><>")
                                for row in rows:
                                    print(row)

                                File_Operations.list_to_excel(rows,_saveName)

                            if saveFormat=='csv':

                                File_Operations.list_to_csv(rows,_saveName)

                            if saveFormat=='gsheet':
                                with dpg.window(popup=True):
                                    dpg.add_text("GSHEET NOT YET IMPLEMENTED")


                except Exception as e:
                    print("------------ ERROR")
                    print(f"Error saving file <{fileName}> @ <{_saveLocation}>")
                    print(f"Error text:\t{e}")
                    print("------------------")


        for i,schema in enumerate(self.schemas):


            if validate_through_cells(i, schema):
                _files = processCells(i, schema)

                saveOutput(i, schema, files=_files)

            