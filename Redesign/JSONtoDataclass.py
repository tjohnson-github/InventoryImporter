



import json
import os

from DPGStage import DPGStage
import dearpygui.dearpygui as dpg
dpg.create_context()


default_path = "Redesign\\UserData"

class DataManager(DPGStage):

    label="Custom Data Import Manager"
    height=600
    width=600

    def generate_id(self,**kwargs):
        
        with dpg.window(label=self.label,height=self.height,width=self.width):

            dpg.add_text(f"Simply add JSON objects to <{default_path}>")
            dpg.add_text(f"<TAGS.json> will make those values available where that TAG is selected",bullet=True)
            dpg.add_text(f"<OPERATIONS.json> are mathematical equations and values that, if selected, will be applied before outputting",bullet=True)

            dpg.add_separator()
            dpg.add_button(label=f"Scan <{default_path}> for JSON objects",callback=self.scan)

            dpg.add_separator()
            with dpg.tab_bar():
                with dpg.tab(label="Tags"):
                   with dpg.child_window() as self.tagWindow:
                        pass
                with dpg.tab(label="Operations"):
                    with dpg.child_window() as self.opsWindow:
                        pass

    def scan(self):

        '''obj = os.scandir(default_path)
 
        # List all files and directories 
        # in the specified path
        #print("Files and Directories in '% s':" % default_path)
        for entry in obj :
            #if entry.is_dir() or entry.is_file():
            #    print(entry.name)
            print(entry)

            #if entry.name.endswith('.json'):

            if entry.name == 'TAGS.json':

                _ = parseJSON(f'{default_path}\\{entry.name}')
            
        '''
        def previewVal(sender,app_data,user_data):
            dpg.configure_item(user_data["destination"],default_value=user_data["tagsDict"][app_data])

        #==========================
        # TAGS
        _ = parseJSON(f'{default_path}\\TAGS.json')

        dpg.push_container_stack(self.tagWindow)

        for tagName,tags in _.items():
            print(tagName)
            
            with dpg.group(horizontal=True):
                
                dpg.add_input_text(default_value=tagName,width=100,enabled=False)
                
                dpg.add_spacer(width=30)

                _keysCombo = dpg.add_combo(items=list(tags.keys()),width=100,callback=previewVal)

                dpg.add_spacer(width=30)

                _valPreview = dpg.add_input_text(enabled=False,width=100)

                dpg.set_item_user_data(_keysCombo,{"tagsDict":tags,"destination":_valPreview})


def getManualInputTags():
    _ = parseJSON(f'{default_path}\\TAGS.json')
    return _ 

def parseJSON(full_filepath: str):


    with open(full_filepath) as f:
        d = json.load(f)
        print(d)

        print(type(d))

        return d

def prepareUserDataDictForTags():

    settingsName = f'{default_path}\\UserData.json'

    userdatadict = parseJSON(settingsName)

    return userdatadict


def setVal(sender,app_data,user_data):

    d = user_data
    key = app_data
    val = d[app_data]

    print(f'Value is {val}')

def displayContents(sender,app_data,user_data):

    d = user_data
    key = app_data
    val = d[app_data]

    dpg.push_container_stack(dpg.get_item_parent(sender))

    dpg.add_combo(items=list(d[app_data].keys()),width=100,callback=setVal,user_data=val)

def main():

    d = prepareUserDataDictForTags()

    with dpg.window():

        dpg.add_combo(items=list(d.keys()),width=100,callback=displayContents,user_data=d)


    dpg.create_viewport(title='Custom Title', width=1300, height=900)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()



if __name__=="__main__":
    main()