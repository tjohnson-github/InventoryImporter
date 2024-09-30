

from Operations_Builtin import builtinFunctions
from Operations import OperationMinimal
from JSONtoDataclass import getUserDataTags
from dearpygui import dearpygui as dpg


def reverseDict(ini_dict,annotations=False):
    # initialising dictionary
 
    # print initial dictionary
    if annotations: print("initial dictionary : ", str(ini_dict))
 
    # inverse mapping using zip and dict functions
    inv_dict = dict(zip(ini_dict.values(), ini_dict.keys()))
 
    # print final dictionary
    if annotations: print("inverse mapped dictionary : ", str(inv_dict))

    return inv_dict

def processRubricOP(op,current_row,input_rows_header,schema,inputFile,revTags,manualTagCombos):

    _tag = op.tag
    _calc= op.calc
    _combos = op.combos

    _kwargs = {}

    print(f'{input_rows_header=}')
    print(f'{_tag=}')

    for i,variableName in enumerate(_combos):
        if variableName!='None' and variableName:#if variableName:

            _tag_of_combo = input_rows_header[i]

            #_sourceVal = getVal(_tag_of_combo,current_row,input_rows_header,schema,inputFile,revTags,manualTagCombos)
            _sourceVal = float(current_row[i])
            _kwargs.update({variableName:_sourceVal})

    print('<><><><><><><><><><><>')
    print("Calculating:::")
    print(f"\t\t{_calc}")
    print(f"\tUsing")
    print(f"\t\t{_kwargs}")

    try:
        _val = eval(_calc,_kwargs)
        print(f"\t\t{_val=}")

    except Exception as e:
        print(f"Error running <({_calc})>:\t{e=}")
        _val = f"ERROR:{e}"

    return _val

def processSchemaOp(operations:list[OperationMinimal], current_row, input_rows_header, starting_val,schema,inputFile,revTags,manualTagCombos) -> any:

    def gatherKwargs(op):

        _kwargs = {}


        for key,val in op.input_desc.items():

            print(key,val)

            if val["choice"]=="Static Value":
                _kwargs.update({key:val["value"]})
            elif val["choice"]=="Tag":

                # Instead grab the value at the current row's tag
                #_tagName = val["value"] # this is the name of the input_tag
                _tag = val["value"]
                print(f'{_tag=}')
                

                # if the operation's _tagName is equal to the current row's _tagName in the input header
                _valueAtTag = getVal(_tag,current_row,input_rows_header,schema,inputFile,revTags,manualTagCombos)

                _kwargs.update({key:_valueAtTag})

                # Does not need to grab the 
                pass

            elif val["choice"]=="Derived":

                print("-------------------- DERIVED CALC\n\n")

                _opTags = getUserDataTags("operation")
                
                _tag = val["value"]

                #_original_Dict = reverseDict(revTags)
                #_inputTag = _original_Dict.get(_inputTag,None)

                _valueAtTag = getVal(_tag,current_row,input_rows_header,schema,inputFile,revTags,manualTagCombos)

                '''if _inputTag in list(revTags.keys()):
                    #_original_Dict = reverseDict(revTags)
                    #_inputTag = _original_Dict.get(_inputTag)
                    
                    _valueAtTag = getVal(_inputTag,current_row,input_rows_header,schema,inputFile,revTags,manualTagCombos)

                    #_inputTag = revTags.get(_outputTagName)
                else:
                    for fnc in schema.filenameConventions:
                        # should be 1
                        _valueAtTag = fnc.getVal(inputFile.name,_inputTag)
                        break'''

                print(f'{_tag=}')
                print(f'{_valueAtTag=}')

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
                print(f'Running {fn.name}...')

                _val = fn.operationActual(**kwargs)
                print(f'{_val = }')
                break
    
    return _val

