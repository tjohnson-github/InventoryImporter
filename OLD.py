def scanInputs(pathingDict, cloudRubric=True, automatePDF = False):
    #====================================================
    # Given a set of filepaths, scan all possible files in the INPUT folder and create the appropriate
    #   UI-based objects which will allow for manual input to more accurately process the vendorfiles.
    #====================================================
    listOfVendorfileObjs    =   []
    #====================================================
    excel_files_to_process  =   fnmatch.filter(os.listdir(pathingDict['input_filepath']), '*.xlsx')
    csv_files_to_process    =   fnmatch.filter(os.listdir(pathingDict['input_filepath']), '*.csv')
    pdf_files_to_process    =   fnmatch.filter(os.listdir(pathingDict['input_filepath']), '*.pdf') if automatePDF else []
    #====================================================
    print ("=========================================")
    #====================================================
    for file in excel_files_to_process:
        listOfVendorfileObjs.append(vendorfile(input_filepath+file))

    for file in csv_files_to_process:
        listOfVendorfileObjs.append(vendorfile(input_filepath+file))

    for file in pdf_files_to_process:
        print (f'Cannot convert {file} to CSV in the same step as processing CSVs.\tPDFs too often require manual validation.')
    #====================================================
    return listOfVendorfileObjs