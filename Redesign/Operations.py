


from DPGStage import DPGStage
from dearpygui import dearpygui as dpg

from dataclasses import dataclass,field
from Builtin_Equations import builtinFunctions

class OperationStep:
    sourceTag: str
    
@dataclass
class Operation:
    #steps: list[OperationStep]
    name: str = ''

class OperationEditor(DPGStage):



    def main(self,**kwargs):
        
        self.schemaColumnEditor = kwargs.get("schemaColumnEditor")
        self.columnIndex = kwargs.get("columnIndex")

        self.operation = kwargs.get("operation",Operation())

    def generate_id(self,**kwargs):

        with dpg.window(height=350,width=500) as self._id:

            self._name = dpg.add_input_text(default_value=self.operation.name,label="Short reminder of what this operation does")
            dpg.add_button(label="Save",callback=self.saveOp)

            dpg.add_separator()

            _opCombo = dpg.add_combo(default_value="~",items=[x for x in list(builtinFunctions.keys())],label="Builtin Functions")

            with dpg.group(horizontal=True):
                dpg.add_text("This column's values will be the",bullet=True)
                dpg.add_combo(items=["Input","Output"],width=75)
                dpg.add_text("of the equation.")

            dpg.add_text("Using this column's values as the initial values of the equation,")


            dpg.add_text("Using the fields as derived from the following tag")
            dpg.add_combo(label='Tag')
            #dpg.add_combo(label=Tag)

            dpg.add_text("Source Column's Tag")
            dpg.add_combo()

            dpg.add_text(f"{dpg.get_value(_opCombo)} value derived from")
                        
            with dpg.group(horizontal=True):
                dpg.add_combo(label="Tag")

    def regenOps(self,sender,parent):
        pass

    def saveOp(self,sender):
        
        # Set all attributes from the input fields
        setattr(self.operation,"name",dpg.get_value(self._name))

        # etc


        self.schemaColumnEditor.operations[self.columnIndex].append(self.operation)

        dpg.delete_item(self.schemaColumnEditor.opDisplay[self.columnIndex],children_only=True)
        dpg.push_container_stack(self.schemaColumnEditor.opDisplay[self.columnIndex])
        self.schemaColumnEditor.populateOps(columnIndex=self.columnIndex)

        print("Saved!")
        dpg.delete_item(self._id)