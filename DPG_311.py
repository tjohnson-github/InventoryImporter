

import dearpygui.dearpygui as dpg

#from JFGC_Data import dept_comb
import Utilities

import JFGC_Data
JFGC = JFGC_Data.JFGC_Data()


#====================================================
#================== HELPER FUNCTIONS


def scanInputs(cloudRubric=True, automatePDF = False):
    #====================================================
    # Given a set of filepaths, scan all possible files in the INPUT folder and create the appropriate
    #   UI-based objects which will allow for manual input to more accurately process the vendorfiles.
    #====================================================
    
    #====================================================
    excel_files_to_process  =   fnmatch.filter(os.listdir(input_filepath), '*.xlsx')
    csv_files_to_process    =   fnmatch.filter(os.listdir(input_filepath), '*.csv')
    pdf_files_to_process    =   fnmatch.filter(os.listdir(input_filepath), '*.pdf') if automatePDF else []
    #====================================================
    print ("=========================================")
    #====================================================
    """ The master_processing_dict is the main variable for all data manipulation regarding ImportInventory
        It has format: 
            { 'filename' : [list_of_rows] }
        with 
            list_of_rows[0] = the header contained within 'filename'
    """
    master_processing_dict={}
    #====================================================
    # Converts PDFs to CSVs in the same directory which will subsquently be processed by csv_to_list
    for file in pdf_files_to_process:
 
        print (f'Cannot convert {file} to CSV in the same step as processing CSVs.\tPDFs too often require manual validation.')

        #PDF_Scraper.scrape_pdf(input_path=input_filepath,output_path=input_filepath,filename=file,annotations=annotations)
        #File_Operations.cleanup(file,input_filepath,processed_path) 
        #print("\t"+file+" successfully converted to csv.\n\t\tMoving from "+input_filepath+" to "+processed_path+"\n")
    #====================================================
    # Converts XLSXs to arrays and adds them to the master processor. 
    for file in excel_files_to_process:
        output_array,errorMsg    =   File_Operations.excel_to_list(input_filepath+file)
        #----------------------
        if output_array==False: 
            print("\t"+errorMsg+"\n"); continue
        #----------------------
        master_processing_dict.update(  {   file    :  output_array  })
    #====================================================
    # Converts CSVs to arrays and adds them to the master processor. 
    for file in csv_files_to_process:
        output_array,errorMsg    =   File_Operations.csv_to_list(input_filepath+file)
        #----------------------
        if output_array==False: 
            print("\t"+errorMsg+"\n"); continue
        #----------------------
        master_processing_dict.update(  {   file    :  output_array  })
    #====================================================
    return master_processing_dict

def formatPathingDict():
    # If the default is selected, uses default for all entries
    # If custom is selected, uses default for all entries EXCEPT the custom input folder to scan.
    #====================================================
    pathingDict: dict = {}
    pathingDict['parent_path']          =   dpg.get_value('base_parent_directory')
    pathingDict['ouput_filepath']       =   dpg.get_value('base_output_path')
    pathingDict['processed_path']       =   dpg.get_value('base_processed_path')
    pathingDict['rubric_path']          =   dpg.get_value('base_rubric_path')
    #====================================================
    if user_data=="default":
        pathingDict['input_filepath']   =   dpg.get_value('base_input_path')
    elif user_data=="custom":
        pathingDict['input_filepath']   =   dpg.get_value('input_path')
    #====================================================
    # Final formatting
    for key,val in enumerate(pathingDict.items()):
        pathingDict[key] = val + "\\"
    #====================================================
    return pathingDict

