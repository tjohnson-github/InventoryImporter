

from DPGStage import DPGStage
import dearpygui.dearpygui as dpg
from dataclasses import dataclass

@dataclass
class FilenameConvention:

    slices: list[str] # v        be      dimensionality v
    tags: list[str]   # ^ should    same                ^

    delim: str
    supported_extensions: list[str]

    def saveToSpreadsheet(self):
        ...

class FilenameExtractor(DPGStage):

    cell_height = 80

    delimitors = ["_","^"]
    delimitor = "_"
    name_slices = ["Ticket#","Example Name","Example Department"]

    supported_extensions = {"xlsx":True,"csv":True}

    delimitorVis: list[int]

    def load_from_spreadsheet(self) -> FilenameConvention:
        ...

    def main(self,**kwargs):

        self.tags = kwargs.get("tags",["See Examples","ticket","Name","Dept","Vendor"])
        
        self.setExample()

        self.tagVis = []
        self.nameSliceVis = []
        self.delimitorVis_A = []
        self.delimitorVis_B = []

    def generate_id(self,**kwargs):

        with dpg.group() as self._id:

            self.delimInput = dpg.add_combo(label="Delimitor",items=self.delimitors,default_value = self.delimitors[0],callback=self.updateDels,width=70)
            self.fieldSetter = dpg.add_input_int(
                label="Specify Naming Segments", # OR Add column before index
                default_value=len(self.name_slices),
                callback=self.changeFields,
                on_enter =True,
                min_value=1,min_clamped =True,
                width=70)


            dpg.add_separator()
            #with dpg.child_window():
            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_text("Filename Convention:")
                    dpg.add_text("Informs which Tag?::")
                with dpg.group() as self.fieldsParent:
                    #names
                    self.populateFields()
                with dpg.group():
                    #dpg.add_listbox(label="Extensions",items=[".csv",".xlsx"])
                    _ = dpg.add_button(label=".XXX",callback=self.manageExt)
                    with dpg.tooltip(_,hide_on_activity=False): dpg.add_text("Manage Extensions")
                    self._tagNote = dpg.add_text("Default Example Tags will be cleared upon entering of tags in the below columns.")
            with dpg.group(horizontal=True):
                dpg.add_text("Example             :")
                self.exampleVis = dpg.add_input_text(enabled=False,default_value=self.example)
            
    def setExample(self):

        self.example = ""
        for i,x in enumerate(self.name_slices):
            self.example += f'{{{x}}}'
            if x!=self.name_slices[-1]:
                self.example+=f'{self.delimitor}'
            else:

                if list(self.supported_extensions.values()).count(False) == len(self.supported_extensions.items()):
                    self.example+=f'.??? *No extensions selected!*****'
                else:
                    for ext,val in self.supported_extensions.items():
                        if val:
                            self.example+=f'.{ext}'
                            if ext!=list(self.supported_extensions.items())[-1]:
                                self.example+=f' \\ '


    def attemptToSave(self):

        def save():

            _supp = []

            for key,val in self.supported_extensions.items():
                if val: _supp.append(key)

            _new = FilenameConvention(
                slices=dpg.get_values(self.nameSliceVis),
                tags=dpg.get_values(self.tagVis),
                delim=dpg.get_value(self.delimInput),
                supported_extensions=_supp
                )

            return _new

        if supported_extensions.values().count(False)==len(self.supported_extensions.items):
            with dpg.window(popup=True):
                dpg.add_text("No extensions selected in the filename convention editor. Please check at least one")
        else:
            _ = save()
        
        return _

    def changeSlices(self,sender,app_data):

        def add_sliceToEnd(self,columnId):
            ...

        def delete_sliceFromEnd(self,columnId):
            ...
           

        # Adding Columns
        if app_data > len(self.name_slices):
            for sliceIndex in range(len(self.name_slices),app_data):
                add_sliceToEnd(self)
             
        # Subtracting Columns
        elif app_data < self.numColumns:
            for sliceIndex in range(app_data,len(self.name_slices)):
                delete_sliceFromEnd(self)

        self.numColumns = app_data


    def manageExt(self,sender):
        
        def setVal(sender,app_data,user_data):

            print(self.supported_extensions)
            self.supported_extensions[dpg.get_item_label(sender)]=app_data
            print(self.supported_extensions)
            self.setExample()
            dpg.configure_item(self.exampleVis,default_value=self.example)

        with dpg.window(popup=True):
            for ext,val in self.supported_extensions.items():
                dpg.add_checkbox(label=ext,default_value=val,callback=setVal)

    def populateFields(self):
        with dpg.group(horizontal=True):
                
            for name in self.name_slices:
                #with dpg.group():

                _width = len(name)*8

                _nms = dpg.add_input_text(default_value=name,width=_width,callback=self.resize)
                self.nameSliceVis.append(_nms)
                       
                #with dpg.group():
                if name != self.name_slices[-1]:
                    _del = dpg.add_text(self.delimitors[0])
                    self.delimitorVis_A.append(_del)

        #tag dropdowns
        with dpg.group(horizontal=True):
                
            for i,name in enumerate(self.name_slices):
                with dpg.group(horizontal=True):
                    _width = dpg.get_item_width(self.nameSliceVis[i])
                    _tv = dpg.add_combo(width=_width,items=self.tags,callback=self.checkTags,default_value=self.tags[0])
                    self.tagVis.append(_tv)

                    if name != self.name_slices[-1]:
                        _del = dpg.add_text(self.delimitors[0])
                        self.delimitorVis_B.append(_del)

    def resize(self,sender,app_data,user_data):
        
        _width = len(app_data)*8
        if _width < 40: _width = 40
        _index = self.nameSliceVis.index(sender)

        for item in [self.nameSliceVis[_index] , self.tagVis[_index]]:
            dpg.configure_item(item,width=_width)

        self.name_slices[_index]=app_data
            

        self.setExample()
        dpg.configure_item(self.exampleVis,default_value=self.example)

    def updateDels(self,sender,app_data,user_data):

        for item in self.delimitorVis_A+self.delimitorVis_B:
            dpg.configure_item(item,default_value=app_data)

        self.delimitor = app_data

        self.setExample()
        dpg.configure_item(self.exampleVis,default_value=self.example)

    def checkTags(self,sender,app_data,user_data):
        
        if app_data=='': return

        _alreadyChecked = False
        for item in self.tagVis:

            if item == sender: continue

            if dpg.get_value(item)==app_data:
                _alreadyChecked=True
                break

        if _alreadyChecked:
            with dpg.window(popup=True):
                dpg.add_text(f"Tag selection '{app_data}' already chosen by another naming slice.")
                dpg.configure_item(sender,default_value='')

    def updateTagList(self,items):

        dpg.configure_item(self._tagNote,show=False)

        _newTags = items
        for tagSelector in self.tagVis:
            #_currentIndex = self.tags.index(dpg.get_value(tagSelector))
            dpg.configure_item(tagSelector,items=_newTags,default_value='')
