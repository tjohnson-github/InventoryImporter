

import dearpygui.dearpygui as dpg
import os
import pickle
import fnmatch
#from JFGC_Data import dept_comb

import Utilities
import Gspread_Rubric
from Vendorfile import vendorfile

import JFGC_Data
JFGC = JFGC_Data.jfgcdata#JFGC_Data.JFGC_Data()

import Importer
import PDF_Scraper
import File_Operations
import WIX_Utilities
import SQL_Scraper
import Auto_Assigner

from Single_Product_Multiple_Rows_Transformer import display_single_product_multiple_rows_transformer 

#====================================================
#================== HELPER FUNCTIONS

def formatPathingDict(input_type):
    # If the default is selected, uses default for all entries
    # If custom is selected, uses default for all entries EXCEPT the custom input folder to scan.
    #print (f"Userdata:\t{user_data}")
    #====================================================
    pathingDict: dict = {}
    pathingDict['parent_path']          =   dpg.get_value('base_parent_directory')+ "\\"
    pathingDict['staged_filepath']       =   dpg.get_value('base_staged_path')+ "\\"
    pathingDict['ouput_filepath']       =   dpg.get_value('base_output_path')+ "\\"
    pathingDict['processed_filepath']       =   dpg.get_value('base_processed_path')+ "\\"
    pathingDict['rubric_path']          =   dpg.get_value('base_rubric_path')+ "\\"
    #====================================================
    if input_type=="default":
        pathingDict['input_filepath']   =   dpg.get_value('base_input_path')+ "\\"
    elif input_type=="custom":
        pathingDict['input_filepath']   =   dpg.get_value('input_path')+ "\\"
    #====================================================
    # Final formatting
    print (pathingDict)
    #for key,val in enumerate(pathingDict.items()):
    #    print (key,val)
        #pathingDict[key] = val + "\\"
    #====================================================
    return pathingDict

def manualInput(vendorfileObjList,pathing_dict,step=1,cloudRubric=True):

    if step==1:
        importer = Importer.Importer(JFGC,pathing_dict,cloudRubric)
        importer.importerWindow(vendorfileObjList)
    elif step==2:
        exporter = Importer.StagedProcessor(JFGC,pathing_dict,cloudRubric)
  
def beginMultiStage(sender, app_data, user_data):
    #====================================================
    dpg.configure_item(dpg.get_item_parent(sender),show=False)
    #====================================================
    #print (f"Userdata1:\t{user_data}")
    input_type          =   "default"
    pathingDict         =   formatPathingDict(input_type)
    #====================================================
    # Given a set of filepaths, scan all possible files in the INPUT folder and create the appropriate
    #   UI-based objects which will allow for manual input to more accurately process the vendorfiles.
    #====================================================
    vendorfileObjList    =   []
    #====================================================
    excel_files_to_process  =   fnmatch.filter(os.listdir(pathingDict['input_filepath']), '*.xlsx')
    csv_files_to_process    =   fnmatch.filter(os.listdir(pathingDict['input_filepath']), '*.csv')
    #pdf_files_to_process    =   fnmatch.filter(os.listdir(pathingDict['input_filepath']), '*.pdf') if automatePDF else []
    #====================================================
    print ("=========================================")
    #====================================================
    for file in excel_files_to_process:
        vendorfileObjList.append(vendorfile(pathingDict["input_filepath"]+file))

    for file in csv_files_to_process:
        vendorfileObjList.append(vendorfile(pathingDict["input_filepath"]+file))
    #for file in pdf_files_to_process:
    #    print (f'Cannot convert {file} to CSV in the same step as processing CSVs.\tPDFs too often require manual validation.')
    #====================================================
    manualInput(vendorfileObjList,pathingDict,1,"multiple")

