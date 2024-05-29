


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


class FileSelector(DPGStage):
    
    type: str = "File"
    height=300
    width = 600
    inputTypes: list[str]
    fileColor: tuple = (255, 255, 0, 255)
    nextStage: callable

    def main(self,**kwargs):

        self.confirmationLabel = kwargs.get("confirmationLabel",f"Confirm Selection")
        self.nextStage = kwargs.get("nextStage",lambda x: print("No callback specified!"))
        self.inputTypes = kwargs.get("inputTypes",["xlsx","csv"])

    def generate_id(self,**kwargs):

        #self.inputType = kwargs.get("inputType","Unspecified File Type")
        label = kwargs.get("label","")

        with dpg.window(height=self.height,width=self.width,label=label) as self._id:
            dpg.add_button(label=f"Select {self.type}",callback=self.openDialogue,width=500)
            self.fileName = dpg.add_input_text(label=f"{self.type}name",default_value=f"~No {self.type} Selected~",enabled=False,width=500)
            #-----------------
            dpg.add_separator()
            #-----------------
            self.next = dpg.add_button(width=500,  label=self.confirmationLabel, callback=self.nextStage,enabled=False)
   
    def openDialogue(self,sender,app_data,user_data):
        with dpg.file_dialog(modal=True,default_path=default_settings_path,callback=self.updateDialogue,height=400,width=400) as self.dialog:
            # for fileType in inputTypes: # IF LIST

            for type in self.inputTypes:

                dpg.add_file_extension(f".{type}", color=self.fileColor, custom_text=type.upper())

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
        filename    =   app_data['file_name']
        parent      =   app_data['current_path']
        #====================================================
        dpg.configure_item(self.fileName,default_value=filename)
        dpg.configure_item(self.next,enabled=True)
        #dpg.add_input_text(tag=f'{self._id}_pdf_output_path',parent=senderParent,enabled=False,default_value=dpg.get_value('base_input_path'),label="Output Path")
        #dpg.add_input_text(tag=f'{self._id}_pdf_processed_path',parent=senderParent,enabled=False,default_value=dpg.get_value('base_processed_path'),label="Processed Path")
        dpg.add_text(default_value="Don't be alarmed; converted PDFs output to Default Input\nfor later use during Multiple File Selection.",parent=self._id)
        dpg.set_item_user_data(self.next,parent)
        #====================================================
        _name_without_extension = filename[:-4]#re.sub('.pdf', '', pdf_filename)
        self.selectedFile = f'{parent}\\{filename}'

class FileSelectorForConversion(FileSelector):

    type: str = "File"
    height=300
    width = 600
    inputTypes: list[str] = ["pdf"]
    outputType:str= "csv"
    fileColor: tuple = (255, 255, 0, 255)
    nextStage: callable = test

    def main(self,**kwargs):

        self.confirmationLabel = kwargs.get("confirmationLabel",f"Convert .{[inputType.upper() for inputType in self.inputTypes]} to .{self.outputType.upper()}")
        self.nextStage = kwargs.get("nextStage",lambda x: print("No callback specified!"))

    def generate_id(self,**kwargs):

        #self.inputType = kwargs.get("inputType","Unspecified File Type")
        label = kwargs.get("label","")

        with dpg.window(height=self.height,width=self.width,label=label) as self._id:
            dpg.add_button(label=f"Select {self.type}",callback=self.openDialogue,width=500)
            self.fileName = dpg.add_input_text(label=f"{self.type}name",default_value=f"~No {self.type} Selected~",enabled=False,width=500)
            #-----------------
            dpg.add_separator()
            with dpg.group(horizontal=True):
                self.saveAs = dpg.add_input_text(default_value=f"~Select {self.type.lower()} first for auto~",enabled=False,width=450)
                #-----------------        
                dpg.add_input_text(label="Save as",default_value=self.outputType,enabled=False,width=50)
            #-----------------
            dpg.add_separator()
            #-----------------
            self.next = dpg.add_button(width=500,  label=self.confirmationLabel, callback=self.nextStage,enabled=False)

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
        filename    =   app_data['file_name']
        parent      =   app_data['current_path']
        #====================================================
        dpg.configure_item(self.fileName,default_value=filename)
        dpg.configure_item(self.next,enabled=True)
        #dpg.add_input_text(tag=f'{self._id}_pdf_output_path',parent=senderParent,enabled=False,default_value=dpg.get_value('base_input_path'),label="Output Path")
        #dpg.add_input_text(tag=f'{self._id}_pdf_processed_path',parent=senderParent,enabled=False,default_value=dpg.get_value('base_processed_path'),label="Processed Path")
        dpg.add_text(default_value="Don't be alarmed; converted PDFs output to Default Input\nfor later use during Multiple File Selection.",parent=self._id)
        dpg.set_item_user_data(self.next,parent)
        #====================================================
        _name_without_extension = filename[:-4]#re.sub('.pdf', '', pdf_filename)
        self.selectedFile = f'{parent}\\{filename}'
        dpg.configure_item(self.saveAs,enabled=True,default_value=_name_without_extension)


def beginPDF(sender, app_data, user_data):
    # Sets the output of the scrape to be the default input folder.
    # Moves the pdf to the default processed folder.
    transformerWindow = dpg.get_item_parent(sender)
    #====================================================
    output_filepath     = dpg.get_value(f'{transformerWindow}_pdf_output_path')
    processed_path      = dpg.get_value(f'{transformerWindow}_pdf_processed_path')
    file                = dpg.get_value(f'{transformerWindow}_pdf_filename')
    parent              = user_data
    saveAs              = dpg.get_value(f'{transformerWindow}_pdf_saveAs')+'.csv'
    #====================================================
    annotations         = False
    #====================================================
    PDF_Scraper.scrape_pdf(input_path=parent,output_path=output_filepath,filename=file,saveName=saveAs,annotations=annotations)
    PDF_Scraper.scrape_pdf_alt(input_path=parent,output_path=output_filepath,filename=file,saveName=saveAs,annotations=annotations)
    processed_path = processed_path + "\\"
    File_Operations.cleanup(file,parent,processed_path) 


def main():
   
    FileSelectorForConversion(nextStage = test)

    dpg.create_viewport(title='Custom Title', width=1300, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__=="__main__":
    main()