def manualInput(master_processing_dict,pathing_dict,individualOrMultiple,cloudRubric=True): 
    #====================================================
    if cloudRubric:
        rubrics  ,  vends  ,  all_headers  ,  tags = Gspread_Rubric.read_formatting_gsheet() 
    else:
        rubrics  ,  vends  ,  all_headers  ,  tags = read_formatting_spreadsheet(pathing_dict['rubric_path'])
    #====================================================
    # Prepare Vendor Info for Manual UI
    vendor_codes    =   JFGC.vendorDict;
    vendor_names    =   list(vendor_codes.keys())
    vendor_names.reverse()

    filename_items  =   ["Vendor","Notes","Dept.","Extension"]

    #tax_codes       =   ["TX","DEL","NT","DE"]
    #tax_meaning     =   ["Taxable","Delivery","Nontaxed","Edible"]
    
    taxDict    =   JFGC.taxDict;

    #====================================================
    # Begin UI
    with dpg.window(label="Manual Input Required",id='manual_input_'+individualOrMultiple,width=820,height=(300+(80*int(len(master_processing_dict.keys()))))):
        #----------------------------------------------------
        dpg.add_button(label="Begin Processing",id="process_button",width=120,height=60)
        dpg.add_same_line(spacing=100)
        with dpg.table(header_row=False):
            dpg.add_table_column()
            dpg.add_checkbox(id="process_wix",label="Process files into WIX format?",default_value=True)
            dpg.add_table_next_column()
            dpg.add_checkbox(id="auto_wix",label="Automatically update website?",default_value=False)
            # Essentially.... if the above ^ is checked, then some time after the intitial completion, the website will be called once for each item to be updated/created.
            # IF process_wix is also checked, can do the calls somewhere in there
            # IF not: then the formatting process will be identical, but the files wont be saved. 
            dpg.add_table_next_column()
            dpg.add_checkbox(id="move_files",label="Move files after completion?",default_value=True)
            dpg.add_checkbox(id="barcode_lookup",label="Enable Barcode Lookup?",default_value=False)
            dpg.add_checkbox(id="skipDuplicates",label="Skip Duplicate Lines?",default_value=False)
        #----------------------------------------------------
        dpg.add_separator()
        dpg.add_input_text(id="outputFileName",label="Save as")
        dpg.add_same_line(spacing=30)
        dpg.add_checkbox(id='defaultSave?',label="Use generic save instead?",default_value=False)
        #----------------------------------------------------
        #dpg.add_input_text(default_value=input_filepath,label=' files being displayed:',enabled=False)
        #[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
        with dpg.child(label="test", width=800, height=40,no_scrollbar=True) as child_container:
            with dpg.table(header_row=False):
                for item in filename_items:

                    dpg.add_table_column()
                    dpg.add_text(f"{item}")
                    dpg.add_table_next_column()
        #[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
        dpg.add_separator()
        dpg.add_separator()
        list_of_vendorfile_objs=[]
        suggestedSaveName_content=[]
        #----------------------------------------------------
        #----------------------------------------------------
        # BEGIN FILE ITERATOR
        for file in master_processing_dict.keys():
            #==============================================================
            # Creates a new vendorfile class object for each file... 
            #   Based on which items remain checked as "information correct" by the time the main button is pressed, 
            #   it will feed into the next part of the program a list of those objects for which information was verified correct.
            vendorfileobj = vendorfile({file : master_processing_dict[file] })
            list_of_vendorfile_objs.append(vendorfileobj)

            print (":::::::::::::::::::_",vendorfileobj.filename)
            #with dpg.child(id=vendorfileobj.filename+"_METAwindow", width=800, height=147,no_scrollbar=True):
            #==============================================================
            dpg.add_text(
                default_value = vendorfileobj.filename,
                color   =   (60,200,100))
            dpg.add_checkbox(
                id      =   vendorfileobj.filename+'_save',
                label   =   "Information Correct?")
            dpg.add_same_line(spacing=10) #-------------------------------------
            dpg.add_combo(
                id      =   vendorfileobj.filename+'_storeLoc',
                label   =   "Store",
                items   =   ["Kens","Olney","Both"],
                width   =   60,
                callback=showQtyAlloc,
                user_data = vendorfileobj.filename)
            dpg.add_same_line(spacing=10) #-------------------------------------
            dpg.add_checkbox(
                id      =   f"{vendorfileobj.filename}_overwritePrice",
                label   =   "Overwrite Price?")
            dpg.add_same_line(spacing=10) #-------------------------------------
            dpg.add_progress_bar(
                id      =   vendorfileobj.filename+'_prog',
                overlay =   "% Complete",
                show    =   True,
                width   =   200)
            dpg.add_text(
                id      =   vendorfileobj.filename+'_error',
                show    =   False)

            dpg.add_combo(items=['Divide Evenly','Copy Quantities'],width=250,default_value="CHOOSE ONE",id=vendorfileobj.filename+'_qtyDivide',label="StoreQtys?",show=False)

            #==============================================================
            with dpg.tab_bar():
                with dpg.tab(label="Information"):
                    with dpg.child(id=vendorfileobj.filename+"_window", width=800, height=67,no_scrollbar=True):
                        with dpg.table(header_row=False):
                            #===================================================
                            # ROW 1
                            for item in vendorfileobj.filename_info.keys():
                                #--------------------
                                dpg.add_table_column()
                                #vvvvvvvvvvvvvvvvvvvv
                                if item=="Dept.":
                                    try:
                                        dpg.add_combo(id=vendorfileobj.filename+"_dept", items = dept_comb,default_value=dept_dict_bkwds[int(vendorfileobj.filename_info[item])])
                                    except:
                                        dpg.add_combo(id=vendorfileobj.filename+"_dept",items = dept_comb,default_value='~None Found~')

                                elif item=="Vendor":
                                    dpg.add_input_text(default_value=vendorfileobj.filename_info[item],width=150,id=vendorfileobj.filename+'_vend')

                                elif item=="Notes":

                                    note =vendorfileobj.filename_info[item]

                                    dpg.add_text(vendorfileobj.filename_info[item],color=(160,160,250))

                                    if note.lower() not in suggestedSaveName_content:
                                            suggestedSaveName_content.append(note.lower())

                                elif item=="Extension":

                                    if vendorfileobj.filename_info[item] not in ["csv","xlsx"]:
                                        color = (240,60,100)
                                    else:
                                        color = (100,200,0)
                                    dpg.add_text("."+vendorfileobj.filename_info[item],color=color)
                                else:
                                    dpg.add_text(vendorfileobj.filename_info[item],color=(160,160,250))
                                #^^^^^^^^^^^^^^^^^^^^
                                dpg.add_table_next_column()
                                #--------------------
                            #===================================================
                            # ROW 2

                            first=True

                            for item in vendorfileobj.filename_info.keys():
                                if item=="Vendor":
                                    #--------------------
                                    guess_val = dpg.get_value(vendorfileobj.filename+'_vend').upper()
                                    # Formats common, problematic titles 
                                    guess_val = guess_val_helper(guess_val)
                                    #--------------------
                                    if len(guess_val)!=0:   num_helper  =   int((len(guess_val)/2)+1)
                                    else:                   num_helper  =   1
                                    #--------------------
                                    # Sets list of vendor names to be only that which starts with what's written in the input text.
                                    # The callback duplicates this functionality
                                    temp_vendor_names=[i for i in vendor_names if i.startswith(guess_val[0:num_helper])]
                                    #--------------------
                                    try:        dpg.add_combo(items=temp_vendor_names,id=vendorfileobj.filename+'_combo',default_value=temp_vendor_names[0], width=150)
                                    except:     dpg.add_combo(items=temp_vendor_names,id=vendorfileobj.filename+'_combo',default_value=guess_val, width=150)
                                    #--------------------
                                elif item=="Notes":
                                    try:
                                        dpg.add_text(vendor_codes[dpg.get_value(vendorfileobj.filename+'_combo')],id=vendorfileobj.filename+'_code')
                                    except:
                                        dpg.add_text("No Code Found Yet",id=vendorfileobj.filename+'_code')
                                    #--------------------
                                elif item=="Dept.":
                                    
                                    dptGroup = dpg.add_group(horizontal = True)

                                    dpg.add_combo(items=taxDict.keys(),id=vendorfileobj.filename+'_tax',width=40,default_value=taxDict.keys()[0],parent=dptGroup)
                                    #dpg.add_same_line(spacing=5)
                                    dpg.add_text(taxDict.keys()[0], id=vendorfileobj.filename+'_taxinfo',parent=dptGroup)
                                    #--------------------
                                else:

                                    #dpg.add_text('')
                                    '''
                                    if first:

                                        dpg.add_same_line(spacing=50)

                                        #test_name = vendorfileobj.filename+'_qtyDivide'
                                        #print ("TEST!!!!!:\t"+test_name)
                                        #dpg.add_combo(items=['Divide Evenly','Copy Quantities'],default_value="~",id=vendorfileobj.filename+'_qtyDivide',label="StoreQtys?",show=False)
                                        #dpg.add_button(id='HELP')
                                        first=False
                                    else:
                                        dpg.add_text('')'''
                                    #--------------------
                                dpg.add_table_next_column()

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

        dpg.configure_item("outputFileName",default_value=saveStr)
        #dpg.add_text("<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>")
        dpg.set_item_callback("process_button",processing_helper)
        today = date.today()
        dpg.set_item_user_data("process_button",[list_of_vendorfile_objs,pathing_dict,today,annotations])
     