def beginMultiExport(sender, app_data, user_data):
    #====================================================
    dpg.configure_item(dpg.get_item_parent(sender),show=False)
    #====================================================
    #print (f"Userdata1:\t{user_data}")
    input_type          =   "default"
    pathingDict         =   formatPathingDict(input_type)
    #====================================================
    # Given a set of filepaths, scan all possible files in the INPUT folder and create the appropriate
    #   UI-based objects which will allow for manual input to more accurately process the vendorfiles.
    #====================================================
    vendorfileObjList    =   []
    #====================================================
    excel_files_to_process  =   fnmatch.filter(os.listdir(pathingDict['input_filepath']), '*.xlsx')
    #pdf_files_to_process    =   fnmatch.filter(os.listdir(pathingDict['input_filepath']), '*.pdf') if automatePDF else []
    #====================================================
    print ("=========================================")
    #====================================================
    for file in excel_files_to_process:
        vendorfileObjList.append(vendorfile(pathingDict["input_filepath"]+file))
    #====================================================
    manualInput(vendorfileObjList,pathingDict,2,"multiple")

#====================================================
# PDF

def PDFfileSelect(sender, app_data, user_data):
    # PDF File select Dialogue
    #-------------------------------------------
    #dpg.file_dialog(modal=True)
    #-------------------------------------------
    with dpg.file_dialog(modal=True,default_path=user_data,callback=updatePDFSelect,height=400,width=400) as dialog:
        #dpg.add_file_extension(".*", color=(255, 255, 255, 255))
        #dpg.add_file_extension("Source files (*.pdf){.pdf}", color=(0, 255, 255, 255))
        dpg.add_file_extension(".pdf", color=(255, 255, 0, 255), custom_text="PDF")
        #dpg.add_fi
        dpg.set_item_user_data(dialog,dpg.get_item_parent(sender))

def updatePDFSelect(sender, app_data, user_data):
    #import re
    # Given the name of the pdf and its parent folder:
    #   - sets the output path to be the default input for later use 
    #   - sets the processed path to be the default processed path
    # TO DO:
    #   - create some manner of popup which explains if the file was successfully processed and/or successfully moved.
    #====================================================
    #print ("TEST")
    print(dpg.get_file_dialog_info(sender))
    print("\n\n")
    pdf_filename    =   app_data['file_name']
    pdf_parent      =   app_data['current_path']
    senderParent    =   user_data #'pdf_fileSelectorWindow'
    #====================================================
    dpg.configure_item(f'{senderParent}_pdf_filename',default_value=pdf_filename)
    dpg.configure_item(f'{senderParent}_process_PDF',enabled=True)
    dpg.add_input_text(tag=f'{senderParent}_pdf_output_path',parent=senderParent,enabled=False,default_value=dpg.get_value('base_input_path'),label="Output Path")
    dpg.add_input_text(tag=f'{senderParent}_pdf_processed_path',parent=senderParent,enabled=False,default_value=dpg.get_value('base_processed_path'),label="Processed Path")
    dpg.add_text(default_value="Don't be alarmed; converted PDFs output to Default Input\nfor later use during Multiple File Selection.",parent=senderParent)
    dpg.set_item_user_data(f'{senderParent}_process_PDF',pdf_parent)
    #====================================================
    temp_name = pdf_filename[:-4]#re.sub('.pdf', '', pdf_filename)
    dpg.configure_item(f'{senderParent}_pdf_saveAs',enabled=True,default_value=temp_name)

def beginPDF(sender, app_data, user_data):
    # Sets the output of the scrape to be the default input folder.
    # Moves the pdf to the default processed folder.
    transformerWindow = dpg.get_item_parent(sender)
    #====================================================
    output_filepath     = dpg.get_value(f'{transformerWindow}_pdf_output_path')
    processed_path      = dpg.get_value(f'{transformerWindow}_pdf_processed_path')
    file                = dpg.get_value(f'{transformerWindow}_pdf_filename')
    parent              = user_data
    saveAs              = dpg.get_value(f'{transformerWindow}_pdf_saveAs')+'.csv'
    #====================================================
    annotations         = False
    #====================================================
    PDF_Scraper.scrape_pdf(input_path=parent,output_path=output_filepath,filename=file,saveName=saveAs,annotations=annotations)
    PDF_Scraper.scrape_pdf_alt(input_path=parent,output_path=output_filepath,filename=file,saveName=saveAs,annotations=annotations)
    processed_path = processed_path + "\\"
    File_Operations.cleanup(file,parent,processed_path) 

