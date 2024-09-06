



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



builtinFunctions = {
    "Margin"        :   {'fn':markupCalculator,'tooltip':"Margin is equal to"},
    "Percentage"    :   {'fn':percentgeCalculator,'tooltip':"Percentage is equal to"},
}


print(markupCalculator(5,0))
print(markupCalculator(5,99))

print(percentgeCalculator(5,200))