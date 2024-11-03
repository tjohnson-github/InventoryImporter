


import dearpygui.dearpygui as dpg
import datetime
import File_Operations
import JFGC_Data
JFGC = JFGC_Data.jfgcdata#JFGC_Data.JFGC_Data()
sqlClient = JFGC_Data.sqlClient

class ConditionFilter:
    group: int
    check: int
    combo: int
    sqlFormattedItems: list
    sqlString: str

    def __init__(self,dpgFormatteditems,label,sqlString,sqlFormattedItems,after=None):
        if after:  self.group = dpg.add_group(horizontal=True,parent=dpg.get_item_parent(after)) # change to after?
        else:       self.group = dpg.add_group(horizontal=True)
        self.check  = dpg.add_checkbox(default_value=True,parent=self.group)
        self.combo  = dpg.add_combo(items=dpgFormatteditems,label=label,width=300,parent=self.group)
        self.sqlString = sqlString
        self.dpgFormatteditems = dpgFormatteditems
        self.sqlFormattedItems = sqlFormattedItems

class SQLScraper:
    queryName: str
    client: sqlClient
    filters: list[ConditionFilter]
    pathingDict: dict

    def getCombinedQty(self,ITEM_NO):
        from_table              =   "IM_INV"
        sort_by                 =   "NAM_UPR"
        cursorStr = f"""SELECT * FROM JFGC.dbo.{from_table} WHERE ITEM_NO LIKE '{ITEM_NO}'"""

        #print(f"Attemtping to run:\n\t{cursorStr}")
        self.client.cursor.execute(cursorStr)

        headers                 =   [i[0] for i in self.client.cursor.description]

        #print (headers)

        #rows = []

        _qty =  0
        storecount = 0

        #print(f"\t\t{ITEM_NO}\n")

        for i,x in enumerate(self.client.cursor):
            #rows.append(x)
            #if i>=6: break
            if storecount >2: break

            if x[headers.index("QTY_AVAIL")]!=0:

                #for col in headers: print(f'{x}\t:\t{x[headers.index(col)]}')

                #print (f'{x[headers.index("QTY_AVAIL")]} at location {x[headers.index("LOC_ID")]}')
                if x[headers.index("LOC_ID")]=='4' or x[headers.index("LOC_ID")]=='6':
                    storecount+=1
                    _qty+=x[headers.index("QTY_AVAIL")]
                    #print (f'\nadding {x[headers.index("QTY_AVAIL")]}')


            #print("============")

        #print("============\n============\n============")

        return _qty 

    def addFilter(self,sender,app_data,user_data):
        
        print(self)
        print(sender)
        print(app_data)
        print(user_data)

        if user_data == "Department":
            new_filter = ConditionFilter(self.dept_names,"Department","CATEG_COD",["0"+str(x.code) if len(str(x.code))==2 else "00"+str(x.code) for x in self.jfgcdata.allDepartments],after=dpg.get_item_parent(sender))
        elif user_data == "Vendor":
            new_filter = ConditionFilter(self.vendorNames,"Vendor","ITEM_VEND_NO",[str(y) for x,y in self.jfgcdata.vendorDict.items()],after=dpg.get_item_parent(sender))

        self.filters.append(new_filter)

    def formatPartial(self,headers,rows):

        print(f"Attempting to format {len(rows)} items.")

        SQL_csv =['ITEM_NO'	, 'PROF_ALPHA_2' , 'DESCR' , 'LST_COST' , 'PRC_1' , 'TAX_CATEG_COD' , 'CATEG_COD' , 'ACCT_COD' , 'ITEM_VEND_NO' , 'PROF_COD_4' , 'PROF_ALPHA_3' , 'PROF_DAT_1' , 'QTY']
        _compiled_list = [SQL_csv]

        _zeroes = []

        for i,row in enumerate(rows):

            if ((i+1)%100==0):
                print(f"Formatting item {i+1} / {len(rows)}")

            _formattedRow = []
            for ii,column in enumerate(SQL_csv):

                if column=="QTY":
                    _qty = self.getCombinedQty(row[headers.index('ITEM_NO')])
                    _formattedRow.append(_qty)
                else:
                    _formattedRow.append(row[headers.index(column)])

            if _qty==0:
                 _zeroes.append(_formattedRow)
            else:
                _compiled_list.append(_formattedRow)

        for x in _zeroes: _compiled_list.append(x)

        print("Done formatting: attempting to save")
        File_Operations.list_to_csv(_compiled_list,f'{self.pathingDict["ouput_filepath"]}\\QUERIES\\{dpg.get_value(self.queryName)}.csv')
        print("\n\nQUERY DONE")

    def runQuery(self):
        
        from_table              =   "IM_ITEM"
        sort_by                 =   "NAM_UPR"
        cursorStr = f"""SELECT * FROM JFGC.dbo.{from_table}"""

        if True in [dpg.get_value(x.check) for x in self.filters] and [ dpg.get_value(x.combo) for x in self.filters].count("")!=len(self.filters):
            cursorStr+=" WHERE"

        filteredBySameType =[]

        for i,filter in enumerate(self.filters):
            

            if dpg.get_value(filter.check) and dpg.get_value(filter.combo):

                if i>1: 
                    if filter.sqlString not in filteredBySameType:
                        cursorStr+=f" AND {filter.sqlString} LIKE"
                    else: cursorStr+=f" OR {filter.sqlString} LIKE"
                    cursorStr+=f" '{filter.sqlFormattedItems[filter.dpgFormatteditems.index(dpg.get_value(filter.combo))]}'"    
                else:
                    cursorStr+=f" {filter.sqlString} LIKE '{filter.sqlFormattedItems[filter.dpgFormatteditems.index(dpg.get_value(filter.combo))]}'"

            filteredBySameType.append(filter.sqlString)

        print(f"Attemtping to run:\n\t{cursorStr}")
        self.client.cursor.execute(cursorStr)

        headers                 =   [i[0] for i in self.client.cursor.description]

        #print (headers)
        #print(f"\n Iterating over {len(self.client.cursor)} rows.")
        rows = []

        #length = [x for i,x in enumerate(self.client.cursor)]
        #length = 0

        for i,x in enumerate(self.client.cursor):
            if ((i+1)%100==0):
                print(f"Counting item {i+1}")
            #length+=1
            rows.append(x)
            
            #if i>=6: break

            '''for ii,column in enumerate(headers):
                if x[ii]!="None" and x[ii]!= None:
                    print(f'{column}\t:\t{x[ii]}')'''

            #print("============\n============\n============")

        self.formatPartial(headers,rows)

    def __init__(self,width,height,pathingDict):

        self.client = sqlClient
        self.pathingDict = pathingDict
       

        with dpg.child_window(width=width,height=height):

            self.jfgcdata = JFGC

            self.queryName = dpg.add_input_text(label="Name of Query",width=170,default_value=str(datetime.datetime.now().strftime('%Y-%m-%d')))
            #dpg.add_text(id='savedirReminder',default_value="Query will be saved in directory:")
            dpg.add_button(label="Run Query",callback=self.runQuery)

            dpg.add_separator()

            dpg.add_text("FILTERS")

            #=============================================
            self.dept_names = [f'{x.code}\t:\t{x.name}' for x in self.jfgcdata.allDepartments]
            deptfilter = ConditionFilter(self.dept_names,"Department","CATEG_COD",["0"+str(x.code) if len(str(x.code))==2 else "00"+str(x.code) for x in self.jfgcdata.allDepartments])
            newdept = dpg.add_button(label="+",parent=deptfilter.group,callback=self.addFilter,user_data="Department")
            #=============================================
            self.vendorNames = [f'{y}\t:\t{x}' for x,y in self.jfgcdata.vendorDict.items()]
            self.vendorNames.reverse()
            vendorfilter = ConditionFilter(self.vendorNames,"Vendor","ITEM_VEND_NO",[str(y) for x,y in self.jfgcdata.vendorDict.items()])
            newvend = dpg.add_button(label="+",parent=vendorfilter.group,callback=self.addFilter,user_data="Vendor")
            #=============================================
            self.filters = [deptfilter,vendorfilter]