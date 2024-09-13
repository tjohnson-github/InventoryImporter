
from DPGStage import DPGStage
from dearpygui import dearpygui as dpg

class BuiltinFunction(DPGStage):

    name: str
    tooltip: str

    inputs: dict[str:type]
    input_desc: dict[str:str]

    input_tag_locations = []

    # If the selected field is TAG then you know to use one or both values from that row's location of that tag vs. the other value (static or TAG derived the same way)

    def operationActual(**kwargs):
        ...

    def displayInputCombo(self,sender,app_data,user_data):
        
        i               = user_data.get("index")
        inputType       = user_data.get("inputType")
        inputDetails    = user_data.get("inputDetails")

        dpg.delete_item(self.inputComboGroup[i],children_only=True)

        self.populateSourceCombo(i,inputType,inputDetails,app_data)

    def populateSourceCombo(self,i,inputType,inputDetails,currentSelection):
        
        #dpg.push_container_stack(self.inputComboGroup[i])

        with dpg.group():
            
            if currentSelection=="Static Value":

                _label = inputDetails.get("label",None)

                if inputDetails["type_if_static"]==float:
                    dpg.add_input_float(width=200,label=_label,parent=self.inputComboGroup[i])
                elif inputDetails["type_if_static"]==str:
                    dpg.add_input_text(width=200,label=_label,parent=self.inputComboGroup[i])
                elif inputDetails["type_if_static"]==int:
                    dpg.add_input_int(width=200,label=_label,parent=self.inputComboGroup[i])

            elif currentSelection=="Tag":
                dpg.add_combo(items=[],default_value='~',width=200)
                dpg.add_text("*Only TAGs that are currently entered in the Schema editor will appear here.")

    def generate_id(self,**kwargs):

        with dpg.group() as self._id:

            dpg.add_spacer(height=20)

            self.inputSourceCombos = []
                
            self.inputComboGroup = []

            self.inputCombos = []

            for i,(inputType,inputDetails) in enumerate(self.input_desc.items()):
                print("---------------")
                print(i)
                print(inputType)
                print(inputDetails)
                dpg.add_separator()

                with dpg.group(horizontal=True):
                    with dpg.child_window(width=200,height=30,border=False,no_scrollbar=True,no_scroll_with_mouse=True):
                        dpg.add_text(f"{inputType} Source: ")
                    _sourceCombo = dpg.add_combo(width=120,items=["Static Value","Tag"],default_value="Static Value",callback=self.displayInputCombo,user_data={"index":i,"inputType":inputType,"inputDetails":inputDetails})
                    self.inputSourceCombos.append(_sourceCombo)

                    _inputComboGroup = dpg.add_group(horizontal=True) 
                    self.inputComboGroup.append(_inputComboGroup)


                dpg.add_input_text(enabled=False,multiline=True,default_value=inputDetails["desc"],height=40)

            for i,(inputType,inputDetails) in enumerate(self.input_desc.items()):

                self.displayInputCombo(
                    sender      =   self.inputSourceCombos[i],
                    app_data    =   dpg.get_value(self.inputSourceCombos[i]),
                    user_data   =   dpg.get_item_user_data(self.inputSourceCombos[i]))
                #self.populateSourceCombo(i,inputType,inputDetails,dpg.get_value(self.inputSourceCombos[i]))


class MarkupCalc(BuiltinFunction):

        name = "Markup"
        tooltip = "Calculates a price markup for a given input cost by the given margin.\n -\tRequires numerical input."

        input_desc = {
            "Inital Cost":{
                "desc":"Which ever column tag is selected here will be used as the initial value to be marked up.",
                "type_if_static": float},
            "Markup":{
                "desc":"Which ever column tag is selected here",
                "type_if_static": float}
        }




        def operationActual(**kwargs):

            item_cost   = kwargs.get("item_cost")
            margin      = kwargs.get("margin")


            if margin >= 100:
                raise Exception("Margins can not exceed 100")

            #======================================================
            item_cost   =   float(input)
            #======================================================
            item_Price = (item_cost / (100 - margin)) * 100    

            q, r        = divmod((100* item_cost), (100 - margin))
        
            skip        = q + int(bool(r))

            if skip!=0 and margin!=0: skip -= 0.01
            #======================================================
            return skip

class PercentageCalc(BuiltinFunction):

        name = "Percentage"
        tooltip = "Increases or decreases input value by the given percentage.\n -\tRequires numerical input."

        input_desc = {
            "Base":{
                "desc":"Which ever column tag is selected here will be used as the initial value to be raised or lowered.",
                "type_if_static": float},
            "Percentage (%)":{
                "desc":"Which ever column tag is selected here, given in %, will be used to calculate the final amount.",
                "type_if_static": float,
                "label":"%"}
        }

        def operationActual(**kwargs):

            Base        = kwargs.get("Base")
            percent     = kwargs.get("percent")

            #======================================================
            Base        = float(Base)
            #======================================================
            amount      = (Base + (Base/100)*percent)  
            #======================================================
            return amount

class Multiplier(BuiltinFunction):

        name = "Multiplier"
        tooltip = "Unlike percentage which adds the multiplied product to the original value, this merely calculates the product.\n -\tObviously, you could input the percentage as a fraction here to arrive at the same number, but this is in case you need it."

        input_desc = {
            "Multiplicand":{
                "desc":"Which ever column tag is selected here will be used as the initial value to be multiplied.",
                "type_if_static": float},
            "Multiplier":{
                "desc":"Which ever column tag is selected here will be multiplied against the multiplicand to create the product.",
                "type_if_static": float},
            "Round to a number of digits?":{
                "desc":"If you wish to round the product to a certain number of significant digits.",
                "type_if_static": int}
        }


        # allow to round to certain values

        def operationActual(**kwargs):

            Multiplicand   = kwargs.get("Multiplicand")
            Multiplier     = kwargs.get("Multiplier")

            #======================================================
            Multiplicand   =   float(Multiplicand)
            #======================================================
            product  = (item_cost + (item_cost/100)*percent)  
            #======================================================
            return item_Price

class StaticValue(BuiltinFunction):

        name = "Static Value"
        tooltip = "Use if every row in this column should be the same value, and that value is not expected to come from anywhere else."

        input_desc = {
            "Value":{
                "desc":"Columns TAGs cannot be selected here, as it would imply a variability of values. Instead, you must supply a single value.",
                "type_if_static": str},
        }

        def operationActual(**kwargs):

            Value   = kwargs.get("Value")
            
            return Value



builtinFunctions = [StaticValue,MarkupCalc,PercentageCalc,Multiplier]

'''def multiplier(value1, value2):
    return value1*value2

def staticValue(value1):
    return value1

builtinFunctions = {
    "Margin"        :   {
        'fn':markupCalculator,
        "inputs":{
            0:"Input Value",
            1:"Markup"},
        'tooltip':"Calculates a markup for a given input value by the given margin.\nRequires numerical input."
        },
    "Percentage"    :   {
        'fn':percentgeCalculator,
        'tooltip':"Increases or decreases input value by the given percentage.\nRequires numerical input."},
    "Multiplier"    :   {
        'fn':multiplier,
        'tooltip':"Multiplies two values together.\nRequires numerical input."}, # for example: quantity in pack
    "Static Value"  :   {
        'fn':staticValue,
        'tooltip':"Will populate every row with the given value"}, # for example: quantity in pack
}'''


def main():

    print(markupCalculator(5,0))
    print(markupCalculator(5,99))
    print(percentgeCalculator(5,200))

if __name__=="__main__":
    main()