def display_pdf_transformer(sender,app_data,user_data):
    #----------------------------------------
    filepath=user_data
    #----------------------------------------
    with dpg.window(label="PDF Format Selection",width=600,height=250) as transformerWindow:
        dpg.add_button(tag=f'{transformerWindow}_pdf_fileselect',label="Select File",callback=PDFfileSelect,user_data=filepath,width=500)
        dpg.add_input_text(tag=f'{transformerWindow}_pdf_filename',label="Filename",default_value="~No File Selected~",enabled=False,width=500)
        #-----------------
        dpg.add_separator()
        group = dpg.add_group(horizontal=True)
        dpg.add_input_text(tag=f'{transformerWindow}_pdf_saveAs',default_value="~Select file first for auto~",enabled=False,width=450,parent=group)
        #-----------------
        #dpg.add_same_line()
        
        dpg.add_input_text(label="Save as",default_value=".csv",enabled=False,width=50,parent=group)
        #-----------------
        dpg.add_separator()
        #-----------------
        dpg.add_button(tag=f'{transformerWindow}_process_PDF',  width=500,  label="Convert PDF to CSV", callback=beginPDF,enabled=False)
        #dpg.set_item_user_data(f'{transformerWindow}_process_PDF',transformerWindow)
        #dpg.set_item_theme("process_PDF", "disabled_btn")
        #dpg.set_item_disabled_theme('process_PDF','disabled_btn')
        #dpg.bind_theme('process_PDF','disabled_btn')

#====================================================
# MISC

def display_duplicate_cleaner():
    pass

def begin_noUrl_autofill(sender, app_data, user_data):
    
    print("--------------")
    print (sender)
    print("--------------")
    print (app_data)
    print("--------------")
    print (user_data)
    print("--------------")
    WIX_Utilities.noUrl_autofill_main(dpg.get_value('noUrl_filename'),user_data)



def autofuill_noURL_file(sender, app_data, user_data):

    filepath=user_data

    with dpg.window(id='noUrl_fileSelectorWindow',label="WIX-Formatted NO_URL File Selection",width=600,height=150):
        dpg.add_input_text( tag='noUrl_filename',  label="Filename",   default_value="~No File Selected~", enabled=False,  width=500)
        dpg.add_button(     tag='fileselect',label="Select File",callback=noUrl_individFileSelect,         user_data=filepath)

        dpg.add_separator()

        dpg.add_slider_int(tag='noURLCutoff',label="% Fidelity Cutoff",default_value=33)
        dpg.add_button(tag='process_noUrl_autofill',    width=600,  label="Process NO_URL Autofill",enabled=False,callback=begin_noUrl_autofill)
        dpg.bind_item_theme('process_noUrl_autofill','disabled_btn')

def update_noUrl_fileSelect(sender,app_data,user_data):
    print (app_data)
    filename        =   next(iter(app_data['selections']))
    parent_folder   =   app_data['current_path']
    if 'no_url' in filename.lower():
        dpg.configure_item(     'noUrl_filename',default_value = filename)
        dpg.configure_item(     'process_noUrl_autofill',enabled=True)
        dpg.set_item_user_data( 'process_noUrl_autofill',user_data = parent_folder)

def noUrl_individFileSelect(sender, app_data, user_data):
    # Individual File select Dialogue

    #-------------------------------------------
    with dpg.file_dialog(modal=True,default_path=f'{user_data}/OUTPUT', id="file_dialog_id",callback=update_noUrl_fileSelect,width=700,height=500):
        dpg.add_file_extension(".*", color=(255, 255, 255, 255))
        dpg.add_file_extension("Source files (*.xlsx){.xlsx}", color=(0, 255, 255, 255))
        #dpg.add_file_extension(".csv", color=(255, 255, 0, 255), custom_text="CSV")
        dpg.add_file_extension(".xlsx", color=(255, 0, 255, 255), custom_text="Excel")
    #-------------------------------------------
    pass

#====================================================
# Default Folder Manip

