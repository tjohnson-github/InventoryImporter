

import dearpygui.dearpygui as dpg

#from JFGC_Data import dept_comb
import Utilities

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

 
