

import random

def oldCutoff():
    #technically inside a loop

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

        emptyCount = row.count('')+row.count(None)+row.count('None')

        if (emptyCount==len(row)):
            print ("\t\t",str(emptyCount)," out of ",len(row)," cells blank. Skipping...")
            #continue
    #--------------------
    # if the number of blank cells  + the number of Nonexistent cells + the number of cells that say "None" is equal to the lengh of the row:
        # it means its a truly empty row



# user interface for defining minimally necessary cells
necessary_cells = ["UPC","Man#","Desc","Cost","QTY"]
necessary_cell_locations = [6,3,13,0,5]

neccessary_cells_dict  = {
    "UPC":6,
    
    }

def skipThisRow(row: list[any]) -> bool : 

    print(row)

    for cell in necessary_cell_locations:
        if row[cell] == '':
            return True


def mainLoop():



    _skippedRows = []

    for x in range(0,100):

        #pretend is a given/random IMPORT schema
        _row = [i for i in range(0,14)]

        for i in range(0,4):
            make_blank = bool(random.randint(0,1))
            if make_blank:
                _row[i] = ""

        if skipThisRow(_row):
            print ("SKipping!")
            _skippedRows.append(_row)
            continue

    print("-------------------")
    print(_skippedRows)
    print(f'{len(_skippedRows)=}')

    # save them to a file to examine

if __name__=="__main__":
    mainLoop()