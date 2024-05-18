

import dearpygui.dearpygui as dpg
dpg.create_context()
from dataclasses import dataclass, field
import pyodbc

import CustomPickler
from DPGStage import DPGStage,debugDPG

default_path = "Redesign//Settings//"



class SQLLinker(DPGStage):

    after: callable

    width: int      =   500
    driver: str     =   '{ODBC Driver 17 for SQL Server}'
    defaults: dict  =   {}
    default_combo_option = "Load Saved SQL Connection"

    settingSchema = ["server","dsn_name","user_name","pwd","main"]
    settingsName = f"{default_path}defaultSQLCnxStrs.txt"

    def generate_id(self,**kwargs):

        self.after = kwargs.get("after",None)

        # Creates the main window for adding a SQL connection

        _mainDefault,_key = self.load_defaults_if_any()


        with dpg.window() as self._id:
            with dpg.group():

                self.defaultCombo = dpg.add_combo(label="Saved Connections",items=list(self.defaults.keys()),default_value=_key if _key!="" else self.default_combo_option,callback=self.update_default_values)

                dpg.add_separator()
                
                self.server = dpg.add_input_text(label="Server IP",width=self.width-200,tag=f"{self._id}_server",default_value=_mainDefault.get("server",""),callback=self.evaluateChanges)
                self.dsn_name = dpg.add_input_text(label="DSN Name",width=self.width-200,tag=f"{self._id}_dsn_name",default_value=_mainDefault.get("dsn_name",""),callback=self.evaluateChanges)
                self.user_name = dpg.add_input_text(label="User Name",width=self.width-200,tag=f"{self._id}_user_name",default_value=_mainDefault.get("user_name",""),callback=self.evaluateChanges)
                self.pwd = dpg.add_input_text(label="Password",width=self.width-200,tag=f"{self._id}_pwd",default_value=_mainDefault.get("pwd",""),callback=self.evaluateChanges)
                
                dpg.add_separator()

                with dpg.group(horizontal=True):
                    self._setDef = dpg.add_button(label="Set as Default?",callback=self.setMainDefault,enabled=False)
                    with dpg.tooltip(self._setDef):
                        dpg.add_text("Can only be chosen if you select a previously saved connection.")
                        dpg.add_separator()
                        dpg.add_text("Will not delete other saved connections.")
                        dpg.add_text("It will only auto-populate the above fields.")
                        dpg.add_text("Other connections can still be used.")
                    self._removeDef = dpg.add_button(label="Remove as Default?",callback=self.removeDefault,enabled=True if _key else False,user_data=_key)

                dpg.add_button(label="Connect!",width=self.width-200,callback=self.evaluate_if_saving_is_necessary)

    def removeDefault(self,sender,app_data,user_data):

        try:
            self.defaults[user_data].update({"main":False})
            CustomPickler.set(self.settingsName,self.defaults)
            dpg.configure_item(self._removeDef,enabled=False)
            with dpg.window(popup=True): dpg.add_text("Default removed!")
        except Exception as e:
            print("No default to remove?:\t{e}")

    def update_default_values(self,sender,app_data,user_data):

        # Populates the fields with default values loaded from the settings file combo selector

        for i, (key,val) in enumerate(self.defaults[app_data].items()):
            if key=="main":
                dpg.configure_item(self._setDef,enabled=not val)
                dpg.configure_item(self._removeDef,enabled=val)
                continue

            dpg.configure_item(f"{self._id}_{key}",default_value=val)

    def evaluateChanges(self):

        _changes = 0 

        for i, (key,val) in enumerate(self.defaults[dpg.get_value(self.defaultCombo)].items()):
            if key=="main":continue
            if val!=dpg.get_value(f"{self._id}_{key}"):
                _changes+=1;

        if _changes>0:
            dpg.configure_item(self._setDef,enabled=True)
        elif _changes <=0:
            dpg.configure_item(self._setDef,enabled=False)


    def evaluate_if_saving_is_necessary(self,sender,app_data,user_data):
        
        # Checks to see if the default combo has been changed. If it has, checks to make sure the fields have been changed before prompting a new save

        if dpg.get_value(self.defaultCombo) == self.default_combo_option:
            self.save_connection_prompt(sender,app_data,user_data)
        else:

            _changes = 0

            for i, (key,val) in enumerate(self.defaults[dpg.get_value(self.defaultCombo)].items()):
                if key=="main":continue
                if val!=dpg.get_value(f"{self._id}_{key}"):
                    _changes+=1;

            if _changes>0:
                self.save_connection_prompt(sender,app_data,user_data)
            else:
                self.attempt_to_connect(sender,app_data,user_data)


    def checkName(self,sender,app_data,user_data):

        # Shows or hides an error message notifying user that the selected cnx name will overwrite an older one

        if app_data in list(self.defaults.keys()):
            dpg.configure_item(self.saveError,default_value=f"** This will overwrite '{app_data}'**",show=True)
        else:
            dpg.configure_item(self.saveError,default_value=f"** This will overwrite '{app_data}'**",show=False)

    def setMainDefault(self,sender,app_data,user_data):

        #remove previous defaults
        for i,(key,val) in enumerate(self.defaults.items()):
            val.update({"main":False})

        _name=dpg.get_value(self.defaultCombo)
        _new = {}
        _subSchema ={}

        for val in self.settingSchema:
            if val =="main":  
                _subSchema.update({val:True})
                continue
            _subSchema.update({val:dpg.get_value(f"{self._id}_{val}")})

        _new.update({_name:_subSchema})
        self.defaults.update(_new)

        CustomPickler.set(self.settingsName,self.defaults)
        dpg.configure_item(self._removeDef,enabled=True,user_data=_name)
        dpg.configure_item(self._setDef,enabled=False)
        with dpg.window(popup=True): dpg.add_text("Default saved!")


    def save_connection_prompt(self,sender,app_data,user_data):
        
        # Loads a popup that asks if the user wants to save their connection fields

        def saveCNX(sender,app_data,user_data):
        
            # Whereas save_connection_prompt opens the window, this actually saves the fields as a schema in the default file

            _new = {}
            _subSchema ={}

            for val in self.settingSchema:
                if val =="main": 
                    #_subSchema.update({val:False})
                    continue
                _subSchema.update({val:dpg.get_value(f"{self._id}_{val}")})

            _new.update({dpg.get_value(self.cnxName):_subSchema})
            self.defaults.update(_new)

            CustomPickler.set(self.settingsName,self.defaults)

            dpg.add_separator(parent=self.saveCnxWindow)
            dpg.add_text(f"'{dpg.get_value(self.cnxName)}' successfully saved!",parent=self.saveCnxWindow)
            dpg.add_button(label="Continue",width=self.width-200,callback=self.attempt_to_connect,parent=self.saveCnxWindow)
 
        _name = ""
        _inError = False
        if dpg.get_value(self.defaultCombo)!=self.default_combo_option:
            _name = dpg.get_value(self.defaultCombo)
            _inError = True

        with dpg.window(popup=True) as self.saveCnxWindow:
            with dpg.group():
                dpg.add_text("Save these connection settings for future use?")
                dpg.add_separator()
                self.cnxName = dpg.add_input_text(label="This connection's name",default_value=_name,callback=self.checkName)
                self.saveError = dpg.add_text(f"** This will overwrite '{_name}'**",color=self.errorColor,show=_inError)
                dpg.add_separator()
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Save",callback=saveCNX)
                    dpg.add_button(label="No Thanks",callback=self.attempt_to_connect)

    def load_defaults_if_any(self):
        
        # Loads from the settings file any previously saved connection fields; doesnt check if it matches the schema yet

        _loadedDefaults = CustomPickler.get(self.settingsName)
        
        if _loadedDefaults:
            self.defaults.update(_loadedDefaults)

        print(_loadedDefaults)

        for i,(key,val) in enumerate(self.defaults.items()):
            
            for ii,(_key,_val) in enumerate(val.items()):
                print(_key,_val)
                if _key=="main" and _val==True:
                    print("hi")
                    return self.defaults[key],key

        return {},""



    def attempt_to_connect(self,sender,app_data,user_data):

         # Attempts to connect to the SQL server using all the fields; if fails, leaves up the self._id window for easy changes

        try:
            dpg.delete_item(self.saveCnxWindow)
        except:
            pass

        try:
            #with dpg.window(popup=True) as _establishing:
            #    dpg.add_text("Establishing connection...")
            #    dpg.add_text("Make sure your computer is connected to the internet.")
            #----------------
            conn_str=(f";DRIVER={self.driver};SERVER={dpg.get_value(self.server)};UID={dpg.get_value(self.user_name)};PWD={dpg.get_value(self.pwd)}")
            cnxn = pyodbc.connect(conn_str)
            cursor = cnxn.cursor()
            #----------------
            self.cnxn   = cnxn
            self.cursor = cursor
            #================
            #dpg.delete_item(_establishing)

            with dpg.window(popup=True):
                dpg.add_text("Connection Sucessful!\nHeading over to table schema importer.")
                dpg.delete_item(self._id)
                try:
                    self.after()
                except Exception as e:
                    print(f"Error with after():\t{e}")
                    raise Exception

        except Exception as e:
            print (f"{e}")
            print ("Cursor object not initialized correctly. Please run Setup and retry.")
            #dpg.delete_item(_establishing)
            with dpg.window(popup=True):
                dpg.add_text("Connection not successful; Please make sure your ODBC Drivers are installed \nand your computer has permission to access the server.")


def main():
   
    SQLLinker()

    dpg.create_viewport(title='Custom Title', width=1300, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__=="__main__":
    main()