import pandas as pd
import tabula.io



def scrape_pdf(input_path, output_path, filename, saveName, annotations=False):

    annotations=True

    if annotations: print ("Converting ",filename," to csv.")
    #----------------------
    #clean_name=filename[:-4]
    #new_name=clean_name+".csv"
    #-------------
    readpath=input_path+"\\"+filename
    tables = tabula.read_pdf(readpath,pages='all',multiple_tables=True,stream=True,lattice=False)

    #tables = tabula.read_pdf(readpath,pages='1',multiple_tables=False,stream=True,lattice=False)
    #----------------------
    disparate_dataframes=[]
    true_header=''
    found_header=False
    no_of_tables=len(tables)
    #----------------------
    for table in tables:
        #----------------------
        df = pd.DataFrame(table)
        dataframeHeader=df.columns
        header=(list(df.columns))

        #----------------------
        if annotations:
            print ("{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}")
            print (table)
            print ("========== Header: ")
            print (header)
            print ("========== Tail: ")
            print(table.tail(n=1))
            print ("{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}")
        #----------------------
        # Assumes first header is the true header.
        # If subsequent headers are not equal to this true_header, skip that table and continue combining dataframe objects into single table. 
        
        #upc_column="UPC"
        #item_column="Item"
        
        upc_column=""
        item_column=""
        qty_column=""
        # If the header has not yet been found....
        if not found_header: 
            #--------------------------------------------------------------
            # Check to see if the current table's header is a match for the values we need....
            for value_name in header:
                if ("UPC".lower() in value_name.lower()):
                    found_header=True
                    upc_column = value_name
                if ("Item".lower() in value_name.lower()):
                    found_header=True
                    item_column=value_name
                if ("Qty".lower() in value_name.lower()):
                    found_header=True
                    qty_column=value_name
                # The above ^ is given two distinct IF statements to allow both upc and item column names to be saved for later use.
            #--------------------------------------------------------------
            if found_header:
                print ("header found!\t\t\t"+str(header))
                true_header = header
                found_header=True
            else: 
                continue
                '''
                # If the header is STILL not found, after iterating through the current header, iterate through the rows of the current table to see if its hidden below.
                # https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas

                messy_header=False
                
                for index,row in list(df.iterrows()):
                    possible_header_index   = index
                    possible_header         = row.tolist()
                    
                    print (index,possible_header)

                    for value_name in possible_header:
                        if ("UPC".lower() in str(value_name).lower()):
                            print ("FOUND!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                            messy_header=True
                            upc_column = value_name
                        if ("Item".lower() in str(value_name).lower()):
                            messy_header=True
                            item_column=value_name

                    if messy_header:

                        for i in range (0,no_of_tables+1):
                            try: 
                                messy_table = tabula.read_pdf(readpath,pages='all',multiple_tables=False,stream=False,lattice=True,)# area=[429,48,671,799])#pandas_options={'names': possible_header})
                                print ("-------------------[][][][][]")

                                df_2 = pd.DataFrame(messy_table)
                                dataframeHeader=df_2.columns
                                header=(list(df_2.columns))
                                print (header)
                                print ("-------------------[][][][][]")
                                for index,row in list(df_2.iterrows()):
                                    print (index,row.tolist())

                            except: print ("moving to table ",str(i))


                        break

                    else: continue


                if not messy_header:  
                    # Look at next table....
                    continue
                '''
        else:
            # If the next table's header isnt equal to the true header, its some unneeded table at the end of the PDF we can ignore. 
            # But we dont want to stop the process entirely because there could be another table below it with the fields we need. 
            if header != true_header:
                continue

        # If the true header has STILL not been found, 
        #if true_header==''


        #================
        print ("-===============-")
        print (true_header)
        print (upc_column)
        print (item_column)
        print (qty_column)
        print ("-===============-")


        if item_column!="":
            df = df.dropna(subset=[item_column]) #drops anything without an item code...
        
        if qty_column!="":
            df = df.dropna(subset=[qty_column]) #drops anything without a qty...
        #================
        '''Formatting test to remove spaces'''
        #df['UPC'] = df['UPC'].astype('str')
        if upc_column!="":
            
            try:
                df[upc_column] = df[upc_column].str.replace(' ','')
                df[upc_column] = df[upc_column].str.replace('-','')
            except Exception as e: 
                print ("Formatting errors: ",e)
                continue
        #df['UPC'] = df['UPC'].astype('str')
        #df['UPC'] = df['UPC'].str.strip()
        #================
        disparate_dataframes.append(df)


    disparate_dataframes=[]
    if (len(disparate_dataframes)==0):
        print ("No Tables Found... Scraping ALL DATA")
        for table in tables:
            df = pd.DataFrame(table)
            disparate_dataframes.append(df)

    #print (len(disparate_dataframes)   )
    
    for x in disparate_dataframes: print (x)

    print (f'# of Tables: {no_of_tables}')

    if no_of_tables==1:
        final_table = disparate_dataframes[0]
    else:
        final_table = pd.concat(disparate_dataframes)
    final_table.to_csv(output_path+"\\"+saveName,index=False)

