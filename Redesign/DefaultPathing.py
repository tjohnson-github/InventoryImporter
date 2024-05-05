


import dearpygui.dearpygui as dpg
dpg.create_context()
from dataclasses import dataclass, field

from DPGStage import DPGStage
from Directory_Selector import DirectorySelector

default_settings_path = "Redesign\\Settings"


@dataclass
class DefaultPaths:
    pass


def test(inputName,saveName):
    print("HERE WE GOOOO",f'{inputName=}',f'{saveName=}')


class DefaultPathing(DPGStage):

    parent_folder = default_settings_path
   
    def generate_id(self,**kwargs):

        #self.dirSelector = 

        with dpg.group() as self._id:
                #[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
                with dpg.child_window(width=600,height=55):
                    dpg.add_text("When selecting a folder, make sure \\Rubric is present and that it contains a valid formatting rubric.")
                    dpg.add_text("All other directories will be auto-created.")
                #[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
                with dpg.child_window(width=600,height=170):
                    #add_input_text(tag='rubric_filename',label="Rubric",default_value="~No File Selected~",enabled=False,width=500)
                    dpg.add_input_text(tag='base_parent_directory',   enabled=False,default_value =   self.parent_folder               ,label="Parent Directory")
                    dpg.add_input_text(tag='base_input_path',         enabled=False,default_value =   self.parent_folder+"\\INPUT"     ,label="Input Path")
                    dpg.add_input_text(tag='base_staged_path',        enabled=False,default_value =   self.parent_folder+"\\STAGED"    ,label="Staged Path")
                    dpg.add_input_text(tag='base_output_path',        enabled=False,default_value =   self.parent_folder+"\\OUTPUT"    ,label="Output Path")
                    dpg.add_input_text(tag='base_processed_path',     enabled=False,default_value =   self.parent_folder+"\\PROCESSED" ,label="Processed Path")
                    dpg.add_input_text(tag='base_rubric_path',        enabled=False,default_value =   self.parent_folder+"\\Rubric"    ,label="Rubric Path")
                #[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
                dpg.add_button(tag='base_select',label="Select Default Directory",callback=self.showDialogue)
                dpg.add_button(tag='save_base_selection',label="Save Information?",show=False,callback=self.saveDefault)
                #dpg.add_text(tag='saved_notify',show=False,default_value="Saved!")
                #-----------------------------------------------
       
    def saveDefault(self,sender,app_data,user_data):
        print(f'{sender=}')
        print(f'{app_data=}')
        print(f'{user_data=}')

    def showDialogue(self,sender,app_data,user_data):
        DirectorySelector(nextStage = self.updateDefaultSelect)

    def updateDefaultSelect(self,sender, app_data, user_data):

        print(f'{sender=}')
        print(f'{app_data=}')
        print(f'{user_data=}')

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
        dpg.configure_item('base_rubric_path',     default_value =   foldername+"\\Rubric"       )
        #====================================================
        dpg.configure_item('save_base_selection',   show=True)


def main():
   
    with dpg.window():
        DefaultPathing()

    dpg.create_viewport(title='Custom Title', width=1300, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__=="__main__":
    main()