

from dataclasses import dataclass
from CustomPickler import get,set

import dearpygui.dearpygui as dpg

default_settings_path = "Redesign\\Settings"

class SettingsManager:

    settingsName = f'{default_settings_path}\\generalSettings.txt'

    @classmethod
    def getSettings(cls):

        _settings = Settings()

        try: 
            _settings = get(cls.settingsName)
        except Exception as e:
            print("Prob doesnt exist yet:\t{e}")


        return _settings

    @classmethod
    def updateSettings(cls,sender,app_data,user_data):

        sender      = sender
        newValue    = app_data
        settingName = user_data

        #----------------------------------
        _settings = cls.getSettings()
        setattr(_settings,settingName,newValue)
        #----------------------------------
        # Save as pickle
        try:
            set(cls.settingsName,_settings)
            with dpg.window(popup=True): dpg.add_text("Settings Updated!")
        except Exception as e:
            with dpg.window(popup=True): dpg.add_text(f"Settings Failed to Update!\nError:\t{e}")


@dataclass
class Settings:
    tutorials: bool = False
    setDefaultFirst: bool = False