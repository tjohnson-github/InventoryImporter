
from DPGStage import DPGStage

from dearpygui import dearpygui as dpg
from Rubric_Editor import RubricEditor

from dataclasses import dataclass,field

from JSONtoDataclass import getManualInputTags


class FiddlerCell(DPGStage):

    height=400
    miniheight = 36

    @dataclass
    class cellData:
        correct: bool = False

    def main(self,**kwargs):
        
        self.inputFile = kwargs.get("inputfileObj")
        self.schemas = kwargs.get("schemas")

        #-----------------data
        self.cd = self.cellData()



    #============================================================================
    # when re-generating... can you ensure that all currently-chosen options do not get re-written?
    def regenerate(self,sender):

        dpg.delete_item(self._id,children_only=True)
        dpg.push_container_stack(self._id)
        self.populate_container()

    def establish_container_id(self,**kwargs):
        pass

    def populate_container(self,**kwargs):
        
            with dpg.group(horizontal=True):

                dpg.add_button(label="Refresh",callback=self.regenerate)

                _ = dpg.add_checkbox(callback=self.resize,default_value=self.cd.correct)
                with dpg.tooltip(_): dpg.add_text("Information correct?")

                dpg.add_spacer(width=30)

                _ = dpg.add_text(self.inputFile.name,color=(60,200,100))#(127, 255, 212)) #(238, 75, 43)
                with dpg.tooltip(_): dpg.add_text(self.inputFile.fullPath)

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

                        print (f'Index of {matchingRubricIndex=}')

                        matchingRubric = list(schema.rubrics.values())[matchingRubricIndex]

                        print(matchingRubric)

                        print(schema.rubrics[matchingRubric.name])
                        
                        self.showRubric(matchingRubric)
            
            #==================================================================
            if matchingRubric:

                self.tagCombos = {}

                with dpg.collapsing_header(label="MANUAL INPUT REQUIRED"):

                    with dpg.group(horizontal=True):

                        _manualTags = getManualInputTags()

                        for tag in matchingRubric.editorTags:
                            
                            if tag in list(_manualTags.keys()):

                                with dpg.group():
                                    with dpg.group(horizontal=True):
                                        dpg.add_text(f'{tag}:')
                                        _valuePreview = dpg.add_text(color=(160,160,250))
                                    _tagCombo = dpg.add_combo(
                                        items=list(_manualTags[tag].keys()),
                                        width=150,
                                        default_value="~",
                                        user_data={"tagDict":_manualTags[tag],"previewDestination":_valuePreview},
                                        callback=self.updateTagPreview)

                                #self.tagCombos.update({tag:_tagCombo})
                                self.tagCombos.update({tag:_valuePreview})


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
        
        with dpg.child_window(height=self.height) as self._id:

            self.populate_container(**kwargs)
    #============================================================================

    def updateTagPreview(self,sender,app_data,user_data):
        
        dpg.configure_item(user_data["previewDestination"],default_value=user_data["tagDict"][app_data])
        

    def showRubric(self,rubric):

        dpg.add_text(f"Rubric Name:\t{rubric.name}")

        with dpg.group(horizontal=True):
            dpg.add_text("Name    :")
                            
            for column_name in rubric.editorNames:
                dpg.add_input_text(default_value=column_name,width=100,enabled=False)
                dpg.add_spacer(width=10)
                dpg.add_text("|")

        with dpg.group(horizontal=True):
            dpg.add_text("Tag     :")
                            
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
    
    
    def main(self,**kwargs):

        self.schemas = kwargs.get("schemas")
        self.filesToProcess = kwargs.get("filesToProcess")

        self.fiddlerCells = []

    def generate_id(self,**kwargs):

        print(self.filesToProcess)

        with dpg.window(height=600,width=700,no_scrollbar=False):

            dpg.add_button(label="Process",width=150,height=75,callback=self.process)

            with dpg.child_window(height=30) as key:
                dpg.add_text("Check boxes")

            with dpg.tab_bar():

                for schema in self.schemas:

                    with dpg.tab(label=schema.name):

                        _to_edit_items = self.filesToProcess[schema.name]

                        for inputfileObj in _to_edit_items:

                            _ = FiddlerCell(inputfileObj=inputfileObj,schemas=self.schemas)
                            self.fiddlerCells.append(_)



    def process(self):

        print("#==========================\nProcessing::::\n")

        for cell in self.fiddlerCells:

            print(cell.inputFile.name)
            print(cell.cd)

            if cell.cd.correct:
                for tag,tagPreview in cell.tagCombos.items():
                    print(f'{tag}\t:\t{dpg.get_value(tagPreview)}')
