


import dearpygui.dearpygui as dpg
dpg.create_context()
from dataclasses import dataclass, field

from DPGStage import DPGStage


default_settings_path = "Redesign//Settings//"


@dataclass
class DefaultPaths:
    pass


def test(inputName,saveName):
    print("HERE WE GOOOO",f'{inputName=}',f'{saveName=}')


class DirectorySelector(DPGStage):

    type = "Directory"
    height=300
    width = 600
    inputType: str = "dir"
    nextStage: callable = test

    # TO use this function; look @ self.nextStage: this is where you're going to be receiving the file name.
    #   It will be <user_data>

    def generate_id(self,**kwargs):

        self.nextStage = kwargs.get("nextStage")
        self.label = f'Select {kwargs.get("label","Directory")}'


        with dpg.window(label="",height=self.height,width=self.width) as self._id:
            dpg.add_button(label=f"Select {self.type}",callback=self.openDialogue,width=500)
            self.selectedName = dpg.add_input_text(label=f"{self.type} Name",default_value=f"~No {self.type} Selected~",enabled=False,width=400)
            #-----------------
            dpg.add_separator()
            #-----------------
            self.next = dpg.add_button(width=500,  label=f"Confirm", callback=self.beforeNextStage,enabled=False)
   
    def beforeNextStage(self,sender,app_data,user_data):
        dpg.delete_item(self._id)
        self.nextStage(sender,app_data,user_data)

    def openDialogue(self,sender,app_data,user_data):

        self.dialogue = dpg.add_file_dialog(
            modal           =   True,
            default_path    =   default_settings_path, 
            directory_selector = True,
            height          =   400,
            width           =   600,
            callback        =   self.updateDialogue)
  
    def updateDialogue(self,sender,app_data,user_data):
        #import re
        # Given the name of the pdf and its parent folder:
        #   - sets the output path to be the default input for later use 
        #   - sets the processed path to be the default processed path
        # TO DO:
        #   - create some manner of popup which explains if the file was successfully processed and/or successfully moved.
        #====================================================
        # DISPLAY
        for i,(key,value) in enumerate(dpg.get_file_dialog_info(sender).items()):
            print(key,"\t",value)
        #====================================================
        _selectedName    =   app_data['file_path_name']
        parent      =   app_data['current_path']
        #====================================================
        dpg.configure_item(self.selectedName,default_value=_selectedName)
        dpg.configure_item(self.next,enabled=True)
        dpg.set_item_user_data(self.next,_selectedName)
        #====================================================
       
def main():
   
    DirectorySelector()

    dpg.create_viewport(title='Custom Title', width=1300, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__=="__main__":
    main()