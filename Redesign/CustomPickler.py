

import pickle

def get(file):
    #--------------
    try:
        settings = pickle.load(open(file,'rb'))
        return settings
    except Exception as e:
        print (f"'{file}' not loaded correctly. Check permissions")
        print (e)
    #--------------
    return None

def set(file,obj):
    #--------------
    try:
        pickle.dump(obj,open(file,'wb'))
    except Exception as e:
        print (f"'{file}' not saved correctly. Check permissions")
        print (e)