def updateFolderSelect(sender, app_data, user_data):
    #====================================================
    foldername  =   app_data['file_path_name']
    #====================================================
    dpg.configure_item('foldername',default_value=foldername)
    dpg.configure_item('input_path',default_value=foldername,label="Input Path")
    dpg.add_text(parent='input_folderWindow',default_value="**Note**: Input path changed; all other paths will remain the default.")
    dpg.add_separator(parent='input_folderWindow')
    dpg.add_button(id='beginScan',width=600,label="Begin Processing Files",callback=beginMultiStage,user_data="custom",enabled=True,parent='input_folderWindow')    

def inputFolderSelect(sender, app_data, user_data):
    # Input Folder select Dialogue
    #-------------------------------------------
    with dpg.file_dialog(modal=True,default_path=user_data, id="folder_dialog_id",callback=updateFolderSelect):
        pass

#====================================================
# INDIVIDUAL FILE MANIP

def getPathingDict():
    pathing_dict:   dict    = {}
    pathing_dict['parent_path']         = get_default_dir() #dpg.get_value('base_parent_directory')
    pathing_dict['staged_filepath']     = dpg.get_value('base_staged_path')
    pathing_dict['ouput_filepath']      = dpg.get_value('base_output_path')
    pathing_dict['processed_filepath']  = dpg.get_value('base_processed_path')
    pathing_dict['rubric_path']         = dpg.get_value('base_rubric_path')
    pathing_dict['input_filepath']      = get_default_dir() #dpg.get_value('base_input_path')
    return pathing_dict



def beginSingleImport(sender, app_data, user_data):
    # Given an individual file, 
    # Parent path and Input path are identical in the case of individual file selection. 
    #====================================================
    filename    =   dpg.get_value('filename')
    parent_path =   user_data+"\\"
    #====================================================
    master_dict:    dict    = {}
    #====================================================
    pathing_dict:   dict    = {}
    pathing_dict['parent_path']     = user_data #dpg.get_value('base_parent_directory')
    pathing_dict['staged_filepath']  = dpg.get_value('base_staged_path')
    pathing_dict['ouput_filepath']  = dpg.get_value('base_output_path')
    pathing_dict['processed_filepath']  = dpg.get_value('base_processed_path')
    pathing_dict['rubric_path']     = dpg.get_value('base_rubric_path')
    pathing_dict['input_filepath']  = user_data #dpg.get_value('base_input_path')
    #====================================================
    vendorfileObjList=[vendorfile(parent_path+filename)]
    #====================================================
    manualInput(vendorfileObjList,pathing_dict,"individual")
    # NEXT THING:::: MAKING SURE THAT A FILE's FORMATTING DICT IS APPLIED ON CHECK, NOT DURING...
    # MUST APPLY THAT DICT TO THE VENDORFILE OBJ SO IT CAN BE EASILY REFERENCED LATER

def updateFileSelect(sender, app_data, user_data):          
    # After an individual file has been selected for some sort of processing,
    # Enable/Disable the correct buttons based on what the filetype can be used for.
    # TO DO:
    #   - make sure the disabled buttons are colored correctly.
    #====================================================
    filename        =   app_data['file_name_buffer']
    parent_folder   =   app_data['current_path']
    #====================================================
    dpg.configure_item('filename',default_value=filename)
    #====================================================
    #====================================================
    if 'wix' in filename.lower():
       dpg.configure_item(      'process_WIX-to-site',enabled=True)
       dpg.set_item_user_data(  'process_WIX-to-site',user_data=parent_folder)

    elif 'full' in filename.lower():
        dpg.configure_item(     'process_master-to-WIX',enabled=True)
        dpg.set_item_user_data( 'process_master-to-WIX',user_data = parent_folder)

    elif 'partial' in filename.lower():
        with dpg.window(popup=True):
            dpg.add_text(       "Partial Files cannot be coverted into WIX")

    else:   # 'inventory' in filename.lower():
        dpg.configure_item(     'process_import-to-master',enabled=True)
        dpg.set_item_user_data( 'process_import-to-master',user_data=parent_folder)

