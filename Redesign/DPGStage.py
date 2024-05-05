

import dearpygui.dearpygui as dpg

class DPGStage:

    label: str

    errorColor = (255, 68, 51)

    def __init__(self,stageOnly=False,**kwargs):

        #kwargs.get("tabView",self.)

        with dpg.stage() as self.stage:
           
           self.generate_id(**kwargs)

        self.set_themes()

        if not stageOnly:
            self.submit()

    def submit(self):
        dpg.unstage(self.stage)

    def set_values(self,**kwargs):
            pass

    def generate_id(self,**kwargs):
       #f"This function should be defined in your custom class:\t{kwargs = }"
        ...

    def set_themes(self):
        ...


