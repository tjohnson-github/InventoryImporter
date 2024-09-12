




class SettingsTest:

    settingsName = f'{default_settings_path}\\generalSettings.txt'
  
    # ======================================
    # SEVERAL WAYS TO DO THIS
    # a
    settings: dict = {
        "tutorials"         :     False,
        "setDefaultFirst"   :     False
        }
    #------------------------------------
    # b
    tutorials           : bool  = False
    setDefaultFirst     : bool  = False
    #------------------------------------
    # c
    @dataclass
    class Settings:
        tutorials       : bool = False
        setDefaultFirst : bool = False
    #------------------------------------

    def LOADSETTINGS(self,**kwargs):
        
        def loadSettings():

            settingsDict = get(self.settingsName)

        #------------------------------------
        # a

        loadSettings()

        try:
            for key,val in settingsDict.items():
                self.settings[key]=val
        except Exception as e:
            print ("Probably doesnt exist yet:\t",e)
        #------------------------------------
        # b

        loadSettings()
        try:
            for key,val in settingsDict.items():
                setattr(self,key,val)
        except Exception as e:
            print ("Probably doesnt exist yet:\t",e)

        #------------------------------------
        # c
        self.settings_dc_instance = SettingsTest.Settings()


    def updateSettingsEXAMPLES(self,sender,app_data,user_data):
        
        # Supposed to be easy way to change values sent in from menu items.
        # I have new functionlity for this in my dataclasses in private git.

        #----------------------------------
        # a
        _label = dpg.get_item_label(sender).lower() # some times the label itself has the secret!
        self.settings[_label] = app_data

        #----------------------------------
        # b
        # self.reversed_alt_settings: dict    = {_tut:self.tutorials}
        self.alt_settings[sender] = app_data

        #----------------------------------
        # c
        # self.dc_settings: dict    = {_tut:self.settings_dc.tutorials}
        self.settings_dc_instance[sender] = app_data
        
        #----------------------------------
        # d
        # only if the label is equal to the field name!
        setattr(self.settings_dc_instance,_label,app_data)
        #----------------------------------
        # Save as pickle
        set(self.settingsName,self.settings)
