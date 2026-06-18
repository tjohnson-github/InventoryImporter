from JFGC_Data import SQLClient

import JFGC_Data
sqlClient = JFGC_Data.sqlClient

import itertools
import os
from File_Operations import getVariable,saveVariable
import dearpygui.dearpygui as dpg
import decorators

class AutoAssignerTab:

    def __init__(self,width,height):

        self.client = sqlClient

        with dpg.child_window(width=width,height=height):
            dpg.add_text(
                "In order to better update products and the website we circumvent CounterPoint8's (Auto-Assign UPC) function by scraping all available item numbers of any desired length and outputting them.",
                wrap=600
            )
            dpg.add_separator()

            self.targetLengthInput = dpg.add_input_int(id="autoassigner_length",default_value=6,label="Current Length",min_value=1,width=100)

            dpg.add_input_int(label="Get new item numbers (max 100 at a time)",
                              width=100,
                              default_value=0,
                              callback=self.getUPCsCustom,
                              on_enter=True,
                              step=0,
                              min_clamped=True,
                              min_value=0,
                              max_clamped=True,
                              max_value=100)
            dpg.add_text("Press Enter after inputting desired item number count.")
            dpg.add_text("Check the terminal for output and copy/paste it as a column into your spreadsheet.")

    def getUPCsCustom(self,sender,app_data):

        print(f"=============== Getting {app_data} item numbers =============")
        counter = app_data
        target_length = dpg.get_value(self.targetLengthInput)
        while counter > 0:
            print(get_next_available_item_no(target_length))
            counter -= 1



last_item_no = -1

def get_next_available_item_no(target_length=6):
    assert isinstance(target_length, int), "get_next_available_item_no expects the target_length parameter to be an int."

    global last_item_no

    if last_item_no == None:
        return None

    item_no = None
    if is_item_no_available(last_item_no + 1, target_length):
        item_no = last_item_no + 1
    else:
        item_no = get_next_available_item_no_following_an_unavailable_item_no(last_item_no, target_length)

    last_item_no = item_no

    ret = f"{item_no:0{target_length}}"

    if len(ret) != target_length: # if we ran out of numbers, e.g. we reached 1000000 with a target length of 6. 
        last_item_no == None
        return None 

    return ret

def get_next_available_item_no_following_an_unavailable_item_no(exclusive_min=-1, target_length=6):
    assert isinstance(exclusive_min, int), "get_next_available_item_no_following_an_unavailable_item_no expects the exclusive_min parameter to be an int."
    assert isinstance(target_length, int), "get_next_available_item_no_following_an_unavailable_item_no expects the target_length parameter to be an int."

    sqlClient = SQLClient()
    CURSOR_STR = f"""select top 1 a.ITEM_NO from JFGC.dbo.IM_ITEM a
                    where len(a.ITEM_NO) = {target_length}
                    and try_cast(a.ITEM_NO as int) is not null
                    and a.ITEM_NO > {exclusive_min}
                    and not exists (
                        select *
                        from JFGC.dbo.IM_ITEM b
                        where len(b.ITEM_NO) = {target_length}
                        and try_cast(b.ITEM_NO as int) is not null
                        and b.ITEM_NO = a.ITEM_NO + 1
                    )
                    order by a.ITEM_NO ASC;""";

    sqlClient.cursor.execute(CURSOR_STR)
    entry = sqlClient.cursor.fetchone()
    header = [i[0] for i in sqlClient.cursor.description]
    return int(entry[header.index("ITEM_NO")]) + 1

def is_item_no_available(item_no, target_length=6):
    assert isinstance(item_no, int), "is_item_no_available expects the item_no parameter to be an int."
    assert isinstance(target_length, int), "is_item_no_available expects the target_length parameter to be an int."
    query = f"select ITEM_NO from JFGC.dbo.IM_ITEM where ITEM_NO = '{item_no:0{target_length}}'"
    sqlClient = SQLClient()
    sqlClient.cursor.execute(query)
    ret = sqlClient.cursor.fetchone()
    return ret is None

def test(start=0, end=None):

    global last_item_no

    target_length = 6

    query = f"""select ITEM_NO from JFGC.dbo.IM_ITEM
            where len(ITEM_NO) = {target_length}
            and try_cast(ITEM_NO AS INT) is not null"""

    sqlClient = SQLClient()
    sqlClient.cursor.execute(query)
    header = [i[0] for i in sqlClient.cursor.description]
    unavailable_set = set()
    for entry in sqlClient.cursor:
        unavailable_set.add(int(entry[header.index("ITEM_NO")]))

    item_no = start
    last_item_no = start - 1
    if end == None:
        end = 10**target_length

    while item_no < end:
        if item_no not in unavailable_set:
           a = get_next_available_item_no(target_length)
           assert a == f"{item_no:06}", f"Expected {item_no:06}, got {a}."
        else:
            if is_item_no_available(item_no, target_length):
                assert not is_item_no_available(item_no, target_length), f"is_item_no_available believes {item_no} is available (expected unavailable)."
        item_no += 1

    if item_no == 10**target_length:
        assert get_next_available_item_no(target_length) is None, f"get_next_available_item_no did not start returning None after all item numbers exhausted!"

if __name__ == "main":
    pass
    #test()