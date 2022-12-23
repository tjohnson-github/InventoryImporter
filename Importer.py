from Vendorfile import vendorfile
import Gspread_Rubric
import dearpygui.dearpygui as dpg

import datetime
from datetime import date


class Importer:
    # Is there a way to make it so you never have to close the program to restart functionality?
    __count: int = 0

    suggestedSaveName_content: list = []

    def __init__(self,JFGC,pathing_dict,cloudRubric=True):
        self.__count+=1
        if cloudRubric:
            self.rubrics  ,  self.vends  ,  self.all_headers  ,  self.tags = Gspread_Rubric.read_formatting_gsheet() 
        else:
            self.rubrics  ,  self.vends  ,  self.all_headers  ,  self.tags = read_formatting_spreadsheet(pathing_dict['rubric_path'])
  
        self.vendor_codes = JFGC.vendorDict;
        self.vendor_names =   list(self.vendor_codes.keys())
        self.vendor_names.reverse()

        #self.taxDict    =   JFGC.taxDict;

        self.JFGC = JFGC
        self.pathing_dict = pathing_dict

    def lock_info(self,sender,app_data,user_data):
        # Helper function for cleaning up the UI after a file's information is accepted for batch processing.
        # If the box is checked, do not show.
        if      app_data: 
                app_data=False
        else:   app_data=True

        dpg.configure_item(user_data+'_window',show=app_data)

        if not app_data: 
            dpg.configure_item(user_data+'_save',label="")
        else:
            dpg.configure_item(user_data+'_save',label="Information Correct?")
        
    def helper_update_taxDesc(self,sender, app_data,user_data):
        # Helper function for updating Tax code labels upon selection.
        dpg.configure_item(
            user_data,
            default_value=self.JFGC.taxDict[app_data])

    def helper_update_vendorNum(self,sender, app_data,user_data):
        # Helper function for quickly updating vendor number during selection.
        dpg.configure_item(user_data,default_value=self.vendor_codes[app_data])

    def helper_update_vendorlist(self,sender,app_data,user_data):
        #---------------------------
        #0: combo
        #self.vendor_names,
        #self.vendor_codes
        #---------------------------
        print (user_data)
        vend        = self.vendor_names
        guess_val   = app_data.upper()
        #---------------------------
        if len(guess_val)!=0:
            num_helper  =    int((len(guess_val)/2)+1)
        else:
            num_helper  =   1
        #---------------------------
        temp_vendor_names   =   [i for i in vend if i.startswith(guess_val[0:num_helper])]
        print(temp_vendor_names)
        try:
            dpg.configure_item(user_data+'_combo', items=temp_vendor_names,default_value=temp_vendor_names[0])
        except:
            dpg.configure_item(user_data+'_combo', items=temp_vendor_names,default_value="~NONE FOUND~")
        dpg.configure_item(user_data+'_vendorCodeDisplay',default_value=self.vendor_codes[dpg.get_value(user_data+'_combo')])

    def helper_update_headerCheck(self,sender,app_data,user_data):
        pass

    def helper_showQtyAlloc(self,sender,app_data,user_data):
        # Helper function for displaying a special combo box that specifies what to do with a given file's QTY if 'BOTH' stores are selected
        box_name    = f"{user_data}_qtyDivide"
        val         = dpg.get_value(f"{user_data}_storeLoc")
        if val=="Both":
            dpg.configure_item(item=box_name,show=True)

    def helper_guess_val(self,value):
        # This function allows me to format common, problematic vendornames so that when clerks or GMs format them 
        #   with colloquial naming, the process isn't slowed down. 
        #   For example: a file might be written as '180' but in fact the vendor name is saved alphabetically as "One Hundred 80"
        # ========================================
        # TO DO:
        #   - allow manual editing, saving, etc
        guess_val   =   ""
        #------------------------
        if value=="KSA":
            guess_val="ADLER"
        elif value.startswith("180"):
            guess_val="One Hundred 80".upper()
        elif value=="Arett" or value=="arett".upper() or value=="arett":
            guess_val="ARETT".upper()
        #elif : 
        #   guess_val = 
        #------------------------
        # ========================================
        if guess_val!="":   return value
        else:               return guess_val

    def helper_saveRubricFiddle(sender,app_data,user_data):
        # Accepts the UI data for a new on-the-fly rubric and either sends a good popup or a bad.
        #   If good, will also create that rubric in the Google Doc Rubric File
        #----------------------------------
        vendorfileObj   =   user_data
        rubric_name     =   dpg.get_value(f"{vendorfileObj.name}_rubric_fiddleName")
        subname         =   dpg.get_value(f"{vendorfileObj.name}_rubric_subName")
        rubric_vals     =   {}
        #----------------------------------
        for item in vendorfileObj.header:
            combo_val   =   dpg.get_value(f"{vendorfileObj.name}_{item}_combo")
            #=================
            # Should re-write to ensure that all fields are accounted for
            # Could do another way, but must format here for the weird way i've been doing it:
            # combo_items =["~","UPC","Manufacturer #","Description","Cost","Retail","Qty"]
            if combo_val        ==  "~":
                weird_format    =   ''
            elif combo_val      ==  "UPC":
                weird_format    =   1
            elif combo_val      ==  "Manufacturer #":
                weird_format    =   2
            elif combo_val      ==  "Description":
                weird_format    =   3
            elif combo_val      ==  "Cost":
                weird_format    =   4
            elif combo_val      ==  "Retail":
                weird_format    =   5
            elif (combo_val      ==  "Qty") or (combo_val      ==  "Quantity"):
                weird_format    =   13
            #=================
            rubric_vals.update({item:weird_format})
        #----------------------------------
        for val in rubric_vals.values():
            if val!='' and list(rubric_vals.values()).count(val)>1:
                with dpg.window(popup=True):
                    dpg.add_text(f"Multiple instances of cell value claimed for new rubric! Can only have one of each!")
                return False
        #----------------------------------
        status,msg = Gspread_Rubric.add_rubric(rubric_name,subname,rubric_vals)
        with dpg.window(popup=True):
            dpg.add_text(msg)
        #----------------------------------
        if status:
            # If the status is good, immediately set that vendorfile object's rubric to format as the one that was just created. 
            self.rubrics  ,  self.vends  ,  self.all_headers  ,  self.tags = Gspread_Rubric.read_formatting_gsheet() 

            temp_name           = rubric_name+"_"+subname
            vendor_format_dict ={}
            for column in self.vends[temp_name].keys():
                #-----------------
                index = vendor_dict[column]
                #-----------------
                try: 
                    # Tries to update the temp_dict with the 
                    vendor_format_dict.update({self.rubrics[list(self.rubrics.keys())[0]][index]:column})
                except:
                    pass

            vendorfileObj.set_formatting_dict(name=temp_name,format=vendor_format_dict)
        #----------------------------------
        return status

    def find_rubric(self,vendorfileObj,annotations=False):

        # Vendorfile headers are messy. 
        # They sometimes have tons of extra 'None' values returned with them, and are full of variations that will need to be accounted for.
        # The base vendor_rubrics we have, though, represent the minimum needed column values for successfully autoformatting. 
        found = False

        for vendor_name in self.vends.keys():
                                
            if self.all_headers[vendor_name] == vendorfileObj.header:
                                
                if annotations: 
                    #print ("MATCH: ",str(match_count)); match_count+=1
                    print ("\t"+str(vendorfileObj.name))
                    print ("\t"+str(vendor_name))
                    print ("\t\t"+str(vendorfileObj.header))
                    print ("\t\t"+str(self.all_headers[vendor_name]))
                    print ("============================")

                #--------------------
                found = True

                header_to_display   = self.all_headers[vendor_name]
                #--------------------
                vendor_format_dict={}
                for column in self.vends[vendor_name].keys():
                    index=self.vends[vendor_name][column]
                    try: 
                        # Tries to update the temp_dict with the 
                        vendor_format_dict.update({self.rubrics[list(self.rubrics.keys())[0]][index]:column})
                    except:
                        #temp_dict.update({rubrics[rubric][index]:column}
                        pass
                #--------------------
                #vendor_format_dict  = zip_formatting_dict(self.rubrics[list(self.rubrics.keys())[0]],self.vends[vendor_name])                
                vendorfileObj.set_formatting_dict(vendor_name, vendor_format_dict)
                dpg.configure_item(vendorfileObj.name+"_headerName",default_value=vendor_name,show=True,color=(127, 255, 212))
                #--------------------
                #rubric_header_group = dpg.add_group(horizontal = True)
                for index,item in enumerate(header_to_display):
                    if item != 'None' and item != None:
                        print(f'CONFIG: {vendorfileObj.name}_rubric_headercheck_{index}')

                        dpg.configure_item(f'{vendorfileObj.name}_rubric_headercheck_{index}',default_value=f'| {item} ')
                #--------------------
                break
      
            # COuld create another check here such that, if nothing is still found, re-iterate, 
            # and look for the .issubset functionality contained originally. 
        if not found:
            vendorfileObj.set_formatting_dict(None,None)
            #dpg.add_text(f'NO FORMAT FOUND --> Create a new one with the next tab!')
            dpg.configure_item(vendorfileObj.name+"_headerName",show=True,color   =   (238, 75, 43))

    def processing_helper(sender,app_data,user_data):
        # Generic Helper Class for either Individual or Multiple file processing.
        #---------------------------
        vendorfile_list =   user_data[0]
        pathing_dict    =   user_data[1]
        today           =   user_data[2]
        annotations     =   user_data[3]
        #---------------------------
        list_to_process =   []
        #---------------------------
        for vendorfileObj in vendorfile_list:
            # If the item is going to be processed...
            if dpg.get_value(vendorfileObj.name+"_save")==True:
                # If that item's store has been correctly specified...
                if dpg.get_value(vendorfileObj.name+'_storeLoc') not in ["Kens","Olney","Both"]:
                    with dpg.window(popup=True):
                        dpg.add_text("A vendorfile has been checked but no store selected!")
                    return
                else:
                    #------------
                    tax         =   dpg.get_value(vendorfileObj.name+"_tax")
                    code        =   dpg.get_value(vendorfileObj.name+"_vendorCodeDisplay")
                    temp_dept   =   dpg.get_value(vendorfileObj.name+"_dept")
                    dept        =   dept_dict_fwds[temp_dept]  
                    #------------
                    vendorfileObj.set_manual_input(tax,code,dept)
                    #------------
                    list_to_process.append(vendorfileObj)
        #---------------------------
        if list_to_process==[]:
            with dpg.window(popup=True):
                dpg.add_text("No vendorfiles selected!\nPlease check which files are ready to process.")
                return
        #---------------------------
        process_inputs(list_to_process,pathing_dict,today,annotations)

    def vendorChildWindow(self,vendorfileObj: vendorfile):
        #============================================================== 
        print (":::::::::::::::::::_",vendorfileObj.name)
        if vendorfileObj.note.lower() not in self.suggestedSaveName_content:
            self.suggestedSaveName_content.append(vendorfileObj.note.lower())
        #==============================================================
        with dpg.child_window(tag=vendorfileObj.name+"_entireChild",width=810,height=190,no_scrollbar=False):
            #==============================================================
            with dpg.child_window(tag=vendorfileObj.name+"_informationCheckerChild", border=False,width=700,height=45):
                dpg.add_text(
                    default_value = vendorfileObj.name,
                    color   =   (60,200,100))
                file_options_a = dpg.add_group(horizontal=True)
                dpg.add_checkbox(
                    tag     =   vendorfileObj.name+'_save',
                    label   =   "Information Correct?",
                    parent  =   file_options_a)
                dpg.add_combo(
                    tag     =   vendorfileObj.name+'_storeLoc',
                    label   =   "Store",
                    items   =   ["Kens","Olney","Both"],
                    width   =   60,
                    callback=   self.helper_showQtyAlloc,
                    user_data = vendorfileObj.name,
                    parent  =   file_options_a)
                dpg.add_checkbox(
                    tag     =   f"{vendorfileObj.name}_overwritePrice",
                    label   =   "Overwrite Price?",
                    parent  =   file_options_a)
                dpg.add_progress_bar(
                    tag     =   vendorfileObj.name+'_prog',
                    overlay =   "% Complete",
                    show    =   True,
                    width   =   200,
                    parent  =   file_options_a)
                dpg.add_text(
                    tag      =   vendorfileObj.name+'_error',
                    show    =   False)
                dpg.add_combo(items=['Divide Evenly','Copy Quantities'],width=250,default_value="CHOOSE ONE",id=vendorfileObj.name+'_qtyDivide',label="StoreQtys?",show=False)
            #============================================================== 
            with dpg.tab_bar():
                with dpg.tab(label="Information"):
                    with dpg.child_window(tag=vendorfileObj.name+"_window", width=790, height=100,no_scrollbar=True):
                        information_group = dpg.add_group(horizontal=True)
                        #--------------------
                        # VENDOR
                        #--------------------
                        vendor_group = dpg.add_group(horizontal=False,parent = information_group)
                        vendorinfo_group = dpg.add_group(horizontal=True,parent = vendor_group)
                        dpg.add_text(default_value="Vendor Code:",parent=vendorinfo_group)
                        dpg.add_text(id=vendorfileObj.name+"_vendorCodeDisplay",default_value="XXXXXX",parent=vendorinfo_group,color=(160,160,250))
                        dpg.add_input_text(default_value=vendorfileObj.vendorName,width=150,id=vendorfileObj.name+'_vend',parent=vendor_group)
                        #--------------------
                        guess_val = dpg.get_value(vendorfileObj.name+'_vend').upper()
                        # Formats common, problematic titles 
                        guess_val = self.helper_guess_val(guess_val)
                        #--------------------
                        if len(guess_val)!=0:   num_helper  =   int((len(guess_val)/2)+1)
                        else:                   num_helper  =   1
                        #--------------------
                        # Sets list of vendor names to be only that which starts with what's written in the input text.
                        # The callback duplicates this functionality
                        temp_vendor_names=[i for i in self.vendor_names if i.startswith(guess_val[0:num_helper])]
                        #--------------------
                        try:        dpg.add_combo(items=temp_vendor_names,id=vendorfileObj.name+'_combo',default_value=temp_vendor_names[0], width=150,parent=vendor_group)
                        except:     dpg.add_combo(items=temp_vendor_names,id=vendorfileObj.name+'_combo',default_value=guess_val, width=150,parent=vendor_group)
                        #--------------------
                        # DEPT
                        #--------------------
                        dept_group = dpg.add_group(horizontal=False,parent = information_group)
                        dpg.add_text(default_value="Department Code",parent=dept_group)
                        try:
                            dpg.add_combo(width=160,id=vendorfileObj.name+"_dept",items = list(self.JFGC.dptByStr.keys()),default_value=self.JFGC.getDptByCode(vendorfileObj.department).dptStr,parent=dept_group)
                        except:
                            dpg.add_combo(width=160,id=vendorfileObj.name+"_dept",items = self.JFGC.dptByStr.keys(),default_value='~None Found~',parent=dept_group)
                        #--------------------
                        # TAX
                        #--------------------
                        tax_group = dpg.add_group(horizontal=False,parent = information_group)
                        taxinfo_group = dpg.add_group(horizontal=True,parent = tax_group)
                        dpg.add_text(default_value="Tax Code:",parent=taxinfo_group)
                        dpg.add_text(list(self.JFGC.taxDict.values())[0], id=vendorfileObj.name+'_taxinfo',parent=taxinfo_group,color=(160,160,250))
                        dpg.add_combo(width=100,items=list(self.JFGC.taxDict.keys()),id=vendorfileObj.name+'_tax',default_value=list(self.JFGC.taxDict.keys())[0],parent=tax_group)
                        #===================================================  
                        # Updates Combo box     based on vendor input
                        dpg.set_item_callback(vendorfileObj.name+'_vend',self.helper_update_vendorlist)
                        dpg.set_item_user_data(vendorfileObj.name+'_vend',vendorfileObj.name)
                        # Updates Vendor Code   based on    combo choice
                        dpg.set_item_callback(vendorfileObj.name+'_combo',self.helper_update_vendorNum)
                        dpg.set_item_user_data(vendorfileObj.name+'_combo',vendorfileObj.name+'_vendorCodeDisplay')
                        # Updates TaxInfo       based on    tax choice
                        dpg.set_item_callback(vendorfileObj.name+'_tax',self.helper_update_taxDesc)
                        dpg.set_item_user_data(vendorfileObj.name+'_tax',vendorfileObj.name+'_taxinfo')
                        #===================================================
                        try:
                            dpg.configure_item(vendorfileObj.name+"_vendorCodeDisplay",default_value=self.vendor_codes[dpg.get_value(vendorfileObj.name+'_combo')])
                        except: 
                            pass
                with dpg.tab(label="Header Check"):
                    with dpg.child_window(tag=vendorfileObj.name+"_headerCheckWindow", width=790, height=100,no_scrollbar=False,horizontal_scrollbar=True):
                            dpg.add_text(tag=vendorfileObj.name+"_headerName",default_value = "NO FORMAT FOUND --> Create a new one with the next tab!",show=False)

                            temp_header = vendorfileObj.header

                            for index,item in enumerate(vendorfileObj.header):
                                try:
                                    temp_header[index]=item.strip()
                                except:
                                    temp_header[index]=item
                            #====================================================
                            file_header_group = dpg.add_group(horizontal = True)
                            dpg.add_input_text(default_value=f"FILE:", readonly=True,parent=file_header_group,width=55)
                            for item in temp_header:
                                if item != 'None' and item != None:
                                    dpg.add_text(f'| {item} ',parent=file_header_group,tag=f'{vendorfileObj.name}_file_headercheck_{item}')
                            dpg.add_separator()
                            #----------------------------------------------------
                            rubric_header_group = dpg.add_group(horizontal = True)
                            dpg.add_input_text(default_value=f"RUBRIC:", readonly=True,parent=rubric_header_group,width=55)
                            for index,item in enumerate(temp_header):
                                if item != 'None' and item != None:
                                    print(f'BUILD: {vendorfileObj.name}_rubric_headercheck_{index}')
                                    dpg.add_text(f'| {"~"*len(item)} ',parent=rubric_header_group,tag=f'{vendorfileObj.name}_rubric_headercheck_{index}')
                            #====================================================
                            self.find_rubric(vendorfileObj)
                            # need to add the rubric header before and have the above function configure the text
                            #   INSTEAD of writing it

                with dpg.tab(label="Rubric Fiddle",tag=vendorfileObj.name+'_rubricFiddle'):
                    with dpg.child_window(tag=vendorfileObj.name+"_rubricFiddleWindow", width=790, height=100,no_scrollbar=False,horizontal_scrollbar=True):
                        #import from somewhere else:
                        rubric_combo_items =["~","UPC","Manufacturer #","Description","Cost","Retail","Quantity"]
                
                        fiddle_row_0 = dpg.add_group(horizontal=True)

                        dpg.add_button(id=f"{vendorfileObj.name}_rubric_fiddleSave",label="Save Rubric",callback=self.helper_saveRubricFiddle,user_data=vendorfileObj,parent=fiddle_row_0,width=40)
                        dpg.add_input_text(id=f"{vendorfileObj.name}_rubric_fiddleName",label="Rubric Name",parent=fiddle_row_0,width=120)
                        dpg.add_input_text(id=f"{vendorfileObj.name}_rubric_subName",label="Subtitle",parent=fiddle_row_0,width=80)

                        fiddle_row_1 = dpg.add_group(horizontal=True)
                        fiddle_row_2 = dpg.add_group(horizontal=True)

                        print(vendorfileObj.header)

                        for item in vendorfileObj.header:
                            component_width=8*len(f"{item}")
                            dpg.add_input_text(default_value=f"{item}", readonly=True,parent=fiddle_row_1,width=component_width)

                            if item in rubric_combo_items:
                                default_fiddle = rubric_combo_items[rubric_combo_items.index(item)]
                            else:
                                default_fiddle = rubric_combo_items[0]

                            dpg.add_combo(id=f"{vendorfileObj.name}_{item}_combo",items=rubric_combo_items,default_value = default_fiddle,parent=fiddle_row_2,width=component_width)

                            #try:
                            #except:
                            #    print("----------------------- Duplicate name: trying")
                            #    print (f"HERE::::::::::::::: {vendorfileObj.name}_{item}_combo")
                            #    dpg.add_combo(id=f"{vendorfileObj.name}_{item}_combo",items=rubric_combo_items,default_value = default_fiddle,parent=fiddle_row_2,width=component_width)
            #===================================================
            dpg.set_item_callback(vendorfileObj.name+'_save',self.lock_info)
            dpg.set_item_user_data(vendorfileObj.name+'_save',vendorfileObj.name)
            # After Save button: logs all the appropriate data into the vendorfile OBJ and continues.
            # logs based on names, so be sure that when we're calling down below, we are calling the items saved here, NOT the ones created below.
        dpg.add_separator()

    def importerWindow(self,vendorfileObjList):
        #====================================================
        if len(vendorfileObjList)<=0:
            with dpg.window(popup=True):
                dpg.add_text("No csv/xlsx files found at input folder selected.!")
            return
        #====================================================
        # Begin UI
        with dpg.window(label="Manual Input Required",tag=f'manual_input_{self.__count}',width=830,height=(300+(115*int(len(vendorfileObjList))))):
            #----------------------------------------------------
            options_group = dpg.add_group(horizontal = True)
            dpg.add_button(tag="process_button",label="Begin Processing",width=120,height=60,parent=options_group)
            options_col_a = dpg.add_group(horizontal = False,parent=options_group)
            dpg.add_checkbox(tag="process_wix",label="Process files into WIX format?",default_value=True,parent=options_col_a),
            dpg.add_checkbox(tag="auto_wix",label="Automatically update website?",default_value=False,parent=options_col_a)
            dpg.add_checkbox(tag="move_files",label="Move files after completion?",default_value=True,parent=options_col_a)
            options_col_b = dpg.add_group(horizontal = False,parent=options_group)
            dpg.add_checkbox(tag="barcode_lookup",label="Enable Barcode Lookup?",default_value=False,parent=options_col_b)
            dpg.add_checkbox(tag="skipDuplicates",label="Skip Duplicate Lines?",default_value=False,parent=options_col_b)
            #----------------------------------------------------
            dpg.add_separator()
            #----------------------------------------------------
            save_group = dpg.add_group(horizontal = True)
            dpg.add_input_text(tag="outputFileName",label="Save as",width=300, parent=save_group)
            dpg.add_checkbox(tag='defaultSave?',label="Use generic save instead?",default_value=False,parent=save_group)
            #----------------------------------------------------
            dpg.add_separator()
            #----------------------------------------------------
            for vendorfile in vendorfileObjList:
                self.vendorChildWindow(vendorfile)
            #===================================================
            saveStr="Inventory-"
            for item in self.suggestedSaveName_content:
                saveStr+=item+'-'
            #===================================================
            dpg.configure_item("outputFileName",default_value=saveStr)
            dpg.set_item_callback("process_button",self.processing_helper)
            today = date.today()
            dpg.set_item_user_data("process_button",[vendorfileObjList,self.pathing_dict,today,True])