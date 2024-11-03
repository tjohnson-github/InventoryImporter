
    
import sys,os
import dearpygui.dearpygui as dpg

import JFGC_Data
JFGC = JFGC_Data.jfgcdata#JFGC_Data.JFGC_Data()


class Markup:

    def __init__(self,width=0,height=0,visualize=False):
        if visualize: 
            with dpg.child_window(width=width,height=height):     
                #======================================================
                dpg.add_text("Price Markup Test")
                #======================================================
                dpg.add_input_float(
                    tag             =   'cost_test',
                    width           =   100,
                    label           =   "Cost")
                dpg.add_combo(
                    tag             =   "test_dept", 
                    items           =   list(x.dptStr for x in JFGC.allDepartments), #list(JFGC.departmentsSTRByCode.values()),
                    default_value   =   list(x.dptStr for x in JFGC.allDepartments)[0])
                #======================================================
                price_group = dpg.add_group(horizontal = True)
                dpg.add_button(
                    parent          =   price_group,
                    label           =   "Check Markup",
                    callback        =   self.markupUpdater)
                dpg.add_input_text(
                    parent          =   price_group,
                    tag             =   'markup-output',
                    default_value   =   0.00,
                    enabled         =   False,
                    label           =   "Price",
                    width           =   120)
                dpg.add_text(
                    parent = price_group,
                    tag             = 'markup-text',
                    default_value   = ''
                    )

    def markupUpdater(self,sender,app_data,user_data):
        #======================================================
        # Calculates item markup based on its cost and department
        #======================================================
        dpt_string  = dpg.get_value("test_dept")
        dpt         = JFGC.getDptByDptStr(dpt_string)
        cost        = dpg.get_value('cost_test')
        price       = self.markupCalculator(cost,dpt)
        #======================================================
        dpg.configure_item('markup-output',default_value=str(price))

    def markupCalculator(self,item_cost,dept,round=False):
        #======================================================
        item_cost   =   float(item_cost)
        #======================================================
        item_Price = (item_cost / (100 - dept.margin)) * 100    
        q, r = divmod((100* item_cost), (100 - dept.margin))
        skip = q + int(bool(r))
        if skip!=0: skip -= 0.01
        #======================================================
        return skip

class PrcBreakdown:

    def __init__(self,width,height):
        with dpg.child_window(width=width,height=height):
            #======================================================
            dpg.add_text("Price Breakdown")
            #======================================================
            breakdown_group = dpg.add_group(horizontal = True)

            with dpg.child_window(width=200,height=height-40,parent=breakdown_group):

                dpg.add_input_float(tag='breakdown_cost',width=100,label="Cost")
                dpg.add_input_int(tag='breakdown_num',width=100,label="Sizes Avail.",default_value=2)
                dpg.add_button(
                    label           =   "Calculate Breakdown",
                    callback        =   self.breakdownCalculator)
            #======================================================        
            dpg.add_input_text(
                tag             =   'breakdown-output',
                default_value   =   0.00,
                label           =   "Prices\nLarge\nto\nSmall",
                parent          =   breakdown_group,
                enabled         =   False,
                width           = 90,
                height          = height-70,
                multiline =True)
            #======================================================

    def breakdownCalculator(self,item_cost,item_dept,round=False):
        #======================================================
        # Calculates item price breakdown based on number of sizes/items in kit
        #======================================================
        cost        = dpg.get_value("breakdown_cost")
        num         = dpg.get_value("breakdown_num")
        #======================================================
        if num < 2 or num > 7:
            dpg.configure_item('breakdown-output',default_value="Wrong Qty!")
            return

        price_divide    =   {
            '2':[.57,.43],
            '3':[.42,.33,.25],
            '4':[.33,.28,.22,.17],
            '5':[.30,.25,.20,.15,.10],
            '6':[.25,.22,.18,.15,.11,.09],
            '7':[.21,.19,.17,.14,.12,.10,.07],
        }

        formatted_results       =   ""
        count                   =   1

        for x in (price_divide[str(num)]):
            print (x*cost)
            count +=1
            formatted_results+=f'{x*cost}\n'

        print (count*15)
        #======================================================
        dpg.configure_item('breakdown-output',default_value=formatted_results,height=int(count*13))

