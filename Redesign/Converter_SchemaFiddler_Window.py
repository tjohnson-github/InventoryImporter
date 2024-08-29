
from DPGStage import DPGStage

from dearpygui import dearpygui as dpg


class FiddlerCell(DPGStage):

    height=400

    def main(self,**kwargs):
        
        self.inputFile = kwargs.get("inputfileObj")
        self.schemas = kwargs.get("schemas")

    def generate_id(self,**kwargs):
        
        with dpg.child_window(height=self.height) as self._id:

            with dpg.group(horizontal=True):

                _ = dpg.add_checkbox(callback=self.resize)
                with dpg.tooltip(_): dpg.add_text("Information correct?")

                dpg.add_spacer(width=30)

                _ = dpg.add_text(self.inputFile.name)
                with dpg.tooltip(_): dpg.add_text(self.inputFile.fullPath)

            dpg.add_separator()

            dpg.add_text(self.inputFile)

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
            with dpg.collapsing_header(label="Matching RUBRICS"):
                for schema in self.schemas:

                    with dpg.group(horizontal=True):
                        dpg.add_color_button(default_value = schema.color,enabled=False,height=30,width=30)
                        dpg.add_text(f"For Schema:\t{schema.name}")
                    
                    
                    if self.inputFile.header not in [rubric.editorNames for rubric in list(schema.rubrics.values())]:
                        dpg.add_text("NO MATCH!!!")
                        dpg.add_button(label="Add input as rubric!")

                '''for schema in self.schemas:
                    for rubric_name in list(schema.rubrics.keys()):
                        rubric = schema.rubrics[rubric_name]
                        
                        if self.inputFile.header == rubric.editorNames:
                            dpg.add_text("MATCH!!!")
                            dpg.add_text(f"{rubric_name=}")
                        else:
                            dpg.add_text("NO MATCH!!!")
                            dpg.add_button(label="Add input as rubric!")'''

            #==================================================================
            with dpg.collapsing_header(label="ALL RUBRICS"):
                for schema in self.schemas:
                    for rubric_name in list(schema.rubrics.keys()):

                        rubric = schema.rubrics[rubric_name]

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
                            dpg.add_spacer(width=10)
                            dpg.add_text("|")

                    '''with dpg.group(horizontal=True):

                        dpg.add_text("Required:")


                        for column in schema.outputSchemaDict["Necessary?"]:

                            dpg.add_input_text(default_value=column,width=100,enabled=False)
                            dpg.add_spacer(width=10)
                            dpg.add_text("|")'''

            #EditorRow(name = = "Column Name",
            #EditorRow(name = "Tag",
            #EditorRow(name = "Necessary?",
            #EditorRow(name = "Operations",



                dpg.add_separator()

    def resize(self,sender,app_data,user_data):

        if app_data:
            dpg.configure_item(self._id,height=36)
        else:
            dpg.configure_item(self._id,height=self.height)

class FiddlerWindow(DPGStage):
    
    
    def main(self,**kwargs):

        self.schemas = kwargs.get("schemas")
        self.to_edit = kwargs.get("to_edit")

    def generate_id(self,**kwargs):

        print(self.to_edit)


        with dpg.window(height=600,width=700,no_scrollbar=False):

            with dpg.child_window(height=30) as key:
                dpg.add_text("Check boxes")

            for schema in self.schemas:

                _to_edit_items = self.to_edit[schema.name]

                for inputfileObj in _to_edit_items:

                    FiddlerCell(inputfileObj=inputfileObj,schemas=self.schemas)

                    print (inputfileObj.name)
                    print (inputfileObj.extension)
                    inputfileObj.displayContents()

                