

import dearpygui.dearpygui as dpg
dpg.create_context()
from dataclasses import dataclass, field

from DPGStage import DPGStage
from Directory_Selector import DirectorySelector

from CustomPickler import get,set

# 2 ways to go about it:
#   1. choose converter first and then scour items; show conversion props
#       or
#   2. choose files in input and then for each file show it's correspondences
#       i.e. if certain files were necessary for multiple kinds of outputs
#
#   3 (1+2): choose single converter as main:
#       but for each file, give the option to undergo other converters?

#   vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
#   4. check boxes for all the conversions u want to do:
#       if n input file's schema / markers matches more than 1 rubric: 
#       show both rubric fiddlers under its name during the INPUT->STAGE step
#   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

@dataclass
class ConversionRubric:
    name: str
    schema: list[str] = field(init=False)
    fileNameTagValueExtractor = []

class ConverterProcess(DPGStage):

    label: str
    height = 500
    width  = 1000

    def main(self,**kwargs):

        self.label = kwargs.get("label")

    def generate_id(self,**kwargs):

        self.main(**kwargs)

        with dpg.window(label=self.label,height=self.height,width=self.width) as self._id:
            
            #----------------------------------------------------
            with dpg.group(horizontal = True) as options:
                dpg.add_button(tag="staged_process_button",label="Begin Processing",width=120,height=60)
                #----------------------------------------------------
                with dpg.group():
                    dpg.add_checkbox(label="Item 1")
                    dpg.add_checkbox(label="Item 2")
                    dpg.add_checkbox(label="Item 3")

                with dpg.group():
                    dpg.add_checkbox(label="Item 4")
                    dpg.add_checkbox(label="Item 5")
                    dpg.add_checkbox(label="Item 6")
            #----------------------------------------------------
            dpg.add_separator()
            #----------------------------------------------------

    def scanInputs(self):
        # scans from default input folder and, given each process selected,

        pass

class ConverterManager(DPGStage):

    height = 500
    width  = 1000

    converters: list[ConversionRubric] = [ConversionRubric(name="CP8"),ConversionRubric("WIX")]

    def generate_id(self,**kwargs):

        with dpg.window(height=self.height,width=self.width) as self._id:
            dpg.add_button(label="New Converter")

            with dpg.tab_bar():
                with dpg.tab(label="Converters") as _allConverters:
                    converter_windows=[]
                    converer_boxes =[]
                    for c in self.converters:

                        with dpg.group(horizontal=True):

                            _chk = dpg.add_checkbox(default_value=True)

                            with dpg.child_window(height=40,) as _cw:
                                dpg.add_text(c.name)

                    converer_boxes.append(_chk)
                    converter_windows.append(_cw)

                with dpg.tab(label="+"):
                    dpg.add_text("Here")

       
def main():
   
    ConverterManager()
    ConverterProcess(label="From Input")

    dpg.create_viewport(title='Custom Title', width=1300, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__=="__main__":
    main()