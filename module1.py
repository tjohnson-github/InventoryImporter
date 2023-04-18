
from dataclasses import dataclass,field

@dataclass
class Rubric:
    name: str
    subname: str
    correspondenceDict: dict

@dataclass
class DesiredFormat:
    name: str
    correspondenceDict: dict

# decouple the editor; 
# learn what you did from DOTMOB whereby each dataclass is responsible for its own UI editor



def read_formatting_gsheet(gsheetName="JFGC Formatting Rubrics"):

    import gspread
    from Gspread_Rubric import authGspread
    #=======================
    gc =  authGspread()
    sh =  gc.open(gsheetName)
    wk =  sh.sheet1
    #=======================
    list_of_lists = wk.get_all_values()
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

    for row in list_of_lists:
        #=======================
        is_header = True if row_count %2!=0 else False
        #=======================
        # To stop reading the document...
        if row[0] != None:
            if row[0].lower()=='END': break
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


def main():
    a = Rubric('test','b',{"a":5})
    print (a)

if __name__=="__main__":
    main()