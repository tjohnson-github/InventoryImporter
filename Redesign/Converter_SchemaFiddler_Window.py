
from DPGStage import DPGStage

from dearpygui import dearpygui as dpg


class FiddlerCell(DPGStage):

    height=100

    def main(self,**kwargs):
        
        self.inputFile = kwargs.get("inputfileObj")

    def generate_id(self,**kwargs):
        
        with dpg.child_window(height=self.height) as self._id:

            with dpg.group(horizontal=True):

                _ = dpg.add_checkbox(callback=self.resize)
                with dpg.tooltip(_): dpg.add_text("Information correct?")

                dpg.add_spacer(width=30)

                _ = dpg.add_text(self.inputFile.name)
                with dpg.tooltip(_): dpg.add_text(self.inputFile.fullPath)

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

            for schema in self.schemas:

                _to_edit_items = self.to_edit[schema.name]

                for inputfileObj in _to_edit_items:

                    FiddlerCell(inputfileObj=inputfileObj)

                    print (inputfileObj.name)
                    print (inputfileObj.extension)
                    inputfileObj.displayContents()

                