def scrape_pdf_alt(input_path, output_path, filename, saveName, annotations=False):

    #   https://tabula-py.readthedocs.io/en/latest/getting_started.html

    if annotations: print (f"Converting {filename} to csv.")
    #----------------------
    readpath=f"{input_path}\\{filename}"
    #----------------------
    '''
    tables = tabula.read_pdf(readpath,pages='all',multiple_tables=True,stream=True,lattice=False)
    all_items = []

    for table in tables:
        print ("==============")
        print (type(table))
        #print (table)
        print (table.columns)

        table_header = list(table.columns)


        all_items.append(table_header)

        for row in table.iterrows():
            print (row)
            temp_row = []
            for item in list(row):
                temp_row.append(str(item))
            all_items.append(temp_row)

    from File_Operations import list_to_excel
    '''
    savenameEE = f"{output_path}\\ALT_{saveName}"

    #list_to_excel(all_items,savenameEE)
    tabula.convert_into(readpath,savenameEE,output_format="csv",stream=True,lattice=True,pages="all")
    savenameEE = f"{output_path}\\ALT_2_{saveName}"
    try: tabula.convert_into(readpath,savenameEE,output_format="csv", stream=True,lattice=False,pages="all")
    except Exception as e:      print ("no work:\t",e)
    savenameEE = f"{output_path}\\ALT_3_{saveName}"

    try: tabula.convert_into(readpath,savenameEE,output_format="csv",stream=False,lattice=True,pages="all")
    except Exception as e:      print ("no work:\t",e)

    savenameEE = f"{output_path}\\ALT_4_{saveName}"

    try: tabula.convert_into(readpath,savenameEE,output_format="csv",stream=False,lattice=False,pages="all")
    except Exception as e:      print ("no work:\t",e)

    #return




    tables = tabula.read_pdf(readpath,pages='all',multiple_tables=False,stream=True,lattice=False)
    #----------------------
    disparate_dataframes=[]
    true_header=''
    found_header=False
    no_of_tables=len(tables)
    #----------------------
    for table in tables:
        #----------------------
        df = pd.DataFrame(table)
        dataframeHeader=df.columns
        header=(list(df.columns))

        #----------------------
        if annotations:
            print ("{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}")
            print (table)
            print ("========== Header: ")
            print (header)
            print ("========== Tail: ")
            print(table.tail(n=1))
            print ("{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}")
        #----------------------
        # Assumes first header is the true header.
        # If subsequent headers are not equal to this true_header, skip that table and continue combining dataframe objects into single table. 
        
        #upc_column="UPC"
        #item_column="Item"
        
        upc_column=""
        item_column=""
        qty_column=""
        # If the header has not yet been found....
        if not found_header: 
            #--------------------------------------------------------------
            # Check to see if the current table's header is a match for the values we need....
            for value_name in header:
                if ("UPC".lower() in value_name.lower()):
                    found_header=True
                    upc_column = value_name
                if ("Item".lower() in value_name.lower()):
                    found_header=True
                    item_column=value_name
                if ("Qty".lower() in value_name.lower()):
                    found_header=True
                    qty_column=value_name
                # The above ^ is given two distinct IF statements to allow both upc and item column names to be saved for later use.
            #--------------------------------------------------------------
            if found_header:
                print ("header found!\t\t\t"+str(header))
                true_header = header
                found_header=True
            else: 
                continue
                '''
                # If the header is STILL not found, after iterating through the current header, iterate through the rows of the current table to see if its hidden below.
                # https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas

                messy_header=False
                
                for index,row in list(df.iterrows()):
                    possible_header_index   = index
                    possible_header         = row.tolist()
                    
                    print (index,possible_header)

                    for value_name in possible_header:
                        if ("UPC".lower() in str(value_name).lower()):
                            print ("FOUND!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                            messy_header=True
                            upc_column = value_name
                        if ("Item".lower() in str(value_name).lower()):
                            messy_header=True
                            item_column=value_name

                    if messy_header:

                        for i in range (0,no_of_tables+1):
                            try: 
                                messy_table = tabula.read_pdf(readpath,pages='all',multiple_tables=False,stream=False,lattice=True,)# area=[429,48,671,799])#pandas_options={'names': possible_header})
                                print ("-------------------[][][][][]")

                                df_2 = pd.DataFrame(messy_table)
                                dataframeHeader=df_2.columns
                                header=(list(df_2.columns))
                                print (header)
                                print ("-------------------[][][][][]")
                                for index,row in list(df_2.iterrows()):
                                    print (index,row.tolist())

                            except: print ("moving to table ",str(i))


                        break

                    else: continue


                if not messy_header:  
                    # Look at next table....
                    continue
                '''
        else:
            # If the next table's header isnt equal to the true header, its some unneeded table at the end of the PDF we can ignore. 
            # But we dont want to stop the process entirely because there could be another table below it with the fields we need. 
            if header != true_header:
                continue

        # If the true header has STILL not been found, 
        #if true_header==''


        #================
        print ("-===============-")
        print (true_header)
        print (upc_column)
        print (item_column)
        print (qty_column)
        print ("-===============-")


        if item_column!="":
            df = df.dropna(subset=[item_column]) #drops anything without an item code...
        
        if qty_column!="":
            df = df.dropna(subset=[qty_column]) #drops anything without a qty...
        #================
        '''Formatting test to remove spaces'''
        #df['UPC'] = df['UPC'].astype('str')
        if upc_column!="":
            
            try:
                df[upc_column] = df[upc_column].str.replace(' ','')
                df[upc_column] = df[upc_column].str.replace('-','')
            except Exception as e: 
                print ("Formatting errors: ",e)
                continue
        #df['UPC'] = df['UPC'].astype('str')
        #df['UPC'] = df['UPC'].str.strip()
        #================
        disparate_dataframes.append(df)


    disparate_dataframes=[]
    if (len(disparate_dataframes)==0):
        print ("No Tables Found... Scraping ALL DATA")
        for table in tables:
            df = pd.DataFrame(table)
            disparate_dataframes.append(df)

    #print (len(disparate_dataframes)   )
    
    for x in disparate_dataframes: print (x)

    print (f'# of Tables: {no_of_tables}')

    if no_of_tables==1:
        final_table = disparate_dataframes[0]
    else:
        final_table = pd.concat(disparate_dataframes)
    final_table.to_csv(output_path+"\\Alt_X_"+saveName,index=False)


'''
inputtt = f"C:/Users/Andrew/source/repos/VENDOR_FILES/INPUT/Test"

form_inputtt = inputtt.replace("/","\\")

print (form_inputtt)

filename = "ASCEODP_NWINVOICEP_M427232708spice2.PDF"


scrape_pdf(form_inputtt,form_inputtt,filename,"test2",True)'''