def beginScan(sender, app_data, user_data):
    #====================================================
    pathingDict         =   formatPathingDict()
    fileContentsDict    =   scanInputs()
    #====================================================
    manualInput(fileContentsDict,pathingDict,"multiple")

#====================================================

def display_indiv_fileSelector():
    pass

def display_group_import():
    pass

def display_pdf_transformer():
    pass

def display_duplicate_cleaner():
    pass

def defaultFolderSelect():
    pass

def saveDefault():
    pass

def main():

    try:
        parent_folder=get_default_dir();
    except:
        parent_folder="<no_directory_selected>"

    with dpg.window(tag="Primary Window",label="Import Inventory JFGC",width=620,height=400):
        
        from DPG_Themes import global_theme
        dpg.bind_theme(global_theme)
  
        # /////////////////////////////////
        #===================================================
        with dpg.tab_bar():
            with dpg.tab(label="Process Files"):
                #[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
                with dpg.child_window(width=600,height=80):
                    dpg.add_text("Welcome to JFGC Import Inventory Helper.\nBegin by selecting a single file, or a folder of files.")
                    dpg.add_text("Files must be of format:\n\t[vendorname]-[tags]-[department #].[extension]")
                #[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
                dpg.add_button(label="Process Individual File",     width=300,  callback=display_indiv_fileSelector,    user_data=parent_folder)
                dpg.add_button(label="Process Multiple Files",      width=300,  callback=display_group_import,          user_data=parent_folder)
                dpg.add_button(label="Convert PDF to CSV",          width=300,  callback=display_pdf_transformer,       user_data=parent_folder)
                dpg.add_button(label="Combine Duplicate Entries",   width=300,  callback=display_duplicate_cleaner,     user_data=parent_folder)
                #-----------------------------------------------
            with dpg.tab(label="Default Directories",tag='dd'):
                #[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
                with dpg.child_window(width=600,height=55):
                    dpg.add_text("When selecting a folder, make sure \\Rubric is present and that it contains a valid formatting rubric.")
                    dpg.add_text("All other directories will be auto-created.")
                #[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
                with dpg.child_window(width=600,height=130):
                    #add_input_text(tag='rubric_filename',label="Rubric",default_value="~No File Selected~",enabled=False,width=500)
                    dpg.add_input_text(tag='base_parent_directory',   enabled=False,default_value =   parent_folder               ,label="Parent Directory")
                    dpg.add_input_text(tag='base_input_path',         enabled=False,default_value =   parent_folder+"\\INPUT"     ,label="Input Path")
                    dpg.add_input_text(tag='base_output_path',        enabled=False,default_value =   parent_folder+"\\OUTPUT"    ,label="Output Path")
                    dpg.add_input_text(tag='base_processed_path',     enabled=False,default_value =   parent_folder+"\\PROCESSED" ,label="Processed Path")
                    dpg.add_input_text(tag='base_rubric_path',        enabled=False,default_value =   parent_folder+"\\Rubric"    ,label="Rubric Path")
                #[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
                dpg.add_button(tag='base_select',label="Select Default Directory",callback=defaultFolderSelect)
                dpg.add_button(tag='save_base_selection',label="Save Information?",show=False,callback=saveDefault)
                dpg.add_text(tag='saved_notify',show=False,default_value="Saved!")
                #-----------------------------------------------
            with dpg.tab(label="Utilities"):
                #[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
                Utilities.Markup(width=400,height=120)
                Utilities.PrcBreakdown(width=400,height=150)
            #-----------------------------------------------

    #===================================================
    return

if __name__=="__main__":

    dpg.create_context()
    dpg.create_viewport(title='JFGC Import Inventory Assistant', width=800, height=500)
    dpg.setup_dearpygui()

    main()
    
    dpg.show_viewport()
    dpg.set_primary_window("Primary Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()

 
