



import json
import os

from DPGStage import DPGStage
import dearpygui.dearpygui as dpg
dpg.create_context()

def parseJSON(full_filepath: str):


    with open(full_filepath) as f:
        d = json.load(f)
        print(d)

        print(type(d))

        return d

def prepareUserDataDictForTags():

    default_path = "Redesign"
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