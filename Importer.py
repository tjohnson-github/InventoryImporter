from Vendorfile import vendorfile
import Gspread_Rubric
import dearpygui.dearpygui as dpg
from typing import List
import datetime,os
from datetime import date

import Gspread_WIX 
import Auto_Assigner
import UPC_Lookup
import WIX_Utilities
import Utilities

import File_Operations

class StagedProcessor:
    __count=0
    
    def __init__(self):
        
        #stagedFiles = self.scan_staged()
        stagedFiles=[1,1,1,1,1]

        with dpg.window(label="Staged File Manager",tag=f'stagedManager_{self.__count}',width=830,height=(300+(115*int(len(stagedFiles))))):

            dpg.add_checkbox(tag="process_wix",label="Process files into WIX format?",default_value=True),
            dpg.add_checkbox(tag="auto_wix",label="Automatically update website?",default_value=False)
            dpg.add_checkbox(tag="combine_files",label="Combine files into one Counterpoint8?",default_value=True,callback=self.showOptions)
            dpg.add_combo(tag='combine_files_options',label="Reorganize by:",items=["Original File","Department","Vendor","Ticket"],show=False)

        self.__count+=1
        print(self.__count)

    def scan_staged(self,pathing_dict):
        #self.input_filepath = pathing_dict['input_filepath']+'\\'
        self.staged_filepath= pathing_dict['staged_filepath']
        self.ouput_filepath = pathing_dict['ouput_filepath']
        #self.ouput_filepath = pathing_dict['staged_filepath']+'\\History\\'
        self.processed_filepath = pathing_dict['processed_filepath']+'fromStaged\\'

        #if not os.path.exists(self.staged_ouput_filepath): os.mkdir(self.staged_ouput_filepath)
        if not os.path.exists(self.processed_filepath): os.mkdir(self.processed_filepath)

        excel_files_to_process  =   fnmatch.filter(os.listdir(self.staged_filepath), '*.xlsx')

    def showOptions(self,sender):

        print(sender)

        if dpg.get_value(sender)==False:
            dpg.configure_item('combine_files_options',show=True)
        else:             
            dpg.configure_item('combine_files_options',show=False)

    def formatFiles(self):
        #==================================================
        # Create wix_format from the XLSX with the full header, as it is the one with possible URLs in the body.
        savefiles       =   dpg.get_value("process_wix")
        update_website  =   dpg.get_value("auto_wix")
        #==================================================
        if savefiles==True or update_website==True :

            all_with            =   []
            all_without         =   []
            recently_added_skus =   []
            header              =   []

            for file in saved_filenames:
                if 'Full' in file:
                    #log.append( " --> Generating WIX formats now.\n")
                    print(f" --> Generating WIX formats now for {file}:\n")
                    #==================================================
                    withUrl,withoutUrl=WIX_Utilities.generate_wix_files_from_xlsx(file,ouput_filepath)
                    #==================================================
                    #write both files
                    if savefiles==True:
                        File_Operations.list_to_excel(withUrl,     ouput_filepath+file+'-wix-URL.xlsx')
                        File_Operations.list_to_excel(withoutUrl,  ouput_filepath+file+'-wix-NO_URL.xlsx')
                        Gspread_WIX.createSheetAndPopulate(ouput_filepath+file+'-wix-NO_URL.xlsx',withoutUrl,folderID="1OLYcoDQ6E6tihDngWIInv3h6MMXzKQFi")
                    #==================================================
                    #updates website
                    if update_website==True:
                        header = withUrl[0]

                        for entry in withUrl[1:]:

                            if entry[header.index('handleId')] not in recently_added_skus:
                                all_with.append(entry)
                                recently_added_skus.append(entry[header.index('handleId')])

                        for entry in withoutUrl[1:]:

                            if entry[header.index('handleId')] not in recently_added_skus:
                                all_without.append(entry)
                                recently_added_skus.append(entry[header.index('handleId')])
                        #Wix_Utilities.autoupdateWebsite(withUrl,withoutUrl)
                    #==================================================
            if update_website==True:
                print ("Beginning website Auto-Update")
                WIX_Utilities.autoupdateWebsite(header,all_with,all_without)

    def processbyWIXRubric():
        pass