def individFileSelect(sender, app_data, user_data):
    # Individual File select Dialogue
    #-------------------------------------------
    with dpg.file_dialog(modal=True,default_path=user_data, id="file_dialog_id",callback=updateFileSelect,width=700):
        dpg.add_file_extension(".*", color=(255, 255, 255, 255))
        dpg.add_file_extension("Source files (*.csv *.xlsx){.csv,.xlsx}", color=(0, 255, 255, 255))
        dpg.add_file_extension(".csv", color=(255, 255, 0, 255), custom_text="CSV")
        dpg.add_file_extension(".xlsx", color=(255, 0, 255, 255), custom_text="Excel")
    #-------------------------------------------
    pass

def display_indiv_fileSelector(sender, app_data, user_data):
    # File selection windoe for individual files.
    # TO DO:
    #   - buttons should be colored correctly when disabled.
    #====================================================
    filepath=user_data
    #====================================================
    with dpg.window(id='fileSelectorWindow',label="Single File Selection",width=600,height=150):
        dpg.add_input_text( id='filename',  label="Filename",   default_value="~No File Selected~", enabled=False,  width=500)
        dpg.add_button(     id='fileselect',label="Select File",callback=individFileSelect,         user_data=filepath)
        #----------------------------------------
        dpg.add_separator()
        #----------------------------------------
        dpg.add_button(id='process_import-to-master',    width=600,  label="Convert Import to Master_inv",       enabled=False,callback=beginSingleImport)
        dpg.add_button(id='process_master-to-WIX',       width=600,  label="Convert Master_inv to WIX format",   enabled=False,callback=beginIndivMasterWix)
        dpg.add_button(id='process_WIX-to-site',         width=600,  label="Upload WIX to website.",             enabled=False,callback=beginIndivWIX)
        #----------------------------------------
        dpg.set_item_disabled_theme('process_import-to-master','disabled_btn')
        dpg.set_item_disabled_theme('process_master-to-WIX','disabled_btn')
        dpg.set_item_disabled_theme('process_WIX-to-site','disabled_btn')

#====================================================
# INDIVIDUAL FILE MANIP

def display_group_import(sender, app_data, user_data):
    # Folder selection window for group imports.
    # Default information is used unless a custom (and temporary) input folder is given.
    #====================================================
    filepath=user_data[0]
    step = user_data[1]

    specific_stage_import_fn = beginMultiStage if step==1 else beginMultiExport
    #print(specific_stage_import_fn)
    #====================================================
    try:
        dpg.delete_item(f'input_folderWindow')
        #dpg.configure_item(f'input_folderWindow',show=False)
    except Exception as e:
        print(f"Cannot delete inputfolder:\t{e}")
    #====================================================

    with dpg.window(tag=f'input_folderWindow',label="Group Import Selection",width=600,height=350):
        #----------------------------------------
        dpg.add_button(tag='defaultselect',label="Use Default Input path?",width=590,callback=specific_stage_import_fn,user_data="default")
        dpg.add_separator()
        dpg.add_text("\t\t\t\tOR")
        dpg.add_separator()
        dpg.add_button(tag='folderselect',label="Select New Temporary Input Folder",width=590,callback=inputFolderSelect,user_data=filepath)
        #----------------------------------------
        dpg.add_input_text(tag='foldername',label="Input Folder Name",default_value="~No Folder Selected~",enabled=False,width=500)
        dpg.add_separator()
        #----------------------------------------
        dpg.add_input_text(tag='parent_directory',   parent='input_folderWindow',enabled=False,default_value =   filepath               ,label="Parent Directory")
        dpg.add_input_text(tag='input_path',         parent='input_folderWindow',enabled=False,default_value =   filepath+"\\INPUT"     ,label="Input Path")
        dpg.add_input_text(tag='staged_path',        parent='input_folderWindow',enabled=False,default_value =   filepath+"\\STAGED"    ,label="Staged Path")
        dpg.add_input_text(tag='output_path',        parent='input_folderWindow',enabled=False,default_value =   filepath+"\\OUTPUT"    ,label="Output Path")
        dpg.add_input_text(tag='processed_path',     parent='input_folderWindow',enabled=False,default_value =   filepath+"\\PROCESSED" ,label="Processed Path")
        dpg.add_input_text(tag='rubric_path',        parent='input_folderWindow',enabled=False,default_value =   filepath+"\\Rubric"    ,label="Rubric Path")
         
