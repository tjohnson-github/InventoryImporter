



def markupCalculator(item_cost,margin):

        if margin >= 100:
            raise Exception("Margins can not exceed 100")

        #======================================================
        item_cost   =   float(item_cost)
        #======================================================
        item_Price = (item_cost / (100 - margin)) * 100    

        q, r = divmod((100* item_cost), (100 - margin))
        
        skip = q + int(bool(r))

        if skip!=0 and margin!=0: skip -= 0.01
        #======================================================
        return skip

def percentgeCalculator(item_cost,percent):
        #======================================================
        item_cost   =   float(item_cost)
        #======================================================
        item_Price = (item_cost + (item_cost/100)*percent)  
        #======================================================
        return item_Price

def multiplier(value1, value2):
    return value1*value2


builtinFunctions = {
    "Margin"        :   {'fn':markupCalculator,'tooltip':"Calculates a markup for a given input value by the given margin."},
    "Percentage"    :   {'fn':percentgeCalculator,'tooltip':"Increases or decreases input value by the given percentage."},
    "Multiplier"    :   {'fn':multiplier,'tooltip':"Multiplies two values together."},
}


print(markupCalculator(5,0))
print(markupCalculator(5,99))

print(percentgeCalculator(5,200))