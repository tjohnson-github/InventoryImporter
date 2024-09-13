


from DPGStage import DPGStage
from dearpygui import dearpygui as dpg

from dataclasses import dataclass,field
from Operations_Builtin import builtinFunctions

class OperationStep:
    sourceTag: str
    
@dataclass
class Operation:
    #steps: list[OperationStep]
    name: str = ''
    

class OperationEditor(DPGStage):

    #TO DO:
    # somehow delete the last one if its still open!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def main(self,**kwargs):
        
        self.schemaColumnEditor = kwargs.get("schemaColumnEditor")
        self.columnIndex = kwargs.get("columnIndex")

        self.operation = kwargs.get("operation",Operation())

        self.editingExisting = kwargs.get("editingExisting",False)

    def displayEquation(self,sender,app_data,user_data):

        _chosenFunction = builtinFunctions[user_data.index(app_data)]

        dpg.configure_item(self.tooltip,default_value = _chosenFunction.tooltip)


        dpg.delete_item(self.functionInputGroup,children_only=True)
        dpg.push_container_stack(self.functionInputGroup)

        _chosenFunction()

    def generate_id(self,**kwargs):

        enabled=kwargs.get("enabled",True)

        with dpg.window(height=350,width=500,label="Operation Details to determine Derived Values for Ouput Schema") as self._id:

            self._name = dpg.add_input_text(width=200,default_value=self.operation.name,label="Short reminder of what this operation does",enabled=enabled)
            
            if enabled:
                dpg.add_button(label="Save",callback=self.saveOp)

            dpg.add_separator()

            _opCombo = dpg.add_combo(default_value="~",items=[x.name for x in builtinFunctions],label="Builtin Functions",enabled=enabled,callback=self.displayEquation,user_data=[x.name for x in builtinFunctions])

            dpg.add_text("Function Details")
            self.tooltip = dpg.add_input_text(enabled=False,multiline=True,default_value='',height=50)

            with dpg.group() as self.functionInputGroup:
                pass

            '''with dpg.group(horizontal=True):
                dpg.add_text("This column's values will be the",bullet=True)
                dpg.add_combo(items=["Input","Output"],width=75,enabled=enabled)
                dpg.add_text("of the equation.")

            dpg.add_text("Using this column's values as the initial values of the equation,")


            dpg.add_text("Using the fields as derived from the following tag")
            dpg.add_combo(label='Tag',enabled=enabled)
            #dpg.add_combo(label=Tag)

            dpg.add_text("Source Column's Tag")
            dpg.add_combo(enabled=enabled)

            dpg.add_text(f"{dpg.get_value(_opCombo)} value derived from")
                        
            with dpg.group(horizontal=True):
                dpg.add_combo(label="Tag",enabled=enabled)'''

    def regenOps(self,sender,parent):
        pass

    def saveOp(self,sender):
        
        # Set all attributes from the input fields
        setattr(self.operation,"name",dpg.get_value(self._name))

        # etc
        for op in self.schemaColumnEditor.operations[self.columnIndex]:
            if self.operation.name == op.name and self.operation != op:
                with dpg.window(popup=True):
                    with dpg.group(horizontal=True):
                        dpg.add_text("There already exists an operation with the name <",color=(255,0,0))
                        dpg.add_text(f'{op.name}')
                        dpg.add_text(">.",color=(255,0,0))
                return 


        if self.operation != op: # if they're different
            self.schemaColumnEditor.operations[self.columnIndex].append(self.operation)

        dpg.delete_item(self.schemaColumnEditor.opDisplay[self.columnIndex],children_only=True)
        dpg.push_container_stack(self.schemaColumnEditor.opDisplay[self.columnIndex])
        self.schemaColumnEditor.populateOps(columnIndex=self.columnIndex)

        print("Saved!")
        dpg.delete_item(self._id)