def updateDefaultSelect(sender, app_data, user_data):
    # Given the general filepath, sets the default items to be whats expected.
    # TO DO:
    #       If these files dont actually exist, create them.
    #====================================================
    foldername=app_data['file_path_name']
    #====================================================
    dpg.configure_item('base_parent_directory',default_value =   foldername                  )
    dpg.configure_item('base_input_path',      default_value =   foldername+"\\INPUT"        )
    dpg.configure_item('base_staged_path',      default_value =   foldername+"\\STAGED"        )
    dpg.configure_item('base_output_path',     default_value =   foldername+"\\OUTPUT"       )
    dpg.configure_item('base_processed_path',  default_value =   foldername+"\\PROCESSED"    )
    dpg.configure_item('base_rubric_path',     default_value =   foldername+"\\Rubric"       )
    #====================================================
    dpg.configure_item('save_base_selection',   show=True)

def defaultFolderSelect(sender, app_data, user_data):
    # Default Folder select Dialogue
    #-------------------------------------------
    with dpg.file_dialog(
        modal           =   True,
        default_path    =   user_data, 
        id              =   "default_dialog_id",
        directory_selector = True,
        height          =   400,
        width           =   600,
        callback        =   updateDefaultSelect):
        pass

def get_default_dir(outfile=".\\Data\\default_dir.txt"):
    if not os.path.exists(".\\Data\\default_dir.txt"):
        return os.path.join(os.path.expanduser('~'), 'VENDOR_FILES')
    #--------------
    last_processed = pickle.load(open(outfile,'rb'))
    #--------------
    return last_processed

def set_default_dir(data,outfile=".\\Data\\default_dir.txt",):
    if not os.path.exists(".\\Data"): os.mkdir(".\\Data")
    #--------------
    pickle.dump(data,open(outfile,'wb'))

def saveDefault(sender,app_data,user_data):

    parent      = dpg.get_value('base_parent_directory')
    dpg.configure_item('saved_notify',show=True)

    i = dpg.get_value('base_input_path')
    s = dpg.get_value('base_staged_path')
    o = dpg.get_value('base_output_path')
    p = dpg.get_value('base_processed_path')
    r = dpg.get_value('base_rubric_path')

    if not os.path.exists(i):
        dpg.add_text(parent='dd',default_value='--> Created Input folder; Add files here.')
        os.mkdir(i)
    if not os.path.exists(i):
        dpg.add_text(parent='dd',default_value='--> Created Staged folder; Check files here before final formatting as processes can directly upload if allowed.')
        os.mkdir(s)    
    if not os.path.exists(o):
        dpg.add_text(parent='dd',default_value='--> Created Output folder; This is what you want.')
        os.mkdir(o)
    if not os.path.exists(p):
        dpg.add_text(parent='dd',default_value='--> Created Processed folder; input and staged files that have been used.')
        os.mkdir(p)
    if not os.path.exists(r):
        dpg.add_text(parent='dd',default_value='--> Created Rubric folder; add rubric here.')
        os.mkdir(r)

    set_default_dir(data=parent)

