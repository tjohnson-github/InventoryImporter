

from Operations_Builtin import builtinFunctions
from Operations import OperationMinimal
from JSONtoDataclass import getUserDataTags


def reverseDict(ini_dict,annotations=False):
    # initialising dictionary
 
    # print initial dictionary
    if annotations: print("initial dictionary : ", str(ini_dict))
 
    # inverse mapping using zip and dict functions
    inv_dict = dict(zip(ini_dict.values(), ini_dict.keys()))
 
    # print final dictionary
    if annotations: print("inverse mapped dictionary : ", str(inv_dict))

    return inv_dict

def calculateOperations(operations:list[OperationMinimal], current_row, input_rows_header, starting_val,schema,inputFile,revTags) -> any:

    def gatherKwargs(op):

        _kwargs = {}

        print("================= Beginning OPs")

        for key,val in op.input_desc.items():

            print(key,val)

            if val["choice"]=="Static Value":
                _kwargs.update({key:val["value"]})
            elif val["choice"]=="Tag":

                # Instead grab the value at the current row's tag
                #_tagName = val["value"] # this is the name of the input_tag
                _outputTagName = val["value"]
                print(f'{_outputTagName=}')
                _inputTag = revTags.get(_outputTagName,None)

                # if the operation's _tagName is equal to the current row's _tagName in the input header
                _valueAtTag = getVal(_inputTag,current_row,input_rows_header,schema,inputFile,revTags)

                _kwargs.update({key:_valueAtTag})

                # Does not need to grab the 
                pass

            elif val["choice"]=="Derived":

                print("-------------------- DERIVED CALC\n\n")

                _opTags = getUserDataTags("operation")
                
                _inputTag = val["value"]

                #_original_Dict = reverseDict(revTags)
                #_inputTag = _original_Dict.get(_inputTag,None)

                if _inputTag in list(revTags.keys()):
                    _original_Dict = reverseDict(revTags)
                    _inputTag = _original_Dict.get(_inputTag)
                    
                    _valueAtTag = getVal(_inputTag,current_row,input_rows_header,schema,inputFile,revTags)

                    #_inputTag = revTags.get(_outputTagName)
                else:
                    for fnc in schema.filenameConventions:
                        # should be 1
                        _valueAtTag = fnc.getVal(inputFile.name,_inputTag)
                        break
                print(f'{_valueAtTag=}')

                print(f'{_inputTag=}')
                _filterName = val["value_filter"]
                print(f'{_filterName=}')

                try:
                    
                    #print(f'{_valueAtTag=}')

                    _derivedValue = _opTags[key][_valueAtTag]

                    print(f'{_derivedValue=}')


                except Exception as e:
                    print(f'Error finding derived value:\t{e}')
                    _derivedValue = f'Error finding derived value:\t{e}'

                _kwargs.update({key:_derivedValue})

        return _kwargs

    _val: any

    for op in operations:

        # IF there are multiple operations, 
        #   1) you can only have 1 static value (and it must be first)
        #   2) any subsequent operations can be chained
        #       2a) each link in the chain should default to use the CURRENT TAG's column as source value
        #   3) If a link later in the chain uses a DIFFERENT TAG as its source, it's effectively overwritten the previous value the chain has been building.

        for fn in builtinFunctions:
            if op.operationType == fn.name:

                kwargs = gatherKwargs(op)

                print(f'{kwargs=}')

                _val = fn.operationActual(**kwargs)
                break
    
    return _val

#def getVal(current_row, column_index, output_tags,revTags,inputFile):
def getVal(input_tag,current_row,input_rows_header,schema,inputFile,revTags):

    #=========================================================================
    # If there is such a tag in the dict, SOURCE IT FIRST... as it may be used in the column
    if input_tag:

        if input_tag not in list(revTags.values()):
            # look into dirname or filename conventions
            print(f'{input_tag=} not in {list(revTags.values())=}')
            print("Checking conventions....")

            _val = None

            for fnc in schema.filenameConventions:
                # should be 1
                _val = fnc.getVal(inputFile.name,input_tag)

            if not _val:
                print("NOT YET IMPLEMENTED DIRNAME CONVETION GETVAL()")
                _val="ERROR NOT FOUND"

        else:

            try:
                input_column_index = input_rows_header.index(input_tag)
                input_column_val = current_row[input_column_index]
                # The value is equal to the input row @ index of the Header's matching TAG

                _val = input_column_val

            except Exception as e:
                print(f'{e}')
    else:
        # input tag not in the dictionary
        _val = ''

    return _val

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
    #revTags.col_to_tag_correspondence={
        #'UPC': 'UPC', 
        #'description': 'Description', 
        #'cost': 'Cost', 
        #'QTY': 'Quantity', 
        #'man#': 'Manufacturer #', 
        #'price': 'Price'}
    print (f'{revTags=}')

    if annotations:
        print("----------------------------------")
        print (f'{inputFile.header}')

    # Iterate through each ROW in the INPUT FILE
    for row in inputFile.rows:

        _row = []

        # Iterate through COLUMN in the OUTPUT HEADER
        for i, output_column in enumerate(output_header):

            print(f"From <{output_tags[i]}>...")

            _tag = revTags.get(output_tags[i],None)

            print(f"Looking for <{_tag}>...")

            _val = getVal(_tag,row,inputFile.header,schema,inputFile,revTags)
          
            #=========================================================================
            # HERE is the bulk of the program:
            #   1. need to see if any operations exist, if so, do them.
            #   2. pull from source tag columsn if necessary

            if schema.outputSchemaDict["Operations"][i]:
                # Right now we only focus on one
                _opVal = calculateOperations(
                    operations          =   schema.outputSchemaDict["Operations"][i],
                    current_row         =   row,
                    input_rows_header   =   inputFile.header,
                    starting_val        =   _val,
                    schema=schema,
                    inputFile=inputFile,
                    revTags=revTags) 
                    # is this last one even necessary? if the column has an operation:
                    #   A) and it uses itself as the main one.. then it'll be grabbed up ahead anyways.
                    #       IN THIS FRAMEWORK: each column has as an operation the 'grab from another column' 
                    #   OR
                    #   B) it uses another row's value as its input...

                if _val!='':
                    print("----:::: {input_column_val} being overwritten by {_opVal}")

                _val = _opVal

            #=========================================================================
            _row.append(_val)

        output_rows.append(_row)

    #print("====================")
    #print("====================")
    #print("====================")

    #for row in output_rows:
    #    print(row)
    
    return output_rows