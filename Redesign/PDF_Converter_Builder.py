

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