def main():

    try:
        parent_folder=get_default_dir();
    except:
        parent_folder="<no_directory_selected>"

    with dpg.window(tag="Primary Window",label="Import Inventory JFGC",width=650,height=400):
       
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
                dpg.add_text("Input -> Stage -> Process")
                
                before_dist_step_group = dpg.add_group(horizontal=True)
                dpg.add_spacer(width=50,parent=before_dist_step_group)
                dpg.add_button(label="Transform Spreadsheet With Multiple Rows for Each Product",          
                               width        =   500,  
                               callback     =   display_single_product_multiple_rows_transformer,       
                               user_data    =   parent_folder,
                               parent       =   before_dist_step_group)
                
                first_step_group = dpg.add_group(horizontal=True)
                '''dpg.add_button(label="Stage Individual File",     
                               width        =   300,  
                               callback     =   display_indiv_fileSelector,    
                               user_data    =   [parent_folder,],
                               parent       =   first_step_group)
                dpg.add_button(label="Process Individual File",     
                               width        =   300,  
                               callback     =   display_indiv_fileSelector,    
                               user_data    =   [parent_folder,],
                               parent       =   first_step_group)'''

                second_step_group = dpg.add_group(horizontal=True)
                dpg.add_button(label="Stage Multiple Files",      
                               width        =   300,  
                               callback     =   display_group_import,          
                               user_data    =   [parent_folder,1],
                               parent       =   second_step_group)
                dpg.add_button(label="Process Multiple Files",      
                               width        =   300,  
                               callback     =   display_group_import,          
                               user_data    =   [parent_folder,2],
                               parent       =   second_step_group)

                third_step_group = dpg.add_group(horizontal=True)
                dpg.add_spacer(width=150,parent=third_step_group)
                dpg.add_button(label="Convert PDF to CSV",          
                               width        =   300,  
                               callback     =   display_pdf_transformer,       
                               user_data    =   parent_folder,
                               parent       =   third_step_group)
                
                fourth_step_group = dpg.add_group(horizontal=True)
                dpg.add_spacer(width=150,parent=fourth_step_group)
                dpg.add_button(label="Combine Duplicate Entries",   
                               width        =   300,  
                               callback     =   display_duplicate_cleaner,     
                               user_data    =   parent_folder,
                               parent       =   fourth_step_group)
                fifth_step_group = dpg.add_group(horizontal=True)
                dpg.add_spacer(width=150,parent=fifth_step_group)
                dpg.add_button(label="Autofill an NO_URL File",   
                               width        =   300,  
                               callback     =   autofuill_noURL_file,     
                               user_data    =   parent_folder,
                               parent       =   fifth_step_group)
                #-----------------------------------------------
            with dpg.tab(label="Default Directories",tag='dd'):
                #[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
                with dpg.child_window(width=600,height=55):
                    dpg.add_text("When selecting a folder, make sure \\Rubric is present and that it contains a valid formatting rubric.")
                    dpg.add_text("All other directories will be auto-created.")
                #[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
                with dpg.child_window(width=600,height=170):
                    #add_input_text(tag='rubric_filename',label="Rubric",default_value="~No File Selected~",enabled=False,width=500)
                    dpg.add_input_text(tag='base_parent_directory',   enabled=False,default_value =   parent_folder               ,label="Parent Directory")
                    dpg.add_input_text(tag='base_input_path',         enabled=False,default_value =   parent_folder+"\\INPUT"     ,label="Input Path")
                    dpg.add_input_text(tag='base_staged_path',        enabled=False,default_value =   parent_folder+"\\STAGED"    ,label="Staged Path")
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
                Utilities.Markup(width=400,height=120,visualize=True)
                Utilities.PrcBreakdown(width=400,height=150)
            #-----------------------------------------------
            #with dpg.tab(label="SQL Scraper"):
                #SQL_Scraper.SQLScraper(width=650-10,height=400-10,pathingDict=getPathingDict())
            with dpg.tab(label="UPC Auto-Assigner"):
                Auto_Assigner.AutoAssignerTab(width=650-10,height=400-10)
    #===================================================
    pass
    
    print("----------------------------------------------")
    print("MAKE SURE THESE ARE THE FOLDERS YOURE USING:::")
    for key,val in getPathingDict().items():
        print(f'{key}\t:\t{val}')

    print("----------------------------------------------")
    #Importer.populateReceivings(getPathingDict())

    return


def customZip():

    import File_Operations

    # did this for some lake valley bullshit
    f1 = File_Operations.excel_to_list("C:\\Users\\Andrew\\source\\repos\\VENDOR_FILES\\INPUT\\ALT_3_Lak_OrderConfirmation380441_JOHNSON'S FLORIST & GARDEN JOH772C_11.xlsx")
    f2 = File_Operations.excel_to_list("C:\\Users\\Andrew\\source\\repos\\VENDOR_FILES\\INPUT\\Johnsons Florist Olney UPC.xlsx")

    print (f1[0][0])
    print (f2[0][0])

    f1_upc_loc = f1[0][0].index("UPC")
    f2_upc_loc = f2[0][0].index("UPC")
    f2_retail_loc = f2[0][0].index("Retail")

    temp_list =[]

    for f1row in f1[0][1:]:

        temp_row = []
        temp_row.append(f1row[f1_upc_loc])

        for f2row in f2[0][1:]:
            if f1row[f1_upc_loc] == f2row[f2_upc_loc]:
                temp_row.append(f2row[f2_retail_loc])

        temp_list.append(temp_row)

    File_Operations.list_to_excel(temp_list,"C:\\Users\\Andrew\\source\\repos\\VENDOR_FILES\\INPUT\\zipped.xlsx")
    



