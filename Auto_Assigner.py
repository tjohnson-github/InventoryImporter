

#from Counterpoint_Connectivity import getBaseSQL
from JFGC_Data import SQLClient

import itertools
import os
from File_Operations import getVariable,saveVariable


def createAvailableUPCsListObj(targetLength = 6,annotations=False):

    working_directory = os.getcwd()
    saveName = f"{working_directory}\\Data\\available_AA_UPCs_{targetLength}.txt"

    #cursor = getBaseSQL(username='sa',password='CounterPoint8')
    sqlClient = SQLClient()
    CURSOR_STR = f"SELECT * FROM JFGC.dbo.IM_ITEM ORDER BY ITEM_NO ASC;"

    sqlClient.cursor.execute(CURSOR_STR)
    header =   [i[0] for i in sqlClient.cursor.description]

    all_skus=[]

    lengths = [[] for x in range(0,30)]

    for entry in sqlClient.cursor:
        all_skus.append(entry[header.index("ITEM_NO")])

    for sku in all_skus: 
        lengths[len(sku)-1].append(sku)

    if annotations:
        print ("Length","\t","Count")
        for i,x in enumerate(lengths):
            if (len(x))==0: continue
            print ((i+1),"\t",len(x))

    is_alpha=[]
    isnt_alpha=[]

    for entry in lengths[targetLength-1]:
        if entry.isdigit():isnt_alpha.append(entry)
        else: is_alpha.append(entry)

    '''if annotations:
        print("========================")
        print (f"Alphanumeric: {len(is_alpha)}")
        print (f"Non-Alpha: {len(isnt_alpha)}")
        print("========================")
        for i,entry in enumerate(is_alpha):
            print (i+1,"\t",entry)

        print("========================")

        for i,entry in enumerate(isnt_alpha):
            print (i+1,"\t",entry)
        print("========================")'''

    discontinuous_lists=[[] for x in range(0,10000)]

    length_index=0

    print("0000000000000000000000000000000000")
    for x in isnt_alpha:
        print (x)

    continuous_list=[]
    for i,entry in enumerate(isnt_alpha):

        listed_entry = []
        listed_entry[:0]=str(entry)
        continuous_list.append(entry)
        '''
        # if its not the right length
        if i+1 > len(isnt_alpha): break

        if int(entry)+1 == int(isnt_alpha[i+1]):

            if entry not in discontinuous_lists[length_index]:
                discontinuous_lists[length_index].append(entry)

        else:
            length_index+=1
            discontinuous_lists[length_index].append(isnt_alpha[i+1])
        '''
    '''
    continuous_list=[]

    for section in discontinuous_lists:

        if section==[]: continue

        for entry in section:

            listed_entry = []

            listed_entry[:0]=str(entry)

            #tuple_formatted_entry =tuple(listed_entry)

            #continuous_list.append(tuple_formatted_entry)
            continuous_list.append(entry)

    for x in discontinuous_lists[0]: 
        print (x)


    '''        
    for x in continuous_list[:5]: 
            print (x)

    #===================================================
    permitted_characters    = ['0','1','2','3','4','5','6','7','8','9']
    total_combinations      = len(permitted_characters)**targetLength
    
    possible_combinations = list(itertools.product(permitted_characters, repeat=targetLength))

    #print (len(possible_combinations))
    #print("aaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    #for x in possible_combinations[:5]: print (x)

    formatted_possible_combinations=[(''.join(x)) for x in possible_combinations]
    #print (len(formatted_possible_combinations))
    #print("bbbbbbbbbbbbbbbbbbbbbbbbbb")
    #for x in formatted_possible_combinations[:5]: print (x)

    available_tuples = (set(formatted_possible_combinations)-set(continuous_list))
    print("ccccccccccccccccccccccccccc")
    for x in list(available_tuples)[:5]:print(x)

    
    print (type(available_tuples))
    print (len(available_tuples))
    print("Reordering....")
    '''    
    available_list = list(available_tuples)
    perfect_list=[]


    for entry in available_list:
       
        perfect_list.append(''.join(entry))

    perfect_list.sort(key=int)
    '''
    perfect_list=list(available_tuples)
    perfect_list.sort(key=int)

    for x in perfect_list[:5]:
        print(x)


    saveVariable(saveName,perfect_list)



    print("===================================")
    print("New UPC List Saved")
    print (f"{total_combinations-len(continuous_list)} UPCs of length {targetLength} remain!")


def getMultipleUPCs(number_needed=2,targetLength=6):

    # Returns a list of strings
    working_directory = os.getcwd()

    saveName = f"{working_directory}\\Data\\available_AA_UPCs_{targetLength}.txt"

    continuous = getVariable(saveName)
    
    upcs = []

    for x in range(0,number_needed):

        upcs.append(str(continuous[x]))

    new_cont = continuous.copy();

    new_cont = new_cont[number_needed:]

    saveVariable(saveName,new_cont)

    return upcs


def getNextUPC(targetLength=6):

    # Returns a string which is the lowest (numerically) available UPC of length X
    working_directory = os.getcwd()
    saveName = f"{working_directory}\\Data\\available_AA_UPCs_{targetLength}.txt"

    continuous = getVariable(saveName)

    next_available_UPC = str(continuous[0])
    continuous.remove(next_available_UPC)
    saveVariable(saveName,continuous)


    return next_available_UPC


def test():

    working_directory = os.getcwd()
    saveName = f"{working_directory}\\Data\\available_AA_UPCs.txt"

    createAvailableUPCsListObj(annotations=True)

    for x in range(0,160):
        print (x+1,"\t",getNextUPC(saveName))
    print("====================")

    aa = getMultipleUPCs(saveName,500)
    i=0;
    for x in aa:
        print (i+1,"\t",x)
        i+=1
    print("====================")
    continuous = getVariable(saveName)

    for i,upc in enumerate(continuous):
        print (i,"\t",upc)


if __name__=="__main__":
    pass
    #print (getMultipleUPCs())
    #createAvailableUPCsListObj()
    #createAvailableUPCsListObj(annotations=True)
    #getNextUPC()