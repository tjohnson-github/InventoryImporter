



def reverseDict(ini_dict,annotations=False):
    # initialising dictionary
 
    # print initial dictionary
    if annotations: print("initial dictionary : ", str(ini_dict))
 
    # inverse mapping using zip and dict functions
    inv_dict = dict(zip(ini_dict.values(), ini_dict.keys()))
 
    # print final dictionary
    if annotations: print("inverse mapped dictionary : ", str(inv_dict))

    return inv_dict

def zipFile(schema,inputFile,matchingRubric,includeHeader=False,annotations=False):
    
    # This moves the columns from the input file's columns to the output schema's columns
    #   using the tags as the correspondence system


    # Special attention needs to be paid for lines that were missing or incomplete
    # or are missing ANY 1 of the necessary columns.

    output_header = schema.outputSchemaDict["Column Name"]
    output_tags   = schema.outputSchemaDict["Tag"]

    if includeHeader:
        output_rows = [output_header]
    else: 
        output_rows = []

    # save
    if annotations:
        print("---------------------- Beginning Zip")

        print (f'{schema.outputSchemaDict["Column Name"]}')
        print (f'{schema.outputSchemaDict["Tag"]}')

    #['ITEM_NO', 'PROF_ALPHA_2',    'DESCR',        'LST_COST', 'PRC_1', 'TAX_CATEG_COD',   'CATEG_COD', 'ACCT_COD',    'ITEM_VEND_NO', 'PROF_COD_4',   'PROF_ALPHA_3', 'PROF_DAT_1',   'QTY']
    #['UPC',     'man#',            'description',  'cost',     'price', 'Tax Code',        'dept',     'dept',         'Vendor Code',  'man#',         'man#',         'date',         'QTY']

        print (f'{matchingRubric.col_to_tag_correspondence=}')

    #matchingRubric.col_to_tag_correspondence={
        #'UPC': 'UPC', 
        #'Description': 'description', 
        #'Cost': 'cost', 
        #'Quantity': 'QTY', 
        #'Manufacturer #': 'man#', 
        #'Price': 'price'}

    revTags = reverseDict(matchingRubric.col_to_tag_correspondence)

    if annotations:
        print("----------------------------------")
        print (f'{inputFile.header}')
    for row in inputFile.rows:

        _row = []

        for i, output_column in enumerate(output_header):

            # Get the tag from the reversed Dictionary whereby: TAG:INPUT_NAME
            _tag = revTags.get(output_tags[i],None)

            # If there is such a tag in the dict:
            if _tag:

                try:
                    input_column_index = inputFile.header.index(_tag)
                    input_column_val = row[input_column_index]
                    # The value is equal to the input row @ index of the Header's matching TAG

                    _row.append(input_column_val)

                except Exception as e:
                    print(f'{e}')
                    print(f'{revTags[_tag]=} not in {inputFile.header=}')
            else:
                _row.append('')

        output_rows.append(_row)

    #print("====================")
    #print("====================")
    #print("====================")

    #for row in output_rows:
    #    print(row)
    
    return output_rows