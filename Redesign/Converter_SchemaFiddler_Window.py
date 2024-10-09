
from DPGStage import DPGStage,dpg_group

from dearpygui import dearpygui as dpg
from Rubric_Editor import RubricEditor
from Rubric import Rubric

from dataclasses import dataclass,field

from JSONtoDataclass import getUserDataTags

from Converter_ColumnZipper import zipFile

import File_Operations

from Vendorfile import InputFile

from Settings_DefaultPathing import DefaultPathing
from Settings_General import SettingsManager

class FiddlerCell(DPGStage):

    matchingRubric: Rubric
    inputFile: InputFile
    #schemas: list[Schema]

    height=200
    miniheight = 30

    tagComboPreviews : list[int]

    @dataclass
    class CellData:
        correct: bool = False
        doNotBatch: bool = False

    def main(self,**kwargs):
        
        self.inputFile = kwargs.get("inputfileObj")
        self.schema = kwargs.get("schema")

        #-----------------data
        self.celldata = self.CellData()

    def updateData(self,sender,app_data,user_data):

        field = user_data.get("field")
        setattr(self.celldata,field,app_data)

        def resize(mini):

            kwargs = {
                "item" : self._id,
                "height": self.height,
                "no_scrollbar":False,
                "no_scroll_with_mouse":False}


            if mini:

                kwargs.update({
                    "height":self.miniheight if not getattr(self.celldata,"doNotBatch") else self.miniheight*2,
                    "no_scrollbar":True,
                    "no_scroll_with_mouse":True
                    })
                  
            dpg.configure_item(**kwargs)

        if field=="doNotBatch":
            # Show/Hide the batched name input
            dpg.configure_item(self.nonbatchedName_Input,show=app_data)

        # Resize with mini = True if the correct checkbox is checked
        resize(mini=getattr(self.celldata,"correct"))

    #============================================================================
    # when re-generating... can you ensure that all currently-chosen options do not get re-written?
    def regenerate(self,sender):

        dpg.delete_item(self._id,children_only=True)
        dpg.push_container_stack(self._id)
        self.populate_id()

    def generate_id(self,**kwargs):
        
        with dpg.child_window(height=self.height,horizontal_scrollbar=True) as self._id:
            self.populate_id(**kwargs)

    def populate_id(self,**kwargs):
        #==================================================================
        with dpg.group(horizontal=True):

            _ = dpg.add_checkbox(callback=self.updateData,default_value=self.celldata.correct,user_data={"field":"correct"})
            with dpg.tooltip(_): dpg.add_text("Information correct?")

            dpg.add_spacer(width=10)

            with dpg.child_window(width=475,height=15,border=False,no_scrollbar=True,no_scroll_with_mouse=True):
                _ = dpg.add_text(self.inputFile.name,color=(60,200,100))#(127, 255, 212)) #(238, 75, 43)
                with dpg.tooltip(_): dpg.add_text(self.inputFile.fullPath)

            dpg.add_checkbox(label="Do not Batch",default_value=self.celldata.doNotBatch,callback=self.updateData,user_data={"field":"doNotBatch"})

        _batchName = self.inputFile.name.split(".")[0]
        self.nonbatchedName_Input = dpg.add_input_text(default_value=_batchName,label="Non-Batched Name",show=False)
        #==================================================================
        with dpg.tab_bar():
            #==================================================================
            with dpg.tab(label="Save Filters") as _save_filters_tab:

                with dpg.tooltip(_save_filters_tab): dpg.add_text("Adds the filter name to the end of each output file.\nIf multiple filters are chosen, multiples will be created.\nYou can specify what to do with particular tags.")

                _donotfilter = dpg.add_checkbox(label="Do not use filter this time.")

                with dpg.group() as filterGroup:

                    #dpg.add_text("Save Filters")

                    _filter_tags = getUserDataTags("filter")

                    def update_filter_sensitive_tag_choices(sender,app_data,user_data):
                
                        sensitive_tag_options = user_data.get("sensitive_tag_options")

                        if app_data!="All":
                            for sens_tag_option in sensitive_tag_options:
                                dpg.configure_item(sens_tag_option,show=False)
                        else: 
                            for sens_tag_option in sensitive_tag_options:
                                dpg.configure_item(sens_tag_option,show=True)

            
                    for key,val in _filter_tags.items():
                        with dpg.group(horizontal=True):
                            _filterCombo = dpg.add_combo(items=["All"]+val["options"],default_value="Both",label=key.upper(),callback=update_filter_sensitive_tag_choices,width=100)
                    
                            _tag_choices = {}

                            for sens_tag in val["sensitive_tags"]:
                    
                                _sensitive_option = dpg.add_combo(items=["Divide","Copy"],default_value="Divide",label=f'<{sens_tag}>',width=100)
                                with dpg.tooltip(_sensitive_option): dpg.add_text("Remainders will be prioritized reading from the left of Filters.JSON")
                                _tag_choices.update({key:_sensitive_option})

                            dpg.set_item_user_data(_filterCombo,user_data={"sensitive_tag_options":_tag_choices})
               
                dpg.set_item_callback(_donotfilter,callback=lambda sender,app_data: dpg.configure_item(filterGroup,show=not app_data))

            #==================================================================
            with dpg.tab(label="Input",show=False):
                with dpg.group(horizontal=True):

                    dpg.add_text("Name    :")

                    for column in self.inputFile.header:
                        dpg.add_input_text(default_value=column,width=100,enabled=False)
                        dpg.add_spacer(width=10)
                        dpg.add_text("|")

            #==================================================================
            matchingRubric = None
            with dpg.tab(label="Rubrics"):
                with dpg.group(horizontal=True):
                    dpg.add_color_button(default_value = self.schema.color,enabled=False,height=30,width=30)
                    dpg.add_text(f"For Schema:\t{self.schema.name}")
                    
                    
                if self.inputFile.header not in [rubric.editorNames for rubric in list(self.schema.rubrics.values())]:
                    dpg.add_text("NO MATCH!!!")
                    dpg.add_button(label="Add input as rubric!",callback=self.openPrepopulatedRubricEditor)

                else:

                    matchingRubricIndex = [rubric.editorNames for rubric in list(self.schema.rubrics.values())].index(self.inputFile.header)

                    # ENSURE THAT THE INDEX IS THE SAME EACH TIME, PERHAPS BY SORTING?
                    #for i in range(0,15):
                    ##    a = list(self.schema.rubrics.values())
                    #    print (a)
                       
                    matchingRubric = list(self.schema.rubrics.values())[matchingRubricIndex]

                    self.showRubric(matchingRubric)

                    setattr(self,"matchingRubric",matchingRubric)
            
            #==================================================================
            if matchingRubric:

                self.tagComboPreviews = {}
                #==================================================================
                with dpg.tab(label="Naming Convention Check"):
                    dpg.add_text("TODO: This is hard, as incoming names are messy\nneed to find a way to have the system guess\nuse the field guesser i made, too\nmaybe write a correspondence system",color=(255,64,25))
                    dpg.add_text("Do I need to import the custom obj builder from tracker?",bullet=True,color=(255,64,25))

                    if self.schema.filenameConventions:
                        for fns in self.schema.filenameConventions:

                            with dpg.group() as fnsExtractor:

                                fns.showExtraction(name=self.inputFile.name)
                #==================================================================
                with dpg.tab(label="MANUAL INPUT REQUIRED"):
       
                    _defaultFirst = getattr(SettingsManager.getSettings(),"setDefaultFirst")

                    with dpg.group(horizontal=True):

                        _manualTags = getUserDataTags('manual')
                        _formatTags = getUserDataTags('formatting')
                        _fncTags    = getUserDataTags('fnc')

                        # v v v v v v v v v v v v v v v v v v v v v
                        # this isnt even true: a manual input tag should be one that's either from the manual
                        # OR ones that 
                        # i think it should JUST be ones that are manually input required
                        # maybe "Manual input check requested"

                        #<><><><>#<><><><>#<><><><>#<><><><>#<><><><>#<><><><>#<><><><>#<><><><>#<><><><>#<><><><>#<><><><>#<><><><>#<><><><>#
                        #        #        #        #        #        #        #        #        #        #        #        #        #        #
                        #<><><><>#<><><><>#<><><><>#<><><><>#<><><><>#<><><><>#<><><><>#<><><><>#<><><><>#<><><><>#<><><><>#<><><><>#<><><><>#

                        #for tag in matchingRubric.editorTags:
                        for i,tag in enumerate(self.schema.outputSchemaDict["Tag"]):
                            
                            # If the tag is in the manual Input JSON
                            if tag in list(_manualTags.keys()):

                                with dpg.group():

                                    # ----------------------------------------------------
                                    with dpg.group(horizontal=True):

                                        dpg.add_text(f'{tag}:')
                                        _valuePreview = dpg.add_text(
                                            default_value=getattr(self.celldata,f'{tag}_preview',''),
                                            color=(160,160,250))

                                    # ----------------------------------------------------
                                    _tagCombo = dpg.add_combo(
                                        items           =   list(_manualTags[tag].keys()),
                                        width           =   150,
                                        default_value   =   getattr(self.celldata,tag,"~"),
                                        user_data       =   {"tag":tag,"tagDict":_manualTags[tag],"previewDestination":_valuePreview},
                                        callback        =   self.updateTagPreview)

                                    # ----------------------------------------------------
                                    if _defaultFirst:

                                        dpg.configure_item(_tagCombo,default_value = list(_manualTags[tag].keys())[0])

                                        self.updateTagPreview(
                                            sender=_tagCombo,
                                            app_data = list(_manualTags[tag].keys())[0],
                                            user_data = dpg.get_item_user_data(_tagCombo)
                                            )
                                    # ----------------------------------------------------
                                #self.tagCombos.update({tag:_tagCombo})
                                self.tagComboPreviews.update({tag:_valuePreview})

                                continue

                            #if self.schema.outputSchemaDict["Manual Check?"][i]: #if there is a check required
                            #for fns in self.schema.filenameConventions[0]:

                            # ======================================================
                            # FILENAME CONVENTIONS ALWAYS REQUIRE A CHECK
                            if self.schema.filenameConventions:
                                
                                fns = self.schema.filenameConventions[0]

                                print(f"CHECKIN....!!! {tag=}....{list(_fncTags.keys())=}")

                                if tag in list(_fncTags.keys()): # HAVE THESE BE FORMATTING KEYS INSTEAD?

                                    if tag in list(self.tagComboPreviews.keys()):
                                        # this will skip over duplicates... but how to ensure the formatted value for this one ends up there, too?
                                        continue

                                    with dpg.group():

                                        # ----------------------------------------------------
                                        with dpg.group(horizontal=True):

                                            dpg.add_text(f'{tag}:')
                                            _valuePreview = dpg.add_text(
                                                default_value=getattr(self.celldata,f'{tag}_preview',''),
                                                color=(160,160,250))

                                        # ----------------------------------------------------
                                        _tagFilter = dpg.add_input_text(
                                            width           =   150,
                                            default_value   =   "",
                                            #user_data       =   {"tag":tag,"tagDict":_manualTags[tag],"previewDestination":_valuePreview},
                                            callback        =   self.updateComboAndPreview)
                                        # ----------------------------------------------------

                                    
                                        _tagCombo = dpg.add_combo(
                                            items           =   list(_fncTags[tag].keys()), # can make thew full thing
                                            width           =   150,
                                            default_value   =   getattr(self.celldata,tag,"~"),
                                            user_data       =   {"tag":tag,"tagDict":_fncTags[tag],"previewDestination":_valuePreview},
                                            callback        =   self.updateTagPreview)
                                        # ----------------------------------------------------
                                        dpg.set_item_user_data(_tagFilter,user_data = {"tag":tag,"tagDict":_fncTags[tag],"combo":_tagCombo,"items": list(_fncTags[tag].keys())})
                                        # ----------------------------------------------------
                                        # try to predict default value

                                        _val_from_filename = fns.getVal(name=self.inputFile.name,tag=tag)

                                        try: 
                                            _split = _val_from_filename.split(" ")
                                            print(f'{_split=}')
                                            for x in list(_fncTags[tag].keys()):
                                                if x.lower().startswith(_split[0].lower()):
                                                    _val_from_filename = x
                                        except Exception as e: 
                                            print(e)
                                       
                                        dpg.configure_item(_tagCombo,default_value = _val_from_filename)

                                        if _val_from_filename in list(_fncTags[tag].keys()):

                                            app_data = _val_from_filename

                                        else:
                                            app_data = "~Not found~"

                                        self.updateTagPreview(
                                            sender      =   _tagCombo,
                                            app_data    =   app_data,
                                            user_data   =   dpg.get_item_user_data(_tagCombo)
                                            )

                                        # ----------------------------------------------------
    
                                    self.tagComboPreviews.update({tag:_valuePreview})
                                    continue

                    # does it match a rubric?
                    # suggest nearest rubrics
            #==================================================================
            '''with dpg.collapsing_header(label="ALL RUBRICS"):
                for rubric_name in list(self.schema.rubrics.keys()):

                rubric = self.schema.rubrics[rubric_name]

                self.showRubric(rubric)'''
            #==================================================================
            with dpg.tab(label="OUTPUT",show=False):
                dpg.add_text(self.schema.name)

                with dpg.group(horizontal=True):

                    dpg.add_text("Name    :")

                    for i,column in enumerate(self.schema.outputSchemaDict["Column Name"]):

                        dpg.add_input_text(default_value=column,width=100,enabled=False)
                        _ = dpg.add_checkbox(default_value=self.schema.outputSchemaDict["Necessary?"][i],enabled=False)
                        with dpg.tooltip(_):
                            dpg.add_text("Necessary?")
                            dpg.add_separator()
                            dpg.add_text("Rows in input file without this value will be skipped\nand instead added to an incomplete staged file.")
                        dpg.add_spacer(width=10)
                        dpg.add_text("|")

                with dpg.group(horizontal=True):

                    dpg.add_text("Tag     :")

                    for column in self.schema.outputSchemaDict["Tag"]:

                        dpg.add_input_text(default_value=column,width=100,enabled=False)
                        dpg.add_spacer(width=10+dpg.get_item_width(_)+27)
                        dpg.add_text("|")

   
            #EditorRow(name = = "Column Name",
            #EditorRow(name = "Tag",
            #EditorRow(name = "Necessary?",
            #EditorRow(name = "Operations",

                dpg.add_separator()

   
    #============================================================================

    def updateComboAndPreview(self,sender,app_data,user_data):

        # Generic function for updating the ITEMS in the combo AND the text field that reflects the final value going to be used for the specified TAG's manual check

        #<><><><><><><><>#<><><><><><><><>#<><><><><><><><>#
        _tag = user_data.get("tag")
        _tagDict = user_data.get("tagDict")
        _combo = user_data.get("combo")
        #<><><><><><><><>#<><><><><><><><>#<><><><><><><><>#
        #---------------------------------------------------
        # change the contents of the list depending on filtering
        all_items = user_data.get("items")
        all_items.sort()

        if app_data =="":
            final_items = all_items
            default_value = "~"
        else:
            final_items = []
            for i,item in enumerate(all_items):
                #print(f'\t{item}')
                if app_data.lower() in item.lower():
                    final_items.append(item) 
            print(final_items[:4])

            try:
                default_value = final_items[0]
            except Exception as e:
                default_value = "~"

        dpg.configure_item(_combo,items = final_items,default_value = default_value)

        #---------------------------------------------------
        # now update the preview
        self.updateTagPreview(
            sender      =   _combo,
            app_data    =   default_value,
            user_data   =   dpg.get_item_user_data(_combo)
            )

    def updateTagPreview(self,sender,app_data,user_data):
        
        # Generic function for updating the text field that reflects the final value going to be used for the specified TAG's manual check
        
        try:

            setattr(self.celldata,user_data["tag"],app_data)
            setattr(self.celldata,f'{user_data["tag"]}_preview',user_data["tagDict"][app_data])
            dpg.configure_item(user_data["previewDestination"],default_value=user_data["tagDict"][app_data])

        except Exception as e:
             dpg.configure_item(user_data["previewDestination"],default_value="ERR")
        
    #============================================================================
    @dpg_group("→")
    def testGroupDec(self):

        for x in range(3):
            dpg.add_checkbox()

    #============================================================================
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



    def openPrepopulatedRubricEditor(self,sender,app_data,user_data):
        
        RubricEditor(schema = self.schema, fromFiddlerCell = self)#,preScannedFile = self.inputFile)

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

            _extensionRemoved = file.name.split('.')[0]

            _name+=_extensionRemoved+"_"

        return _name

    def generate_id(self,**kwargs):

        with dpg.window(height=600,width=700,no_scrollbar=False):

            dpg.add_button(label="Process",width=150,height=75,callback=self.process)

            with dpg.tab_bar():

                # Here is what puts all the schemas into ONE TAB BAR
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

                            _ = FiddlerCell(inputfileObj=inputfileObj,schema=schema)
                            self.fiddlerCells[i].append(_)



    def process(self):

        print("#==========================\nSaving Files::::\n")

        #=======================================================================================
        def validate_through_cells(i,schema):

            for cell in self.fiddlerCells[i]:

                # If it has been selected as complete
                if cell.celldata.correct:
                    for tag,tagPreview in cell.tagComboPreviews.items():
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

            # each schema will have its own output file(s)
                
            _batchedRows = [schema.outputSchemaDict["Column Name"]]
            _batchedNonExistent = True

            #--------------------------------------------
            for cell in self.fiddlerCells[i]:

                if cell.celldata.correct:

                    _output_rows = zipFile(
                        schema          =   schema,
                        inputFile       =   cell.inputFile,
                        matchingRubric  =   cell.matchingRubric,
                        includeHeader   =   cell.celldata.doNotBatch,
                        manualTagCombos =   cell.tagComboPreviews)

                    if cell.celldata.doNotBatch:
                        _files_as_2D_lists.update({dpg.get_value(cell.nonbatchedName_Input):_output_rows})
                    else:
                        [_batchedRows.append(x) for x in _output_rows]
                        if _batchedNonExistent: _batchedNonExistent = False
            #--------------------------------------------

            if not _batchedNonExistent:
                _files_as_2D_lists.update({dpg.get_value(self.batchedNames[i]):_batchedRows})
    
            return _files_as_2D_lists

        def saveOutput(i,schema,files: list[list]):

            _saveLocation = getattr(schema,"outputOverride",DefaultPathing.getPaths().output)
            
            for fileName,rows in files.items():

                try:
                    print("------------ SO FAR SO GOOD")
                    print(f"Attempting to save file <{fileName}> @ <{_saveLocation}>")
                    print("------------------")

                    for saveFormat,val in schema.supported_formats.items():

                        _saveName = f'{_saveLocation}\\{fileName}.{saveFormat}'

                        if val:

                            print(f'Saving as:\t{_saveName}')

                            # Here is where you could factory pattern.... give each an execute function.... delay execution
                            if saveFormat=='xlsx':
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

        #=======================================================================================

        for i,schema in enumerate(self.schemas):

            # If every cell's correct box is marked FALSE... nothing is selected.              
            if [cell.celldata.correct for cell in self.fiddlerCells[i]].count(False) == len(self.fiddlerCells[i]):
                with dpg.window(popup=True):
                    dpg.add_text("No Files Selected.")
            
            else:

                # If the validation fails, the process stops so that user can make the required changes. Will happen until the end.
                # MAYBE can collect the errors all @ once.
                if validate_through_cells(i, schema):

                    _files = processCells(i, schema)

                    saveOutput(i, schema, files=_files)

            