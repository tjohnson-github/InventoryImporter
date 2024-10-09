


import dearpygui.dearpygui as dpg
dpg.create_context()
from dataclasses import dataclass, field,fields
import os
from DPGStage import DPGStage
#from Directory_Selector import DirectorySelector
from Selector_Directory import DirectorySelector

from CustomPickler import get,set

default_settings_path = "Redesign\\Settings"


@dataclass
class DefaultPaths:
    base: str
    input: str
    staged: str
    output: str
    processed: str
    rubric: str

    def makeDirectories(self,sender,app_data,user_data):

        for field in fields(self):

            _path = getattr(self,field.name)

            if not os.path.exists(_path):
                os.mkdir(_path)

        user_data()

class DefaultPathing(DPGStage):

    buttonWidth = 300
    parent_folder = "ConverterFiles"
    settingsName = f'{default_settings_path}\\defaultPathing.txt'
   
    @classmethod
    def getPaths(cls):

        return get(cls.settingsName)

    def findDefault(self):
        try:
           _ = get(self.settingsName)
        except Exception as e:
           print ("Probably doesnt exist yet:\t",e)

           _ = DefaultPaths(
            f'{self.parent_folder}',
            f'{self.parent_folder}\\INPUT',
            f'{self.parent_folder}\\STAGED',
            f'{self.parent_folder}\\OUTPUT',
            f'{self.parent_folder}\\PROCESSED',
            f'{self.parent_folder}\\RUBRICS',
            )

        return _

    def main(self,**kwargs):

        self.mainPage = kwargs.get("mainPage")

    def generate_id(self,**kwargs):

        default = self.findDefault()


        _baseDefault = default.base
        _inputDefault = default.input
        _stagedDefault = default.staged
        _outputDefault = default.output
        _processedDefault = default.processed 
        _rubricsDefault = default.rubric

        with dpg.window(label="Set Default Directories") as self._id:
            with dpg.group():
                #[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
                with dpg.child_window(width=600,height=58):
                    dpg.add_text("When selecting a folder, make sure \\Rubric is present and that it contains a valid formatting rubric.")
                    dpg.add_text("All other directories will be auto-created.")
                #[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
                with dpg.child_window(width=600,height=175):
                    #add_input_text(tag='rubric_filename',label="Rubric",default_value="~No File Selected~",enabled=False,width=500)
                    with dpg.group(horizontal=True):
                        dpg.add_input_text(tag='base_parent_directory',   enabled=False,default_value =   _baseDefault,width=self.buttonWidth)
                        _baseUpdate = dpg.add_button(label="Parent Directory",callback=self.updateBaseDialogue)
                    with dpg.collapsing_header(label="Specify different subdirectories",leaf =True):
                        with dpg.group(horizontal=True):
                            dpg.add_input_text(tag='base_input_path',         enabled=False,default_value =   _inputDefault,width=self.buttonWidth)
                            _inputUpdate = dpg.add_button(label="Input Path",callback=self.updateSubDirDialogue,user_data='base_input_path')
                        with dpg.group(horizontal=True):
                            dpg.add_input_text(tag='base_staged_path',        enabled=False,default_value =   _stagedDefault,width=self.buttonWidth)
                            _stagedUpdate = dpg.add_button(label="Staged Path",callback=self.updateSubDirDialogue,user_data='base_staged_path')
                        with dpg.group(horizontal=True):
                            dpg.add_input_text(tag='base_output_path',        enabled=False,default_value =   _outputDefault,width=self.buttonWidth)
                            _outputUpdate = dpg.add_button(label="Output Path",callback=self.updateSubDirDialogue,user_data='base_output_path')
                        with dpg.group(horizontal=True):
                            dpg.add_input_text(tag='base_processed_path',     enabled=False,default_value =   _processedDefault,width=self.buttonWidth)
                            _processedUpdate = dpg.add_button(label="Processed Path",callback=self.updateSubDirDialogue,user_data='base_processed_path')
                        with dpg.group(horizontal=True):
                            dpg.add_input_text(tag='base_rubric_path',        enabled=False,default_value =   _rubricsDefault,width=self.buttonWidth)
                            _rubricUpdate = dpg.add_button(label="Rubric Path",callback=self.updateSubDirDialogue,user_data='base_rubric_path')
                #[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
                with dpg.tooltip(_baseUpdate):
                    dpg.add_text("This is the folder that will contain the following sub folders.")
                    dpg.add_text("Any that do not exist at time of selection will be auto-created.")
                    dpg.add_separator()
                    dpg.add_text("Click to specify a different directory than the parent subfolder.")
                with dpg.tooltip(_inputUpdate):
                    dpg.add_text("This is where the program will scan files that match an input schema.")
                    dpg.add_text("Files that match a schema will have their suggested conversions displayed\nor the conversions can be automatic, assuming program has enough information to draw on.")
                    dpg.add_separator()
                    dpg.add_text("Click to specify a different directory than the parent subfolder.")
                with dpg.tooltip(_stagedUpdate):
                    dpg.add_text("This is where, if enabled, output files will be staged for human review before the process continues.")
                    dpg.add_text("Even if disabled, files will drop here momentarily for the program to scan.")
                    dpg.add_separator()
                    dpg.add_text("Click to specify a different directory than the parent subfolder.")
                with dpg.tooltip(_outputUpdate):
                    dpg.add_text("This is where where the final products of this process will end up.")
                    dpg.add_text("You will have a chance to edit the naming conventions in the UI before they're created.")
                    dpg.add_separator()
                    dpg.add_text("Click to specify a different directory than the parent subfolder.")
                with dpg.tooltip(_processedUpdate):
                    dpg.add_text("This is where input files that have been successfully scraped and converted will go.")
                    dpg.add_separator()
                    dpg.add_text("Click to specify a different directory than the parent subfolder.")
                with dpg.tooltip(_rubricUpdate):
                    dpg.add_text("This is where the rubric spreadsheets will be saved. They can be edited manually or through the UI.")
                    dpg.add_text("If you wish to use Google Sheets, please go under settings and select `Link Google Account`.")
                    dpg.add_separator()
                    dpg.add_text("Click to specify a different directory than the parent subfolder.")
                #[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
                with dpg.tooltip('base_parent_directory'):
                    dpg.add_text(dpg.get_value('base_parent_directory'))

                with dpg.tooltip('base_input_path'):
                    dpg.add_text(dpg.get_value('base_input_path'))

                with dpg.tooltip('base_staged_path'):
                    dpg.add_text(dpg.get_value('base_staged_path'))

                with dpg.tooltip('base_output_path'):
                    dpg.add_text(dpg.get_value('base_output_path'))

                with dpg.tooltip('base_processed_path'):
                    dpg.add_text(dpg.get_value('base_processed_path'))

                with dpg.tooltip('base_rubric_path'):
                    dpg.add_text(dpg.get_value('base_rubric_path'))
                #[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
                dpg.add_button(tag='save_base_selection',label="Save Information?",show=True,callback=self.saveDirpaths)
                dpg.add_button(label="Reset Subdirectories",callback=self.updateAllFields,user_data=dpg.get_value('base_parent_directory'))
                dpg.add_button(label="Back",callback=self.delete)
                #-----------------------------------------------


    def saveDirpaths(self,sender,app_data,user_data):
        print(f'{sender=}')
        print(f'{app_data=}')
        print(f'{user_data=}')

        _pathingObj = DefaultPaths(
            dpg.get_value('base_parent_directory'),
            dpg.get_value('base_input_path'),
            dpg.get_value('base_staged_path'),
            dpg.get_value('base_output_path'),
            dpg.get_value('base_processed_path'),
            dpg.get_value('base_rubric_path'),)

        set(self.settingsName,_pathingObj)


        with dpg.window(popup=True):
            dpg.add_text("Directory paths saved successfully!")
            
            # ENSURES the DIRNAME <defaults> ARE ALSO UPDATED
            for schema in self.mainPage.schemas:

                if schema.dirnameConvention:

                    if schema.dirnameConvention.pathIsDefault:
                        dpg.add_separator()
                        dpg.add_text(f"{schema.name}'s default directory has been updated.")




    def updateBaseDialogue(self,sender,app_data,user_data):
        DirectorySelector(nextStage = self.updateAllFields)

    def updateSubDirDialogue(self,sender,app_data,user_data):
        self.last_selected = sender
        DirectorySelector(nextStage = self.updateSpecificField, label=dpg.get_item_label(sender))

    def updateSpecificField(self,sender, app_data, user_data):
        _field_to_change = dpg.get_item_user_data(self.last_selected)
        dpg.configure_item(_field_to_change,default_value=user_data)

    def updateAllFields(self,sender, app_data, user_data):

        # Given the general filepath, sets the default items to be whats expected.
        # TO DO:
        #       If these files dont actually exist, create them.
        #====================================================
        foldername=user_data
        #====================================================
        dpg.configure_item('base_parent_directory',default_value =   foldername                  )
        dpg.configure_item('base_input_path',      default_value =   foldername+"\\INPUT"        )
        dpg.configure_item('base_staged_path',     default_value =   foldername+"\\STAGED"        )
        dpg.configure_item('base_output_path',     default_value =   foldername+"\\OUTPUT"       )
        dpg.configure_item('base_processed_path',  default_value =   foldername+"\\PROCESSED"    )
        dpg.configure_item('base_rubric_path',     default_value =   foldername+"\\RUBRICS"       )
        #====================================================
        dpg.configure_item('save_base_selection',   show=True)


def main():
   
    #with dpg.window():
    DefaultPathing()

    dpg.create_viewport(title='Custom Title', width=1300, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__=="__main__":
    main()