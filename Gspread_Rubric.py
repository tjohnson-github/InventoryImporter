

import pickle
import gspread
from google.oauth2.service_account import Credentials
from Gspread_Auth import auth_gspread
from decimal import *

def add_rubric(name,subname,values):
    #============================================================
    # Select Worksheet
    gc  =   auth_gspread()
    sh  =   gc.open("JFGC Formatting Rubrics")
    wk  =   sh.sheet1
    #============================================================
    # Get All Values in first column
    names_list = wk.col_values(1)
    #=============================================== =============
    # Determine where my rubric stops
    if ('END' in names_list):
        last_cell = names_list.index("END")+1
    #============================================================
    # Format Name_Subname pairs from first column
    temp_name_pairs=[]
    for i,temp_name in enumerate(names_list):

        if temp_name=='END': break

        if (i+1)%2==1:

            if names_list[i+1]!='':
                temp_pair = f"{names_list[i]}_{names_list[i+1]}"
            else:
                temp_pair = f"{names_list[i]}"

            temp_name_pairs.append(temp_pair)
        else: continue
    #============================================================
    # Format name and subname
    if subname!='':
        name_to_add = f"{name}_{subname}"
    else:
        name_to_add = name
    #============================================================
    # Check to make sure the name_subname to add has no values that will break my rubric
    if ('END' == name_to_add) or ('end' == name_to_add):
        return False,"Rubric name and subname cannot contain the word 'END'"
    if ('RUBRIC' == name_to_add) or ('rubric' == name_to_add):
        return False,"Rubric name and subname cannot contain the word 'RUBRIC'"
    #============================================================
    # Print rubric values into cells
    if name_to_add not in temp_name_pairs:

        temp_row_A = [name]
        temp_row_B = [subname]

        for key,val in values.items():
            temp_row_A.append(key)
            temp_row_B.append(val)

        # Add a stopper so my old read function knows when to stop reading
        temp_row_A.append("STOP")

        # Print first of two rows
        for i,item in enumerate(temp_row_A):
            #if i+1!=38:
            wk.update_cell(last_cell,i+1,item)

        last_cell+=1

        # Print second of two rows
        for i,item in enumerate(temp_row_B):
            #if i+1!=38:
            wk.update_cell(last_cell,i+1,item)

        last_cell+=1

        wk.update_cell(last_cell,1,'END')

        return True,f"{name}_{subname} successfully added to rubric!"

    else:
        return False,f"{name}_{subname} already exists in rubric! Cannot save!"
    