class InputProcessor:
    vendorfileobj_list          : List[vendorfile]
    final_KENS_output_array     : List[any]=[]
    final_OLNEY_output_array    : List[any]=[]
    final_BOTH_output_array     : List[any]=[]

    
    def __init__(self,JFGC,list_to_process,pathing_dict):
        print ("=========================================")
        print ("============PROCESSING INPUTS============")            
        print ("=========================================")
        self.rubrics  ,  self.vends  ,  self.all_headers  ,  self.tags =Gspread_Rubric.read_formatting_gsheet()

        self.input_filepath = pathing_dict['input_filepath']
        self.staged_filepath= pathing_dict['staged_filepath']
        #self.ouput_filepath = pathing_dict['ouput_filepath']+'\\'
        self.processed_filepath = pathing_dict['processed_filepath']+'fromInput\\'
        
        if not os.path.exists(self.processed_filepath): os.mkdir(self.processed_filepath)

        self.talk_to_wix = dpg.get_value(item="talk_to_wix")
        self.vendorfileobj_list = list_to_process
        self.temp_AA=[]
        self.JFGC = JFGC
        # Instead of doing both, we print ONE FULL
        # and then after a final check period; (with a refresh button to validate that files have been checked)
        #   (can also start program from this check period which looks at special folder that has all FULLs)
        # give the option to format into:
        #   partial.csv (no edits necessary now; and full acts as record
        #   wix found
        #   wix missing

        self.processbyRubric(self.rubrics["SQL Full"])
        self.saveFilesToStaged(self.rubrics["SQL Full"],"SQL Full")
        
    def processbyRubric(self,rubric,annotations=True):

        output_order        = self.reorder_rubric_dict(rubric)
        print(output_order)
        #===========================================
        final_KENS_output_array     = [output_order]
        final_OLNEY_output_array    = [output_order]
        final_BOTH_output_array     = [output_order]
        #===========================================
        self.formatted_count =   1 # counts how many files have so far been processed... mostly for print()
        self.AA_count        =   0 # counts how many auto assigned UPCs have been requested
        # temp_AA and AA_count were on different levels before so that subsequent rubric marching would not request doubles and instead use the old.
        #===========================================
        for file in self.vendorfileobj_list:
            #-----------------------------------
            if annotations:
                print ("=========================================")
                print ("\t\t\t\tNEW VENDOR\t\t\t\t\t\t")
                print (file)
                print ('\n')
                print ("______________________")
            #-----------------------------------
            vendor              =   file.formatting_dict_name
            vendor_format_dict  =   file.formatting_dict
            #-----------------------------------
            if vendor==None:  
                #--------------------
                #log.append( "\t"+str(file.name)+" has no matching vendor_format in the rubric. Skipping...\n\n")
                print ("\t"+str(file.name)+" has no matching vendor_format in the rubric. Skipping...\n\n")
                dpg.configure_item(file.name+'_error',default_value= f'{file.name} has no matching vendor_format in the rubric. Skipping...\n{str(file.header)}',show=True)
                continue           
                #--------------------
            if annotations:
                print ( "\t"+str(file.name)+" is to be formatted with "+str(vendor)+"\n")
            #--------------------
            header  = file.header
            rows    = file.rows
            #--------------------
            # Now that we have: 
            #   1) the vendorfile dataclass
            #   2) that file's header's matching rubric header
            # It is time to begin 
            #--------------------
            for ii,row in enumerate(rows):
                #--------------------
                #SQL Full:	ITEM_NO	, PROF_ALPHA_2 , DESCR , LST_COST , PRC_1 , TAX_CATEG_COD , CATEG_COD , ACCT_COD , ITEM_VEND_NO , PROF_COD_4 , PROF_ALPHA_3 , PROF_DAT_1 , QTY , ImageUrl , ImageUrl2 , Description , ProductType , Collection , OptionName , OptionType , OptionDescription
                #SQL csv:	ITEM_NO	, PROF_ALPHA_2 , DESCR , LST_COST , PRC_1 , TAX_CATEG_COD , CATEG_COD , ACCT_COD , ITEM_VEND_NO , PROF_COD_4 , PROF_ALPHA_3 , PROF_DAT_1 , QTY
                #--------------------
                if annotations:
                    print("_______________________________________________________")
                    print ("\t",rows.index(row)," out of ",len(rows))
                    print ("\t\t",row)
                #--------------------
                percent_complete=(rows.index(row)/len(rows))
                dpg.configure_item(f'{file.name}_prog',show=True,default_value=percent_complete,overlay=f"{int(percent_complete*100)}%")
                #--------------------
                ignore_threshold = False
                if not ignore_threshold:
                    """ 
                    This section tries to determine if the row is empty save for one or two typos.
                        Often at the end of a vendorfile were there rows with no entries save for a "_" or "#"
                        Or empty rows used as spacers between rows with valid information.
                    """
                    '''
                    cutoff_threshold = 4
                    # If the number of empty cells in a row is greater than or equal to the full length of the row minus the threshold, go to next row. 
                    if (row.count('')+row.count(None))>=len(row)-cutoff_threshold and (len(row)-cutoff_threshold>0):

                        if annotations: 
                            print ("\t\t",str(row.count('')+row.count(None))," out of ",len(row)," cells blank. Skipping...")
                        continue
                    '''
                    if (row.count('')+row.count(None)+row.count('None')==len(row)):
                        print ("\t\t",str(row.count('')+row.count(None)+row.count('None'))," out of ",len(row)," cells blank. Skipping...")
                        continue
                #--------------------
                # vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
                temp_list,remainders = self.iterateColumns(row,file,vendor_format_dict,output_order,annotations)
                # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                # AFTER ALL COLUMNS LOOPED FROM CURRENT ROW:
                #==================================================
                #       CHECK EMPTY TEMP_LIST
                # For each cell in the line we're appending, if any of them aren't empty, its not an empty line
                # Checks each entry in the temp_list. If even one of them isn't empty, the whole thing isnt empty.
                print (temp_list)
                print("<><><><><><>||||||||<><><><><>||||||||<><><><><><>")
                is_empty=True
                for cell in temp_list:
                    if cell!=None and cell!='': 
                        is_empty=False; break
                if is_empty: 
                    print(f'Row {ii} generated empty output format! Check:\t{row}')
                    continue # go to next row
                #==================================================
                #       CHECK DUPLICATE TEMP_LIST
                # Checks to see if the entry already exists in the final output array. 
                # If it already does, then it's a duplicate.
                # TO DO:
                #   - We had an error before whereby the file had 2x each entry, as opposed to one of each with double the inventory.
                if dpg.get_value("skipDuplicates")==False:
                    if dpg.get_value(file.name+"_storeLoc")=="Kens":
                        final_KENS_output_array.append(temp_list)
                        #==========================================================================
                    elif dpg.get_value(file.name+"_storeLoc")=="Olney":
                        final_OLNEY_output_array.append(temp_list)
                        #==========================================================================
                    else:
                        if remainders==True:
                            modified_list   =   temp_list.copy()
                            fixed_qty       =   str(int(float(temp_list[output_order.index('QTY')]))+1)
                            fixed_qty       =   fixed_qty.replace('.0','')
                            modified_list[output_order.index('QTY')]=fixed_qty
                            final_KENS_output_array.append(modified_list)
                        else:
                            final_KENS_output_array.append(temp_list)
                        final_OLNEY_output_array.append(temp_list)
                else: 
                    if dpg.get_value(file.name+"_storeLoc")=="Kens" and (temp_list not in final_KENS_output_array):
                        if temp_list not in final_KENS_output_array: 
                            final_KENS_output_array.append(temp_list)
                        else: 
                            print (f"DUPLICATE line not added to Kens_Array\n\t{temp_list}")
                        #==========================================================================
                    elif dpg.get_value(file.name+"_storeLoc")=="Olney" and (temp_list not in final_OLNEY_output_array):
                        if temp_list not in final_OLNEY_output_array: 
                            final_OLNEY_output_array.append(temp_list)
                        else:
                            print (f"DUPLICATE line not added to Olney_Array\n\t{temp_list}")
                        #==========================================================================
                    else:
                        # If both stores; give remainder to one store
                        # Currently hardcoded as KENS but could make a button or switcher
                        # = = = = = = = = = = =
                        if remainders==True:
                                modified_list   =   temp_list.copy()
                                fixed_qty       =   str(int(float(temp_list[output_order.index('QTY')]))+1)
                                fixed_qty       =   fixed_qty.replace('.0','')
                                modified_list[output_order.index('QTY')]=fixed_qty
                        # = = = = = = = = = = =
                        if modified_list not in final_KENS_output_array: 
                            final_KENS_output_array.append(modified_list)
                        else: 
                            print (f"DUPLICATE line not added to Kens_Array\n\t{modified_list}")
                        # = = = = = = = = = = =
                        if temp_list not in final_OLNEY_output_array: 
                            final_OLNEY_output_array.append(temp_list)
                        else:
                            print (f"DUPLICATE line not added to Olney_Array\n\t{temp_list}")
            #==================================================
            #       MOVE FILE
            self.formatted_count+=1
            #--------------------------------------------------------------               
            print( "\t\t"+"--> Moving file"+"\n")
            try: 
                File_Operations.cleanup(file.name,self.input_filepath,self.processed_filepath)
                print("\t\t\t"+"File transferred correctly."+"\n\n")
            except Exception as e:
                print("\t\t\t"+"File did not transfer correctly."+str(e)+"\n")
                print("\t\t\t"+"File unmoved."+"\n\n")
                
            print("\t\t"+"Formatting Complete."+"\n\n")
        #===========================================
        self.final_KENS_output_array  = final_KENS_output_array
        self.final_OLNEY_output_array = final_OLNEY_output_array
        self.final_BOTH_output_array  = final_BOTH_output_array

    def iterateColumns(self,row,file,vendor_format_dict,output_order,annotations=False):
        temp_list   =   []
        remainders  =   False
        header=file.header
        #============================================================
        # v v v v v v v v v v v v v v v v v v v v v v v v v v v v v v
        print (f'::------------ Problematic Columns Start:')

        for column in output_order:
            #print (f'CURRENT COLUMN:\t{column}')
            try: 
                if column == 'ITEM_NO':
                    # <<<<<<<<<<< UPC >>>>>>>>>>>
                    #print(row[header.index(vendor_format_dict[column])] == None)
                    #--------------------
                    if (column not in vendor_format_dict.keys()):

                        if i==0:
                            temp_upc = Auto_Assigner.getNextUPC()
                            self.temp_AA.append(temp_upc)
                        else:
                            temp_upc = self.temp_AA[self.AA_count]
                            self.AA_count+=1

                        temp_list.append(temp_upc)
                        AA=True
                    elif (row[header.index(vendor_format_dict[column])] == '') or (row[header.index(vendor_format_dict[column])] == None)or (row[header.index(vendor_format_dict[column])] == ' ')or (row[header.index(vendor_format_dict[column])] == 'None'):
                        # If there is no UPC code found, begin autoassign. 
                        #temp_list.append("(AUTO-ASSIGN)")

                        if i==0:
                            temp_upc = Auto_Assigner.getNextUPC()
                            temp_AA.append(temp_upc)
                        else:
                            temp_upc = temp_AA[AA_count]
                            AA_count+=1


                        temp_list.append(temp_upc)

                        AA=True
                    else: 
                        temp_sku = row[header.index(vendor_format_dict[column])]
                        #---------- FORMAT HERE
                        temp_sku = str(temp_sku).replace("-","")
                        temp_sku = str(temp_sku).replace(" ","")
                        #---------- FORMAT END
                        temp_list.append(temp_sku)
                        sku      = row[header.index(vendor_format_dict[column])]
                        if self.talk_to_wix:
                            resp = WIX_Utilities.get_product(sku)
                            print(f"Did Wix find a product?\t{resp}")
                        AA=False
                    #--------------------
                elif column == 'PROF_DAT_1':
                    # <<<<<<<<<<< Today's Date >>>>>>>>>>>
                    #--------------------
                    today = date.today()
                    temp_list.append(today.strftime("%m/%d/%y"))
                    #--------------------
                elif column == 'LST_COST':
                    # <<<<<<<<<<< Last Cost >>>>>>>>>>>
                    # What we bought it for
                    #--------------------
                    temp_price = row[header.index(vendor_format_dict['LST_COST'])]
                    temp_price = str(temp_price).replace("$",'')
                    temp_price = str(temp_price).replace(" ",'')
                    temp_list.append(temp_price)
                    #--------------------
                elif column == 'ACCT_COD' or column == "CATEG_COD":
                    # <<<<<<<<<<< Dept >>>>>>>>>>>
                    #--------------------
                    dept="00"+str(file.department)
                    if len(dept)>3: dept=dept[1:]
                    temp_list.append(dept)
                    #--------------------
                elif column == 'PROF_ALPHA_3':
                    # <<<<<<<<<<< Man # >>>>>>>>>>>    
                    # Same as Manufacturing #
                    #--------------------
                    temp_list.append(row[header.index(vendor_format_dict['PROF_ALPHA_2'])])
                    #--------------------
                elif column == 'PRC_1':
                    # <<<<<<<<<<< Retail Price >>>>>>>>>>>          
                    #--------------------
                    overwrite_price     =   dpg.get_value(f"{file.name}_overwritePrice")
                    use_cost            =   False
                    #--------------------
                    if ('PRC_1' in vendor_format_dict.keys() and not overwrite_price):
                        # This should only work if the rubric has a column correspondence for PRC_1...
                        #   as in... we should know what files will have price overrides, and can accomodate in the rubric file
                        temp_price       =      row[header.index(vendor_format_dict['PRC_1'])]

                        if temp_price is None:
                            print (temp_price,"\t1\t",type(temp_price))
                            use_cost=True
                        elif temp_price=='':
                            print (temp_price,"\t2\t",type(temp_price))
                            use_cost=True
                        elif temp_price.count(' ')==len(list(temp_price)):
                            print (temp_price,"\t3\t",type(temp_price))
                            use_cost=True
                        elif temp_price=="None":
                            print (temp_price,"\t4\t",type(temp_price))
                            use_cost=True
                        else:
                            print (temp_price,"\t5\t",type(temp_price))
                            temp_price  =   str(temp_price).replace("$",'')
                            price       =   temp_price
                    else:   use_cost=True
                    #--------------------            
                    if use_cost:

                        markup = Utilities.Markup()

                        # -------------
                        deptCode                =    file.department
                        temp_price              =    row[header.index(vendor_format_dict['LST_COST'])]
                        temp_price              =    str(temp_price).replace("$","")
                        temp_price              =    str(temp_price).replace(" ","")
                        # -------------
                        try:
                            strPrice            =   temp_price
                            strBasedPrice       =   markup.markupCalculator(strPrice,self.JFGC.getDptByCode(deptCode))
                            price               =   strBasedPrice
                        except:
                            intFloatPrice       =   int(float(temp_price))
                            intFloatBasedprice  =   markup.markupCalculator(intFloatPrice,self.JFGC.getDptByCode(deptCode))
                            price               =   intFloatBasedprice
                        # -------------
                    temp_list.append(price)
                    #--------------------
                elif column == 'TAX_CATEG_COD':
                    # <<<<<<<<<<< TAX CODE >>>>>>>>>>>    
                    #--------------------
                    temp_list.append(file.taxCode)
                    #--------------------
                elif column == 'ITEM_VEND_NO':
                    # <<<<<<<<<<< Vendor Code >>>>>>>>>>>    
                    #--------------------
                    temp_list.append(file.vendorCode)
                    #--------------------
                elif column == 'PROF_COD_4':   # ITEM PRICE CODE
                    # <<<<<<<<<<< Item Price Code >>>>>>>>>>>    
                    #--------------------
                    dept=int(file.department)
                    if (dept >=1 and dept<=14) or (dept>=34 and dept<=53): 
                        temp_list.append("A")
                    elif (dept >=15 and dept<=24):
                        temp_list.append("B")
                    elif (dept >=25 and dept<=31):
                        temp_list.append("C")
                    #--------------------
                elif column == 'ImageUrl':
                    # <<<<<<<<<<< Image URL (if it exists) >>>>>>>>>>>    
                    #--------------------
                    temp_str_barcode =''
                    print(f'Autoassigned?\t{AA}')
                    if AA==False:
                        format_dict_label = vendor_format_dict.get(column,None)
                        if format_dict_label==None:
                            # If the url column is empty, try wix.
                            if self.talk_to_wix:
                                temp_url = WIX_Utilities.get_url(resp)
                                print (temp_url)
                                temp_str_barcode=temp_url
                            else:
                                temp_str_barcode = ''
                        else: 
                            # If the url column has data, take that info.
                            temp_str_barcode = row[header.index(format_dict_label)]
                        #------------------------------------------------------------
                        # Only uses barcode lookup if wix's URL returned nothing
                        if (temp_str_barcode == '') and (dpg.get_value('barcode_lookup')==True):
                            temp_barcode = UPCLookup.upcLookup(sku)
                            temp_str_barcode = temp_barcode['productImageUrl']
                        #------------------------------------------------------------
                    print("does it get here? C")

                    temp_list.append(temp_str_barcode)
                    #--------------------
                elif column == "Collection":
                    # <<<<<<<<<<< Collection >>>>>>>>>>>    
                    #--------------------
                    temp_collection = ''
                    if AA==False:
                        if self.talk_to_wix:
                            temp_collection = WIX_Utilities.get_collection(resp)
                    temp_list.append(temp_collection)
                    #--------------------
                elif column == "QTY":
                    # <<<<<<<<<<< Quantity >>>>>>>>>>>    
                    #--------------------
                    temp_qty = ''

                    if (column not in vendor_format_dict.keys()):
                        temp_qty = '0'
                    elif row[header.index(vendor_format_dict[column])] != '' and  row[header.index(vendor_format_dict[column])] != None:
                        temp_qty = str(row[header.index(vendor_format_dict[column])])
                    else: 
                        temp_qty = '0'

                    if dpg.get_value(file.name+"_qtyDivide")=="Divide Evenly" and temp_qty!='0':
                        if int(float(temp_qty))%2==0:
                            halved_qty = str(int(float(temp_qty))/2)
                            halved_qty = halved_qty.replace('.0','')
                        else:
                            halved_qty = str((int(float(temp_qty))-1)/2)
                            halved_qty = halved_qty.replace('.0','')
                            remainders = True
                        temp_qty = halved_qty

                    temp_list.append(str(temp_qty))
                    #--------------------
                else:
                    # <<<<<<<<<<< UNDEFINED >>>>>>>>>>>    
                    #--------------------
                    if column in vendor_format_dict.keys():
                        temp_list.append(row[header.index(vendor_format_dict[column])])
                    else: temp_list.append('')
                    #--------------------
            except Exception as e:
                #if annotations: print (column,"\t",e)
                print (column,"\t",e)
                temp_list.append('*!ERROR!*')
        print("----- problematic columns end::")
        #============================================================
        return temp_list, remainders

    def saveFilesToStaged(self,savefile_format,format_name):
        temp_saved_filenames=[]
        #---------------------------------
        print( " -->"+"For "+format_name+":"+"\n")
        print( "\t\t"+str(self.formatted_count)+" out of "+str(len(self.vendorfileobj_list))+" files processed without any errors.\n")
        print ("SAVING FILES!!!!!!!!!!!!!!!!!")
        #---------------------------------
        for i,output_array in enumerate([self.final_KENS_output_array,self.final_OLNEY_output_array]):
            #---------------------------------
            if len(output_array)==1: continue #aka IT'S ONLY THE HEADER
            if i==0:    store_loc = "Kens"
            elif i== 1: store_loc = "Olney"
            #---------------------------------
            if dpg.get_value("defaultSave?")==True:
                # Weekday / Month / Day
                savefile_name   =   'Inventory-'+store_loc+"-"+format_name
            else: 
                savefile_name   =   dpg.get_value("outputFileName")+"-"+store_loc+"-"+format_name

            temp_saved_filenames.append(savefile_name)
            #---------------------------------
            # If the partial is saving, save it as CSV for better Counterpoint integration in addition to an excel, which Full will also be saved as.
            #if savefile_format.lower() == 'SQL Partial'.lower():
            #    File_Operations.list_to_csv(output_array,self.staged_filepath+savefile_name+".csv")
            #else:
            File_Operations.list_to_excel(output_array,self.staged_filepath+savefile_name+".xlsx")
        
        self.saved_filenames = temp_saved_filenames
        # ^ in the future, will be replaced by another file rubric reading of the STAGED section (not input)


    def reorder_rubric_dict(self,unordered_dict):
        # Each dict passed here should have the same length
        #----------------------
        dict_as_list_header=[]
        #----------------------
        i=0
        while i<=len(unordered_dict.keys()):
            try:dict_as_list_header.append(unordered_dict[i])
            except: pass
            i+=1
        #----------------------
        return dict_as_list_header

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
            height = 63
        else:   
            app_data=True
            height = 190 

        dpg.configure_item(user_data+'_window',show=app_data)
        dpg.configure_item(user_data+"_entireChild",height=height)
        dpg.configure_item(user_data+'_tabBar',show=app_data)

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

    def helper_update_deptCode(self,sender,app_data,user_data):
        print("helper_update_deptCode START:")
        print(sender)
        print(app_data)
        print(user_data)
        dpg.configure_item(f'{sender}Str',default_value=self.JFGC.getDptByDptStr(app_data).code)
        print("helper_update_deptCode END")

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

    def helper_update_headerCheck(self,vendorfileObj):
        # updates the rubric portion of header check
        print(vendorfileObj.formatting_dict)

        vendor_name=vendorfileObj.vendorName
        # assuming vendorfile vendor has been found
        dpg.configure_item(vendorfileObj.name+"_headerName",default_value=vendor_name,show=True,color=(127, 255, 212))
        
        for index,item in enumerate(vendorfileObj.header):
            if item != 'None' and item != None:
                #print(f'CONFIG: {vendorfileObj.name}_rubric_headercheck_{index}')

                dpg.configure_item(f'{vendorfileObj.name}_rubric_headercheck_{index}',default_value=f'| {item} ')
 
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

            vendor_format_dict  =   {}
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
            helper_update_headerCheck(vendorfileObj)
        #----------------------------------
        return status

    def find_rubric(self,vendorfileObj,annotations=False):
        # attach rubric to obj

        # Vendorfile headers are messy. 
        # They sometimes have tons of extra 'None' values returned with them, and are full of variations that will need to be accounted for.
        # The base vendor_rubrics we have, though, represent the minimum needed column values for successfully autoformatting. 
        found = False

        # check all vendors
        for vendor_name in self.vends.keys():
            # if the headers match                    
            if self.all_headers[vendor_name] == vendorfileObj.header:
                #--------------------
                found = True
                header_to_display   = self.all_headers[vendor_name]
                #--------------------
                if annotations: 
                    #print ("MATCH: ",str(match_count)); match_count+=1
                    print ("\t"+str(vendorfileObj.name))
                    print ("\t"+str(vendor_name))
                    print ("\t\t"+str(vendorfileObj.header))
                    print ("\t\t"+str(self.all_headers[vendor_name]))
                    print ("============================")
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
                self.helper_update_headerCheck(vendorfileObj)

                '''dpg.configure_item(vendorfileObj.name+"_headerName",default_value=vendor_name,show=True,color=(127, 255, 212))
                #--------------------
                #rubric_header_group = dpg.add_group(horizontal = True)
                for index,item in enumerate(header_to_display):
                    if item != 'None' and item != None:
                        print(f'CONFIG: {vendorfileObj.name}_rubric_headercheck_{index}')

                        dpg.configure_item(f'{vendorfileObj.name}_rubric_headercheck_{index}',default_value=f'| {item} ')'''
                #--------------------
                break
      
            # COuld create another check here such that, if nothing is still found, re-iterate, 
            # and look for the .issubset functionality contained originally. 
        if not found:
            vendorfileObj.set_formatting_dict(None,None)
            #dpg.add_text(f'NO FORMAT FOUND --> Create a new one with the next tab!')
            dpg.configure_item(vendorfileObj.name+"_headerName",show=True,color   =   (238, 75, 43))

    def processing_helper(self,sender,app_data,user_data):
        # Generic Helper Class for either Individual or Multiple file processing.
        #---------------------------
        for x in user_data: print (x)
        #---------------------------
        vendorfile_list =   user_data[0]
        pathing_dict    =   user_data[1]
        #today           =   user_data[2]
        annotations     =   user_data[2]
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
                    #temp_dept   =   dpg.get_value(vendorfileObj.name+"_dept")
                    dept        =   int(dpg.get_value(f'{vendorfileObj.name}_deptStr'))
                    #dept_dict_fwds[temp_dept]  
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
        processor = InputProcessor(self.JFGC,list_to_process,self.pathing_dict)
        #process_inputs(list_to_process,pathing_dict,today,annotations)
        # go to next stage

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
            with dpg.tab_bar(tag=vendorfileObj.name+"_tabBar"):
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
                        dpg.add_combo(items=temp_vendor_names,id=vendorfileObj.name+'_combo',default_value='', width=150,parent=vendor_group)
                        try:        
                            #dpg.add_combo(items=temp_vendor_names,id=vendorfileObj.name+'_combo',default_value=temp_vendor_names[0], width=150,parent=vendor_group)
                            dpg.configure_item(vendorfileObj.name+'_combo',default_value=temp_vendor_names[0])
                        except:     
                            #dpg.add_combo(items=temp_vendor_names,id=vendorfileObj.name+'_combo',default_value=guess_val, width=150,parent=vendor_group)
                            dpg.configure_item(vendorfileObj.name+'_combo',default_value=guess_val)
                        #--------------------
                        # DEPT
                        #--------------------
                        dept_group      = dpg.add_group(horizontal=False,parent = information_group)
                        deptInfo_group  = dpg.add_group(horizontal=True,parent = dept_group)

                        dpg.add_text(tag=f'{vendorfileObj.name}_deptInfo',default_value="Department Code:",parent=deptInfo_group)
                        dpg.add_text(tag=f'{vendorfileObj.name}_deptStr',default_value='XX',parent=deptInfo_group,color=(160,160,250))
                        dpg.add_combo(width=160,id=vendorfileObj.name+"_dept",items = list(self.JFGC.dptByStr.keys()),default_value='~None Found~',parent=dept_group,callback=self.helper_update_deptCode)

                        try:
                            temp_def_val = self.JFGC.getDptByCode(vendorfileObj.department.dptStr)
                            print("__________"+temp_def_val)
                            print(vendorfileObj.department)
                            print(type(temp_def_val))

                            if temp_def_val==f"No department found with code {vendorfileObj.department}!": 
                                raise Exception 

                            dpg.configure_item(f'{vendorfileObj.name}_dept',default_value=temp_def_val)
                            dpg.configure_item(f'{vendorfileObj.name}_deptStr',default_value=vendorfileObj.department)
                        except Exception as e:
                            print (f"special error:\t{e}")
                        
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

                            #self.helper_update_headerCheck(vendorfileObj)

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
                                    #print(f'BUILD: {vendorfileObj.name}_rubric_headercheck_{index}')
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
            #dpg.add_checkbox(tag="move_files",label="Move files after completion?",default_value=True,parent=options_col_a)
            options_col_b = dpg.add_group(horizontal = False,parent=options_group)
            dpg.add_checkbox(tag="talk_to_wix",label="Ping wix for UPCs,Collections,Images?",default_value=True,parent=options_col_a)

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
            #today = date.today()

            dpg.set_item_user_data("process_button",user_data=[vendorfileObjList,self.pathing_dict,True])
            dpg.set_item_callback("process_button",self.processing_helper)



if __name__=="__main__":

    dpg.create_context()
    dpg.create_viewport(title='importer test', width=830, height=700)
    dpg.setup_dearpygui()

    b = StagedProcessor()   
    
    dpg.show_viewport()
    #dpg.set_primary_window("Primary Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()