#def getVal(current_row, column_index, output_tags,revTags,inputFile):
def getVal(tag,current_row,input_rows_header,schema,inputFile,revTags,manualTagCombos):

    # This will return none if there's 
    _input_header_column_name = revTags.get(tag,None)

    #=========================================================================
    # If there is such a tag in the dict, SOURCE IT FIRST... as it may be used in the column

    def determine_source():

        if _input_header_column_name not in input_rows_header:

            #print(f'====> {_input_header_column_name=} not in {input_rows_header=}')

            print(f">>>>>>>>> <{_input_header_column_name}> not in Input Header; must source elsewhere...")

            _val = None

            #===============================================================
            print(">>> Checking manual tags....")
            try:

                _manual = getUserDataTags("manual")
                #print(f'{tag=}')
                #print(f'{_manual=}')
                #print(f'{manualTagCombos=}')
                #print(f'{list(_manual.keys())=}')

                if tag in list(_manual.keys()):
                    _val = dpg.get_value(manualTagCombos[tag])
                    return _val 
            except Exception as e:
                print(f"Cannot find {tag=} in manual inputs:\t{e}")

            #===============================================================
            print(">>> Checking Filename convention....")
            try:
                for fnc in schema.filenameConventions:
                    # should be 1

                    _val = fnc.getVal(inputFile.name,tag)
                    return _val
            except Exception as e:
                print(f"Cannot find {tag=} in filename conventions:\t{e}")

            #===============================================================
            print(">>> Checking Filename convention....")
            try:
                print("NOT YET IMPLEMENTED DIRNAME CONVETION GETVAL()")
            except Exception as e:
                print(f"Cannot find {tag=} in filename conventions:\t{e}")
            #===============================================================
            print(">>> Tag Cannot be sourced anywhere....")
            if not _val:
                _val=""
                return _val

        else:

            try:
                input_column_index  = input_rows_header.index(_input_header_column_name)
                input_column_val    = current_row[input_column_index]
                # The value is equal to the input row @ index of the Header's matching TAG

                _val = input_column_val

                #============================
                if _val=="None": _val= ''
                # maybe have a setting for this

                return _val

            except Exception as e:
                print(f'Error deducing value from current row:\t{e}')
                return ''
    
        '''else:
            # input tag not in the dictionary
            _val = '''''

    val = determine_source()

    

    return val

