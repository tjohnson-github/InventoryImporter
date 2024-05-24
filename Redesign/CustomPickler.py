

import pickle

def get(file):
    #--------------
    try:
        loadedObj = pickle.load(open(file,'rb'))
        print (loadedObj)
        return loadedObj
    except Exception as e:
        raise Exception(f"'{file}' not loaded correctly. Check permissions:\n\t{e}")
       #print (e)
    #--------------
    return None

def set(file,obj):
    #--------------
    try:
        pickle.dump(obj,open(file,'wb'))
    except Exception as e:
        print (f"'{file}' not saved correctly. Check permissions")
        print (e)

