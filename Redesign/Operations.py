


from DPGStage import DPGStage
from dearpygui import dearpygui as dpg
import copy
from dataclasses import dataclass,field
from Operations_Builtin import builtinFunctions
import Operations_Builtin

class OperationStep:
    sourceTag: str
    
@dataclass
class Operation:
    #steps: list[OperationStep]
    name: str = ''
    
@dataclass
class OperationMinimal:
    name: str = ''
    operationType: str = ''
    input_desc: dict = field(default_factory= lambda: {})

class OperationEditor(DPGStage):

    width = 580
    #TO DO:
    # somehow delete the last one if its still open!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    currentOp: Operations_Builtin.BuiltinFunction = None

    ops = {
        'Markup':Operations_Builtin.MarkupCalc,
        "Percentage":Operations_Builtin.PercentageCalc,
        "Multiplier":Operations_Builtin.Multiplier,
        "Static Value":Operations_Builtin.StaticValue}

    def main(self,**kwargs):
        
        self.schemaColumnEditor = kwargs.get("schemaColumnEditor")
        self.columnIndex = kwargs.get("columnIndex")

        self.tags = kwargs.get("tags")

        self.operation = kwargs.get("operation",OperationMinimal())

        self.editingExisting = kwargs.get("editingExisting",False)

    def displayEquation(self,sender,app_data,user_data):

        _chosenFunction = builtinFunctions[user_data.index(app_data)]

        dpg.configure_item(self.tooltip,default_value = _chosenFunction.tooltip)


        dpg.delete_item(self.functionInputGroup,children_only=True)
        dpg.push_container_stack(self.functionInputGroup)

        if self.operation.input_desc!={}:
            self.currentOp = _chosenFunction(input_desc = self.operation.input_desc,tags=self.tags)
        else:
            self.currentOp = _chosenFunction(tags=self.tags)

    def generate_id(self,**kwargs):

        enabled=kwargs.get("enabled",True)

        with dpg.window(height=350,width=self.width,label="Operation Details to determine Derived Values for Ouput Schema") as self._id:

            self._name = dpg.add_input_text(width=200,default_value=self.operation.name,label="Short reminder of what this operation does",enabled=enabled)
            
            if enabled:
                dpg.add_button(label="Save",callback=self.saveOp)

            dpg.add_separator()

            _combodf = '~' if self.operation.operationType == '' else self.operation.operationType

            _opCombo = dpg.add_combo(default_value=_combodf,items=[x.name for x in builtinFunctions],label="Builtin Functions",enabled=enabled,callback=self.displayEquation,user_data=[x.name for x in builtinFunctions])

            dpg.add_text("Function Details")
            _tooltipDF = self.ops.get(self.operation.operationType).tooltip if self.operation.operationType != '' else ''
            self.tooltip = dpg.add_input_text(enabled=False,multiline=True,default_value=_tooltipDF,height=50,width=self.width-90)

   
            with dpg.group() as self.functionInputGroup:
                pass

            if self.operation.operationType !='':
                self.displayEquation(_opCombo,self.operation.operationType,[x.name for x in builtinFunctions])


    def regenOps(self,sender,parent):
        pass

    def saveOp(self,sender):
        
        if not self.currentOp:
            with dpg.window(popup=True):
                dpg.add_text("No operation to save!",color=(255,0,0))
            return 

        # Set all attributes from the input fields
        setattr(self.operation,"name",dpg.get_value(self._name))
        setattr(self.operation,"operationType",self.currentOp.name)

        _desc_with_values = copy.deepcopy(self.currentOp.input_desc)
        for inputType,valueLocation in self.currentOp.input_tag_locations.items():
            print("---<>------")
            print(inputType)
            print(valueLocation)


            if inputType.endswith("_filter"):

                _type = inputType.split("_")[0]

                _desc_with_values[_type].update({"value_filter":dpg.get_value(valueLocation)})
            else:
                _desc_with_values[inputType].update({"value":dpg.get_value(valueLocation)})


        setattr(self.operation,"input_desc",_desc_with_values)

        # etc
        for op in self.schemaColumnEditor.operations[self.columnIndex]:
            if self.operation.name == op.name and self.operation != op:
                with dpg.window(popup=True):
                    with dpg.group(horizontal=True):
                        dpg.add_text("There already exists an operation with the name <",color=(255,0,0))
                        dpg.add_text(f'{op.name}')
                        dpg.add_text(">.",color=(255,0,0))
                return 

        #print(f'{op=}')

        #if self.operation != op: # if they're different
        #    self.schemaColumnEditor.operations[self.columnIndex].append(self.operation)

        if self.operation not in self.schemaColumnEditor.operations[self.columnIndex]:
            self.schemaColumnEditor.operations[self.columnIndex].append(self.operation)

        dpg.delete_item(self.schemaColumnEditor.opDisplay[self.columnIndex],children_only=True)
        dpg.push_container_stack(self.schemaColumnEditor.opDisplay[self.columnIndex])
        self.schemaColumnEditor.populateOps(columnIndex=self.columnIndex)

        print("Saved!")
        dpg.delete_item(self._id)