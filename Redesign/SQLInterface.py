

import dearpygui.dearpygui as dpg
dpg.create_context()
from dataclasses import dataclass, field
import pyodbc

import CustomPickler
from DPGStage import DPGStage

default_path = "Redesign//Settings//"



class SQLLinker(DPGStage):

    after: callable

    width: int      =   500
    driver: str     =   '{ODBC Driver 17 for SQL Server}'
    defaults: dict  =   {}
    default_combo_option = "Load Saved SQL Connection"

    settingSchema = ["server","dsn_name","user_name","pwd"]
    settingsName = f"{default_path}defaultSQLCnxStrs.txt"

    def generate_id(self,**kwargs):

        self.after = kwargs.get("after",None)

        # Creates the main window for adding a SQL connection

        self.load_defaults_if_any()

        with dpg.window() as self._id:
            with dpg.group():

                self.defaultCombo = dpg.add_combo(label="Saved Connections",items=list(self.defaults.keys()),default_value=self.default_combo_option,callback=self.update_default_values)

                dpg.add_separator()
                
                self.server = dpg.add_input_text(label="Server IP",width=self.width-200,tag=f"{self._id}_server")
                self.dsn_name = dpg.add_input_text(label="DSN Name",width=self.width-200,tag=f"{self._id}_dsn_name")
                self.user_name = dpg.add_input_text(label="User Name",width=self.width-200,tag=f"{self._id}_user_name")
                self.pwd = dpg.add_input_text(label="Password",width=self.width-200,tag=f"{self._id}_pwd")
                
                dpg.add_separator()

                dpg.add_button(label="Connect!",width=self.width-200,callback=self.evaluate_if_saving_is_necessary)

    def update_default_values(self,sender,app_data,user_data):

        # Populates the fields with default values loaded from the settings file combo selector

        for i, (key,val) in enumerate(self.defaults[app_data].items()):
            dpg.configure_item(f"{self._id}_{key}",default_value=val)

    def evaluate_if_saving_is_necessary(self,sender,app_data,user_data):
        
        # Checks to see if the default combo has been changed. If it has, checks to make sure the fields have been changed before prompting a new save

        if dpg.get_value(self.defaultCombo) == self.default_combo_option:
            self.save_connection_prompt(sender,app_data,user_data)
        else:

            _changes = 0

            for i, (key,val) in enumerate(self.defaults[dpg.get_value(self.defaultCombo)].items()):
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

    def save_connection_prompt(self,sender,app_data,user_data):
        
        # Loads a popup that asks if the user wants to save their connection fields

        def saveCNX(sender,app_data,user_data):
        
            # Whereas save_connection_prompt opens the window, this actually saves the fields as a schema in the default file

            _new = {}
            _subSchema ={}

            for val in self.settingSchema:
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

    def attempt_to_connect(self,sender,app_data,user_data):

         # Attempts to connect to the SQL server using all the fields; if fails, leaves up the self._id window for easy changes

        try:
            dpg.delete_item(self.saveCnxWindow)
        except:
            pass

        try:
            #----------------
            conn_str=(f";DRIVER={self.driver};SERVER={dpg.get_value(self.server)};UID={dpg.get_value(self.user_name)};PWD={dpg.get_value(self.pwd)}")
            cnxn = pyodbc.connect(conn_str)
            cursor = cnxn.cursor()
            #----------------
            self.cnxn   = cnxn
            self.cursor = cursor
            #================
            with dpg.window(popup=True):
                dpg.add_text("Connection Sucessful!\nHeading over to table schema importer.")
                dpg.delete_item(self._id)
                try:
                    self.after()
                except Exception as e:
                    print("Error with after():\t{e}")

        except Exception as e:
            print (f"Error:\t{e}")
            print ("Cursor object not initialized correctly. Please run Setup and retry.")
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