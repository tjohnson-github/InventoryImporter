from Vendorfile import vendorfile
import Gspread_Rubric
import dearpygui.dearpygui as dpg

import datetime
from datetime import date


class Importer:

    suggestedSaveName_content: list = []

    def __init__(self,JFGC,pathing_dict,cloudRubric=True):
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


    def helper_showQtyAlloc(self,sender,app_data,user_data):
        # Helper function for displaying a special combo box that specifies what to do with a given file's QTY if 'BOTH' stores are selected
        box_name    = f"{user_data}_qtyDivide"
        val         = dpg.get_value(f"{user_data}_storeLoc")
        if val=="Both":
            dpg.configure_item(item=box_name,show=True)

    def guess_val_helper(self,value):
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
        for item in vendorfile_list:
            # If the item is going to be processed...
            if dpg.get_value(item.name+"_save")==True:
                # If that item's store has been correctly specified...
                if dpg.get_value(item.name+'_storeLoc') not in ["Kens","Olney","Both"]:
                    with dpg.window(popup=True):
                        dpg.add_text("A vendorfile has been checked but no store selected!")
                    return
                else:
                    #------------
                    tax         =   dpg.get_value(item.name+"_tax")
                    code        =   dpg.get_value(item.name+"_vendorCodeDisplay")
                    temp_dept   =   dpg.get_value(item.name+"_dept")
                    dept        =   dept_dict_fwds[temp_dept]  
                    #------------
                    item.set_manual_input(tax,code,dept)
                    #------------
                    list_to_process.append(item)
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
        dpg.add_text(
            default_value = vendorfileObj.name,
            color   =   (60,200,100))
        file_options_a = dpg.add_group(horizontal=True)
        dpg.add_checkbox(
            id      =   vendorfileObj.name+'_save',
            label   =   "Information Correct?",
            parent  =   file_options_a)
        dpg.add_combo(
            id      =   vendorfileObj.name+'_storeLoc',
            label   =   "Store",
            items   =   ["Kens","Olney","Both"],
            width   =   60,
            callback=   self.helper_showQtyAlloc,
            user_data = vendorfileObj.name,
            parent  =   file_options_a)
        dpg.add_checkbox(
            id      =   f"{vendorfileObj.name}_overwritePrice",
            label   =   "Overwrite Price?",
            parent  =   file_options_a)
        dpg.add_progress_bar(
            id      =   vendorfileObj.name+'_prog',
            overlay =   "% Complete",
            show    =   True,
            width   =   200,
            parent  =   file_options_a)
        dpg.add_text(
            id      =   vendorfileObj.name+'_error',
            show    =   False)
        dpg.add_combo(items=['Divide Evenly','Copy Quantities'],width=250,default_value="CHOOSE ONE",id=vendorfileObj.name+'_qtyDivide',label="StoreQtys?",show=False)
        #============================================================== 
        with dpg.tab_bar():
            with dpg.tab(label="Information"):
                with dpg.child(tag=vendorfileObj.name+"_window", width=800, height=87,no_scrollbar=True):
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
                    guess_val = self.guess_val_helper(guess_val)
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
                        dpg.add_combo(width=130,id=vendorfileObj.name+"_dept",items = list(self.JFGC.dptByStr.keys()),default_value=self.JFGC.getDptByCode(vendorfileObj.department).dptStr,parent=dept_group)
                    except:
                        dpg.add_combo(width=130,id=vendorfileObj.name+"_dept",items = self.JFGC.dptByStr.keys(),default_value='~None Found~',parent=dept_group)
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
                    #Could add header or selectors here
                    #dpg.add_text(vendorfileobj.header)
                #===================================================
                dpg.set_item_callback(vendorfileObj.name+'_save',self.lock_info)
                dpg.set_item_user_data(vendorfileObj.name+'_save',vendorfileObj.name)
                # After Save button: logs all the appropriate data into the vendorfile OBJ and continues.
                # logs based on names, so be sure that when we're calling down below, we are calling the items saved here, NOT the ones created below.
                dpg.add_separator()

    def importerWindow(self,vendorfileObjList):
        if len(vendorfileObjList)>1:
            individualOrMultiple = 'multiple'
        elif len(vendorfileObjList)==1:
            individualOrMultiple = 'individual'
        else:
            #display popup that no files were found
            pass

        #====================================================
        # Begin UI
        with dpg.window(label="Manual Input Required",tag='manual_input_'+individualOrMultiple,width=820,height=(300+(80*int(len(vendorfileObjList))))):
            #----------------------------------------------------
            options_group = dpg.add_group(horizontal = True)
            dpg.add_button(label="Begin Processing",id="process_button",width=120,height=60,parent=options_group)
            options_col_a = dpg.add_group(horizontal = False,parent=options_group)
            dpg.add_checkbox(id="process_wix",label="Process files into WIX format?",default_value=True,parent=options_col_a),
            dpg.add_checkbox(id="auto_wix",label="Automatically update website?",default_value=False,parent=options_col_a)
            dpg.add_checkbox(id="move_files",label="Move files after completion?",default_value=True,parent=options_col_a)
            options_col_b = dpg.add_group(horizontal = False,parent=options_group)
            dpg.add_checkbox(id="barcode_lookup",label="Enable Barcode Lookup?",default_value=False,parent=options_col_b)
            dpg.add_checkbox(id="skipDuplicates",label="Skip Duplicate Lines?",default_value=False,parent=options_col_b)
            #----------------------------------------------------
            dpg.add_separator()
            #----------------------------------------------------
            save_group = dpg.add_group(horizontal = True)
            dpg.add_input_text(id="outputFileName",label="Save as",width=300, parent=save_group)
            dpg.add_checkbox(id='defaultSave?',label="Use generic save instead?",default_value=False,parent=save_group)
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