def zipFile(schema,inputFile,matchingRubric,manualTagCombos,includeHeader=False,annotations=True):
    
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

    revTags = reverseDict(matchingRubric.col_to_tag_correspondence)


    # save
    if annotations:
        print("---------------------- Beginning Zip")

        print (f'{schema.outputSchemaDict["Column Name"]=}')
        print (f'{schema.outputSchemaDict["Tag"]=}')

        #['ITEM_NO', 'PROF_ALPHA_2',    'DESCR',        'LST_COST', 'PRC_1', 'TAX_CATEG_COD',   'CATEG_COD', 'ACCT_COD',    'ITEM_VEND_NO', 'PROF_COD_4',   'PROF_ALPHA_3', 'PROF_DAT_1',   'QTY']
        #['UPC',     'man#',            'description',  'cost',     'price', 'Tax Code',        'dept',     'dept',         'Vendor Code',  'man#',         'man#',         'date',         'QTY']
        print("----------------------------------")
        
        print (f'{matchingRubric.tagOverrides=}')
        print (f'{matchingRubric.col_to_tag_correspondence=}')

        # INPUT COLUMN NAME : SCHEMA TAG

        #matchingRubric.col_to_tag_correspondence={
            #'UPC': 'UPC', 
            #'Description': 'description', 
            #'Cost': 'cost', 
            #'Quantity': 'QTY', 
            #'Manufacturer #': 'man#', 
            #'Price': 'price'}
        
        print (f'{revTags=}')

        #  SCHEMA TAG : INPUT COLUMN NAME

        #revTags.col_to_tag_correspondence={
            #'UPC': 'UPC', 
            #'description': 'Description', 
            #'cost': 'Cost', 
            #'QTY': 'Quantity', 
            #'man#': 'Manufacturer #', 
            #'price': 'Price'}

        print("----------------------------------")
        print (f'{inputFile.header=}')
        print("----------------------------------")

    def skiprow(row) -> bool:

        #if row.count("None")==len(row): return True

        if row.count('') == len(row) or row.count('None') == len(row) or row.count(None) == len(row):
            return True

        return False


    # Iterate through each ROW in the INPUT FILE
    for row in inputFile.rows:

        if skiprow(row): continue

        print("--<>--<>--<>--<>--<>--<>----------------")
        print("--<>--<>--<>--<>--<>--<>----------------")
        print(row)

        _row = []

        # Iterate through COLUMN in the OUTPUT HEADER
        for i, output_column in enumerate(output_header):

            print(f"#============\nFrom <{output_tags[i]}>...\n")

            _tag = output_tags[i]

            # Get the input column NAME from the schema tag 
            

            #print(f"Looking for <{_input_header_column_name}>...")

            if _tag in [op.tag for op in matchingRubric.ops]:
                print("================= Attempting RUBRIC OPs")
                for op in matchingRubric.ops:
                    if _tag == op.tag:

                        print(op)
                        #print(type(op))

                        _val = processRubricOP(op,row,inputFile.header,schema,inputFile,revTags,manualTagCombos)
                        print(f'{_val=}')
                        break
            elif _tag == "":
                _val = ''
            else:
                _val = getVal(_tag,row,inputFile.header,schema,inputFile,revTags,manualTagCombos)
            #=========================================================================
            # HERE is the bulk of the program:
            #   1. need to see if any operations exist, if so, do them.
            #   2. pull from source tag columsn if necessary

            _override =  matchingRubric.tag_to_override_correspondence.get(_tag,None)
            # if the override exists, we are to use the columns instead
            print(f"{_override=}")
            print(f"{_val=}")


            if not _override or _val == '':
                # If the override is not engaged, try and process the operation
                
                print("================= Attempting SCHEMA OPs")

                try:
                    if schema.outputSchemaDict["Operations"][i]:
                        # Right now we only focus on one
                        _opVal = processSchemaOp(
                            operations          =   schema.outputSchemaDict["Operations"][i],
                            current_row         =   row,
                            input_rows_header   =   inputFile.header,
                            starting_val        =   _val,
                            schema=schema,
                            inputFile=inputFile,
                            revTags=revTags,
                            manualTagCombos=manualTagCombos) 
                            # is this last one even necessary? if the column has an operation:
                            #   A) and it uses itself as the main one.. then it'll be grabbed up ahead anyways.
                            #       IN THIS FRAMEWORK: each column has as an operation the 'grab from another column' 
                            #   OR
                            #   B) it uses another row's value as its input...

                        if _val!='':
                            print("----:::: {input_column_val} being overwritten by {_opVal}")

                        _val = _opVal
                except Exception as e:
                    print(f"Error conducting operation @ tag = <{_tag}>:\n\t{e}")
                    print(f'Defaulting to found value.')

            #=========================================================================
            # INSIST ON THERE BEING SOME KIND OF FAILSAFE TO MAKE SURE THAT A RUBRIC OP OF THE SAME ___ doesnt interfere with ____




            #=========================================================================
            try:
                print(">>> Checking for final formatting...")

                _formatTags = getUserDataTags('formatting')

                #print(f'{_tag=}')
                #print(f'{_formatTags=}')


                if _tag in list(_formatTags.keys()):

                    print(f"Overwriting {_tag=} with {dpg.get_value(manualTagCombos[_tag])=}!")
                    _val = dpg.get_value(manualTagCombos[_tag])

            except Exception as e:
                print(f"Formatting requested but not found:\t{e}")

            #=========================================================================
            print("#====================================================")
            _row.append(_val)

        output_rows.append(_row)
    
    return output_rows