if __name__=="__main__":


    

    dpg.create_context()
    dpg.create_viewport(title='JFGC Import Inventory Assistant', width=900, height=700)
    dpg.setup_dearpygui()

    main()
    
    dpg.show_viewport()
    dpg.set_primary_window("Primary Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()

  
class ImporterHome:
    tag = "Importer Home"

    def __init__(self,width=650,height=400):
        try:
            parent_folder=get_default_dir();
        except:
            parent_folder="<no_directory_selected>"

        with dpg.window(tag=self.tag,label="Import Inventory JFGC",width=width,height=height):
        
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
                    dpg.add_text("Input -> Stage -> Process")
                    first_step_group = dpg.add_group(horizontal=True)
                    '''dpg.add_button(label="Stage Individual File",     
                                   width        =   300,  
                                   callback     =   display_indiv_fileSelector,    
                                   user_data    =   [parent_folder,],
                                   parent       =   first_step_group)
                    dpg.add_button(label="Process Individual File",     
                                   width        =   300,  
                                   callback     =   display_indiv_fileSelector,    
                                   user_data    =   [parent_folder,],
                                   parent       =   first_step_group)'''

                    second_step_group = dpg.add_group(horizontal=True)
                    dpg.add_button(label="Stage Multiple Files",      
                                   width        =   300,  
                                   callback     =   display_group_import,          
                                   user_data    =   [parent_folder,1],
                                   parent       =   second_step_group)
                    dpg.add_button(label="Process Multiple Files",      
                                   width        =   300,  
                                   callback     =   display_group_import,          
                                   user_data    =   [parent_folder,2],
                                   parent       =   second_step_group)

                    third_step_group = dpg.add_group(horizontal=True)
                    dpg.add_spacer(width=150,parent=third_step_group)
                    dpg.add_button(label="Convert PDF to CSV",          
                                   width        =   300,  
                                   callback     =   display_pdf_transformer,       
                                   user_data    =   parent_folder,
                                   parent       =   third_step_group)
                
                    fourth_step_group = dpg.add_group(horizontal=True)
                    dpg.add_spacer(width=150,parent=fourth_step_group)
                    dpg.add_button(label="Combine Duplicate Entries",   
                                   width        =   300,  
                                   callback     =   display_duplicate_cleaner,     
                                   user_data    =   parent_folder,
                                   parent       =   fourth_step_group)
                    fifth_step_group = dpg.add_group(horizontal=True)
                    dpg.add_spacer(width=150,parent=fifth_step_group)
                    dpg.add_button(label="Autofill an NO_URL File",   
                                   width        =   300,  
                                   callback     =   autofuill_noURL_file,     
                                   user_data    =   parent_folder,
                                   parent       =   fifth_step_group)
                    #-----------------------------------------------
                with dpg.tab(label="Default Directories",tag='dd'):
                    #[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
                    with dpg.child_window(width=600,height=55):
                        dpg.add_text("When selecting a folder, make sure \\Rubric is present and that it contains a valid formatting rubric.")
                        dpg.add_text("All other directories will be auto-created.")
                    #[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[
                    with dpg.child_window(width=600,height=170):
                        #add_input_text(tag='rubric_filename',label="Rubric",default_value="~No File Selected~",enabled=False,width=500)
                        dpg.add_input_text(tag='base_parent_directory',   enabled=False,default_value =   parent_folder               ,label="Parent Directory")
                        dpg.add_input_text(tag='base_input_path',         enabled=False,default_value =   parent_folder+"\\INPUT"     ,label="Input Path")
                        dpg.add_input_text(tag='base_staged_path',        enabled=False,default_value =   parent_folder+"\\STAGED"    ,label="Staged Path")
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
                    Utilities.Markup(width=400,height=120,visualize=True)
                    Utilities.PrcBreakdown(width=400,height=150)