def read_formatting_gsheet(gsheetName="JFGC Formatting Rubrics"):
    #import gspread
    #from Gspread_Rubric import authGspread
    gc =  auth_gspread()
    sh =  gc.open(gsheetName)
    wk =  sh.sheet1
    #=======================
    vendor_names    =   []     
    vendor_tags     =   []      
    vendor_dicts    =   []   
    #--------
    rubric_names    =   []
    #rubric_headers  =   []
    rubric_dicts    =   []
    #--------
    header_present  =   False
    values_present  =   False
    #--------
    unformatted_headers =   {}
    vendor_tag_dict     =   {}
    #--------
    row_count       =   1
    #--------
    #names_list = wk.col_values(1)
    #if ('END' in names_list):
    #    last_cell = names_list.index("END")+1
    

    list_of_lists = wk.get_all_values()



    for row in list_of_lists:
        #=======================
        # Checks that the first row of every set of two corresponds to header names, not order. 
        if row_count % 2 != 0:  is_header=True
        else:                   is_header=False
        #=======================
        # To stop reading the document...
        if row[0] != None:
            if row[0].lower()=='END'.lower(): break
        # remove case sensitivity here ^^^^^^^
        #=======================
        if is_header:
            temp_name=row[0]
            vendor_names.append(temp_name)
        else:         
            #--------------------
            if row[0]=='rubric':  
                is_rubric=True
                rubric_names.append(temp_name)
                vendor_names.remove(temp_name)
            else:                       
                is_rubric=False
                temp_tag=''
                # If the tag location isnt empty, create a new name for that variant
                if row[0]!=None and row[0]!='':
                    variant_format  = vendor_names[vendor_names.index(temp_name)]+"_"+row[0]
                    vendor_names[vendor_names.index(temp_name)]=variant_format
                    temp_name       = variant_format
                    temp_tag        = row[0]
                elif row[0]==None or row[0]=='':
                    variant_format  = vendor_names[vendor_names.index(temp_name)]+"_"
                    vendor_names[vendor_names.index(temp_name)]=variant_format
                    temp_name       = variant_format
                    #temp_tag        = row[0]
                    #temp_tag = ''



                vendor_tags.append(temp_tag)
                vendor_tag_dict.update({temp_name:temp_tag})
            #--------------------
        #=======================
        temp_row=[]
        #=======================
        for index,cell in enumerate(row[1:]):
            #----------------------------
            # If there's no value in the final 
            #if (cell=="STOP" or index+1>=38) and is_header: break
            if cell=="STOP" and is_header: break
            #if index+1==38 and is_header: break
            #if cell.value==None and is_header: continue
            #elif cell.value==None and not is_header: 
            #----------------------------
            #try:

            #while cell.endswith(" "):
            #    cell = str(list(cell[:-1]))
            if cell==None or cell=='':
                temp_row.append(None)
            else:
                temp_row.append(cell)
            #except:
            #    temp_row.append(cell)
            #----------------------------
        #=======================
        # Rows are either headers (made of labels) or values (made of ints)
        # Allows the objects to persist through loops.
        if is_header:
            temp_header =   []
            for column in temp_row:

                temp_column =   column

                if temp_column!=None:
                    while temp_column.endswith(' '):
                        temp_column = str(list(temp_column[:-1]))

                    while temp_column.startswith(' '):
                        temp_column = str(list(temp_column[1:]))

                temp_header.append(temp_column)  

            header_present=True
        else:
            
            unformatted_headers.update({temp_name:temp_header})

            temp_vals=[]
            for x in temp_row:
                try:
                    temp_vals.append(int(x))
                except:
                    temp_vals.append(None)

            values_present=True
        #=======================
        # If a label / value pair has been produced: 
        if header_present and values_present:
            #---------------------
            temp_dict=dict(zip(temp_header, temp_vals))
            #---------------------
            if is_rubric:
                # Value : Header Value is the correct order, as values will be replaced with that value's rubric column name later. 
                temp_dict=dict(zip(temp_vals, temp_header))
                rubric_dicts.append(temp_dict)
            else: #is_vendor
                vendor_dicts.append(temp_dict)
            #---------------------
            # Resets the label/value pair detectors. 
            header_present=False; values_present=False
        #=======================
        row_count+=1

    print('=================================================================')
    #print('=================================================================')
    #for x in vendor_names: print (x)
    print('=================================================================')

    #[][][][][][][][][][][][][][]
    zipped_rubrics=dict(zip(rubric_names, rubric_dicts))
    zipped_vendors=dict(zip(vendor_names, vendor_dicts))
    #[][][][][][][][][][][][][][]
    return zipped_rubrics,zipped_vendors, unformatted_headers, vendor_tag_dict


def updateSheetfromTop(sheetName,entries_to_add):

    # Assumes sheet with correct header is already present:

    gc = auth_gspread()
    sh = gc.open(sheetName)
    wk = sh.sheet1

    current_header  = wk.row_values(1)
    incoming_header = entries_to_add[0]

    # Checks header to make sure they indeed match

    try:
        if current_header==[]:
            print ("SHEET MOST LIKELY EMPTY; CREATING HEADER")
            wk.insert_row(incoming_header,index=1)

        if incoming_header == current_header:
        
            for entry in entries_to_add[1:]:
                wk.insert_row(entry,index=2)

        else:
            print("LOGS BEING SENT TO WRONG FILE!")

    except Exception as e:
        print (f"Cannot Print to {sheetName}:\t{e}")