def manualInput(vendorfileObjList,pathing_dict,individualOrMultiple,cloudRubric=True): 
   
        # BEGIN FILE ITERATOR
        for vendorfile in vendorfileObjList:
         
            #==============================================================
            with dpg.tab_bar():
                with dpg.tab(label="Information"):
                    with dpg.child(id=vendorfileobj.filename+"_window", width=800, height=67,no_scrollbar=True):
                        with dpg.table(header_row=False):
                            #===================================================  
                            # Updates Combo box     based on vendor input
                            dpg.set_item_callback(vendorfileobj.filename+'_vend',update_vendorlist)
                            #dpg.set_item_user_data(vendorfileobj.filename+'_vend',[vendorfileobj.filename+'_combo',vendor_names])
                            dpg.set_item_user_data(vendorfileobj.filename+'_vend',[vendorfileobj.filename,vendor_names,vendor_codes])
                            # Updates Vendor Code   based on    combo choice
                            dpg.set_item_callback(vendorfileobj.filename+'_combo',update_vendorNum)
                            dpg.set_item_user_data(vendorfileobj.filename+'_combo',[vendorfileobj.filename+'_code',vendor_codes])
                            # Updates TaxInfo       based on    tax choice
                            dpg.set_item_callback(vendorfileobj.filename+'_tax',update_taxDesc)
                            dpg.set_item_user_data(vendorfileobj.filename+'_tax',[vendorfileobj.filename+'_taxinfo',tax_meaning])
                            #===================================================
                        #Could add header or selectors here
                        #dpg.add_text(vendorfileobj.header)
                    #===================================================
                    #dpg.add_same_line(spacing=5)
                    dpg.set_item_callback(vendorfileobj.filename+'_save',lock_info)
                    dpg.set_item_user_data(vendorfileobj.filename+'_save',vendorfileobj.filename)
                    # After Save button: logs all the appropriate data into the vendorfile OBJ and continues.
                    # logs based on names, so be sure that when we're calling down below, we are calling the items saved here, NOT the ones created below.
                    dpg.add_separator()

                with dpg.tab(label="Header Check"):

                    with dpg.child(id=vendorfileobj.filename+"_headerCheckWindow", width=800, height=80,no_scrollbar=True):

                        dpg.add_text(id=vendorfileobj.filename+"_headerName")

                        with dpg.table(header_row=False,resizable= True):


                            temp_header = vendorfileobj.header
                            for index,item in enumerate(temp_header):
                                try:
                                    temp_header[index]=item.strip()
                                except:
                                    temp_header[index]=item

                            for item in vendorfileobj.header:
                                if item != 'None' and item != None:
                                    dpg.add_table_column()
                                    dpg.add_text(f'| {item} ')
                                    dpg.add_table_next_column()

                            print ('==============')
                            #for x in rubrics:
                            #    print (x)
                            # =====================================================
                            # This is where the decision is made as to which rubric header line matches the current file's header line. 
                            found = False
                            for vendor_name in vends.keys():
                                # Vendorfile headers are messy. They sometimes have tons of extra 'None' values returned with them, and are full of variations that will need to be accounted for.
                                # The base vendor_rubrics we have, though, represent the minimum needed column values for successfully autoformatting. 
                                
                                
                                #if set(all_headers[vendor_name]).issubset(temp_header):
                                if all_headers[vendor_name] == temp_header:
                                
                                    
                                    if annotations: 
                                        #print ("MATCH: ",str(match_count)); match_count+=1
                                        print ("\t"+str(vendorfileobj.filename))
                                        print ("\t"+str(vendor_name))
                                        print ("\t\t"+str(vendorfileobj.header))
                                        print ("\t\t"+str(all_headers[vendor_name]))
                                        print ("============================")
                                    vendor = vendor_name
                                    header_to_display = all_headers[vendor_name]
                                    #--------------------
                                    found = True
                                    vendor_format_dict = zip_formatting_dict(rubrics[list(rubrics.keys())[0]],vends[vendor])
                                    #--------------------
                                    #print (vendor_format_dict)
                                    break
                                else:
                                    #print (vendorfileobj.header)
                                    #print (all_headers[vendor_name])
                                    pass


                                # COuld create another check here such that, if nothing is still found, re-iterate, 
                                # and look for the .issubset functionality contained originally. 

                            if found:
                                # If a rubric is found, attach it to the object. 
                                vendorfileobj.set_formatting_dict(vendor, vendor_format_dict)
                                dpg.configure_item(vendorfileobj.filename+"_headerName",default_value=vendor_name)

                                for item in header_to_display:
                                    if item != 'None' and item != None:
                                        dpg.add_text(f'| {item} ')
                                        dpg.add_table_next_column()

                            else:
                                vendorfileobj.set_formatting_dict(None,None)
                                dpg.add_text(f'NO FORMAT FOUND --> Create a new one with the next tab!')

                with dpg.tab(label="Rubric Fiddle",id=vendorfileobj.filename+'_rubricFiddle'):

                    #import from somewhere else:
                    combo_items =["~","UPC","Manufacturer #","Description","Cost","Retail","Quantity"]

                    with dpg.table(header_row=False,resizable=True):

                        #rubric_name = f"{vendorfileobj.filename}_rubric_fiddleName"

                        dpg.add_table_column()
                        dpg.add_button(id=f"{vendorfileobj.filename}_rubric_fiddleSave",label="Save Rubric",callback=saveRubricFiddle,user_data=vendorfileobj)
                        dpg.add_table_next_column()
                        dpg.add_table_column()
                        dpg.add_input_text(id=f"{vendorfileobj.filename}_rubric_fiddleName",label="Rubric Name")
                        dpg.add_table_next_column()
                        dpg.add_table_column()
                        dpg.add_input_text(id=f"{vendorfileobj.filename}_rubric_subName",label="Subtitle")

  
                    with dpg.table(header_row=False,resizable=True):

                        for item in vendorfileobj.header:
                            dpg.add_table_column()
                            dpg.add_input_text(default_value=f"{item}", readonly=True)
                            dpg.add_table_next_column()

                        dpg.add_table_row()

                        print (vendorfileobj.header)

                        temp_header = vendorfileobj.header
                        while temp_header[-1]=='None':
                            temp_header = temp_header[:-2]

                        #for item in vendorfileobj.header:
                        for item in temp_header:
                            dpg.add_table_next_column()
                            print (item)
                            print (combo_items)
                            if item in combo_items:
                                default_fiddle = combo_items[combo_items.index(item)]
                            else:
                                default_fiddle=combo_items[0]

                            try:
                                dpg.add_combo(id=f"{vendorfileobj.filename}_{item}_combo",items=combo_items,default_value = default_fiddle)
                            except:
                                print("----------------------- Duplicate name: trying")
                                print (f"HERE::::::::::::::: {vendorfileobj.filename}_{item}_combo")
                                dpg.add_combo(id=f"{vendorfileobj.filename}_{item}_combo",items=combo_items,default_value = default_fiddle)

                with dpg.tab(label="Expand View",id=vendorfileobj.filename+'_expandTest'):

                    dpg.add_button(id=vendorfileobj.filename+'_expandBtn',label="Display Expanded Editor",callback=vendorfileobj.expandedView)

                
        #===================================================
        saveStr="Inventory-"
        for item in suggestedSaveName_content:
            saveStr+=item+'-'
        #===================================================
        dpg.configure_item("outputFileName",default_value=saveStr)
        #dpg.add_text("<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>")
        dpg.set_item_callback("process_button",processing_helper)
        today = date.today()
        dpg.set_item_user_data("process_button",[list_of_vendorfile_objs,pathing_dict,today,True])