
from DPGStage import DPGStage
from dearpygui import dearpygui as dpg

class BuiltinFunction(DPGStage):

    name: str
    tooltip: str

    inputs: dict[str:type]
    input_desc: dict[str:str]

    input_tag_locations = []

    def operationActual(**kwargs):
        ...

    def main(self,**kwargs):
        ...

    def generate_id(self,**kwargs):
        ...

class MarkupCalc(BuiltinFunction):

        name = "Markup"
        tooltip = "Calculates a price markup for a given input cost by the given margin.\n -\tRequires numerical input."

        input_desc = {
            "Inital Cost":{
                "desc:":"Which ever column tag is selected here will be used as the initial value to be marked up.",
                "type_if_static": float},
            "Markup":{
                "desc":"Which ever column tag is selected here",
                "type_if_static": float}
        }

        def operationActual(**kwargs):

            item_cost = kwargs.get("item_cost")
            margin = kwargs.get("margin")


            if margin >= 100:
                raise Exception("Margins can not exceed 100")

            #======================================================
            item_cost   =   float(input)
            #======================================================
            item_Price = (item_cost / (100 - margin)) * 100    

            q, r = divmod((100* item_cost), (100 - margin))
        
            skip = q + int(bool(r))

            if skip!=0 and margin!=0: skip -= 0.01
            #======================================================
            return skip

class PercentageCalc(BuiltinFunction):

        name = "Percentage"
        tooltip = "Increases or decreases input value by the given percentage.\n -\tRequires numerical input."

        input_desc = {
            "Inital Value":{
                "desc:":"Which ever column tag is selected here will be used as the initial value to be raised or lowered.",
                "type_if_static": float},
            "Percentage (%)":{
                "desc":"Which ever column tag is selected here",
                "type_if_static": float,
                "label":"%"}
        }

        def operationActual(**kwargs):

            item_cost = kwargs.get("item_cost")
            percent = kwargs.get("percent")

            #======================================================
            item_cost   =   float(item_cost)
            #======================================================
            item_Price = (item_cost + (item_cost/100)*percent)  
            #======================================================
            return item_Price



def percentgeCalculator(item_cost,percent):
        #======================================================
        item_cost   =   float(item_cost)
        #======================================================
        item_Price = (item_cost + (item_cost/100)*percent)  
        #======================================================
        return item_Price

def multiplier(value1, value2):
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
}


def main():

    print(markupCalculator(5,0))
    print(markupCalculator(5,99))
    print(percentgeCalculator(5,200))

if __name__=="__main__":
    main()
