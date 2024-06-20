

from DPGStage import DPGStage
import dearpygui.dearpygui as dpg
from dataclasses import dataclass,field,asdict

def setFixer(iterable):
    return list(set(iterable))


@dataclass
class FilenameConvention:
    # this means that:
    #   when scanning a folder OR when using a rubric
    #   files that:
    #       match the extension
    #       AND match the naming convention
    #   will get picked up.
    # 
    #   If the EXTENSIONS match, AND the filename convention Matches
    #   BUT it does not exist in the rubric:
    #       >>>> give user an option to add it. <<<<


    # Slices can have a lot of fields.
    # When importing: all field names will be displayed as TOOLTIPS
    # FOr every tag that is empty: ignore
    # FOr every tag that exists: IMMEDIATELY POPULATE THAT VALUE INTO THE TABLE BELOW UNDER THAT COLUMN: 
    #   AND SHOW IF IT WILL BE BY ITSELF, OR OPERATED UPON
    #   LET THEM ADDITIONALLY FORMAT IT


    slices: list[str] = field(default_factory=lambda: ["Ticket#","Example Name","Example Department"]) # v        be      dimensionality v
    tags: list[str] = field(default_factory=lambda: ['','',''])  # ^ should    same                ^

    delim: str = "_"
    supported_extensions: list[str] = field(default_factory=lambda: [])

    def saveToSpreadsheet(self):
        ...


class FilenameExtractorManager(DPGStage):
    height=220

    extractors: list = []
    extractorTabs: list = []

    disabled=False

    def main(self,**kwargs):

        self.editor = kwargs.get("editor")
        self.conventions = kwargs.get("filenameConventions")

    def generate_id(self,**kwargs):
        
        _color = kwargs.get("color")

        with dpg.child_window(border=False,height=self.height) as self._id:
            with dpg.group(horizontal=True):

                self.color = dpg.add_color_button(height=self.height-30,width=30,default_value=_color)

                with dpg.group():

                    self.doNOtUse = dpg.add_checkbox(label="Do not Use Naming Convention Extraction",default_value=self.disabled,callback=self.hide)
                    with dpg.tooltip(self.doNOtUse):
                        dpg.add_text("If used, the program will aid you in relaying what a given input file's name means and can benefit from TAGs.")
                        dpg.add_text("If unused, file scanning pre-load no TAGGED information ")
                    dpg.add_separator()

                    with dpg.child_window(border=False,height=190,horizontal_scrollbar=True) as self.tobeHidden:
                        
                        with dpg.tab_bar() as self.tabBar:

                            for i,fnc in enumerate(self.conventions):

                                with dpg.tab(label=f"Convention {i+1}") as _tab:
                                    
                                    _fns = FilenameExtractor(editor=self.editor,filenameConvention=fnc)
                                    self.extractors.append(_fns)

                                self.extractorTabs.append(_tab)

                            _new = dpg.add_tab_button(label='+',callback=self.addNew)
                            self.extractorTabs.append(_new)

        if self.conventions == []: 
            self.disabled = True
            dpg.configure_item(self.doNOtUse,default_value=self.disabled)
            self.hide(sender=None,app_data=dpg.get_value(self.doNOtUse))
        else:
            self.disabled = False
            try:
                self.editor.schemaLoader.colEditor.updateTags()
            except Exception as e:
                print(f'schemaLoader DNE')

    def addNew(self):

        # Reset all ----------------------------
        #print(self.extractorTabs)

        for tab in self.extractorTabs:
            dpg.delete_item(tab)

        self.extractorTabs = []
        self.extractors = []

        # Create New Convention ----------------------------
        _con = FilenameConvention()
        self.conventions.append(_con)

        # Iterate over conventions; give each an extractor ------------
        dpg.push_container_stack(self.tabBar)
        for i,fnc in enumerate(self.conventions):

            with dpg.tab(label=f"Convention {i+1}") as _tab:
                                    
                _fns = FilenameExtractor(editor=self.editor,filenameConvention=fnc)
                self.extractors.append(_fns)

            self.extractorTabs.append(_tab)

        _new = dpg.add_tab_button(label='+',callback=self.addNew)
        self.extractorTabs.append(_new)
        
        self.editor.schemaLoader.colEditor.updateTags()

    def hide(self,sender,app_data):

        dpg.configure_item(self.tobeHidden,show=not app_data)
        dpg.configure_item(self.color,height = self.height-30 if not app_data else 30)
        dpg.configure_item(self._id,height = self.height if not app_data else 35)

        if self.conventions==[] and not app_data:
            pass

            try:
                self.addNew()
                # and request new tags
                #self.editor.schemaLoader.colEditor.updateTags()
            except Exception as e:
                print(e)

    def getTags(self):
        _allTags = []

        for extractor in self.extractors:
            _allTags.extend(extractor.tagVis)

        return _allTags

    def updateTagList(self,items):
        
        for extractor in self.extractors:
            print(extractor.convention.slices)
            extractor.updateTagList(items)

    def attemptToSave(self):

        _fnsConventions = []

        for extractor in self.extractors:
            _fnsConventions.append(extractor.attemptToSave())

        return _fnsConventions

class FilenameExtractor(DPGStage):

    cell_height = 80
    height=190

    delimitors = ["_","^"]
    #delimitor = "_"
    #name_slices = ["Ticket#","Example Name","Example Department"]

    supported_extensions = {"xlsx":True,"csv":True}
    disabled:bool
    delimitorVis: list[int]

    default_option = "~"

    # administrative
    def main(self,**kwargs):

        self.editor = kwargs.get("editor")
        self.convention = kwargs.get("filenameConvention")
        self.availTags = [self.default_option] #+ self.convention.tags

    def generate_id(self,**kwargs):

        self._tagNote1 = dpg.add_text("\tNote: All slices and tags seen below are example placeholders")

        dpg.add_separator()

        self.delimInput = dpg.add_combo(label="Delimitor",items=self.delimitors,default_value = self.convention.delim,callback=self.updateDels,width=70)
        self.fieldSetter = dpg.add_input_int(
            label="Specify Naming Segments", # OR Add column before index
            default_value=len(self.convention.slices),
            callback=self.changeNumSlices,
            on_enter =True,
            min_value=1,min_clamped =True,
            width=70)

        dpg.add_separator()

        with dpg.group(horizontal=True):
            with dpg.group():
                _fnc = dpg.add_text("Filename Convention:")
                with dpg.tooltip(_fnc):
                    dpg.add_text("Slices will be read from the -> LEFT -> , so files may contain any number of additional slices. But only what is here will be visible to the program.")
                _tag= dpg.add_text("Informs which Tag?::")
                with dpg.tooltip(_tag):
                    dpg.add_text("If a given named slice has a TAG specified (one made in the column editor) then, when loading that file, it will stage that value for manipulation in that column.")

            with dpg.group() as self.fieldsParent:
                self.populateFields()
            with dpg.group():
                _ = dpg.add_button(label=".XXX",callback=self.manageExtensions)
                with dpg.tooltip(_,hide_on_activity=False): dpg.add_text("Manage Extensions")
                self._tagNote2 = dpg.add_text("Default Example Tags will be cleared upon entering of tags in the below columns.")
        with dpg.group(horizontal=True):
            dpg.add_text("Example            :")
            self.exampleVis = dpg.add_input_text(enabled=False)
            self.setExample()

    # dpg field changes            
    def populateFields(self):

        # Main iterator (similar to regenerateMoments)

        self.tagVis = []
        self.nameSliceVis = []
        self.delimitorVis_A = []
        self.delimitorVis_B = []

        with dpg.group(horizontal=True) as self.nameSliceWindow:
                
            for i,name in enumerate(self.convention.slices):

                _width = len(name)*10 if len(name)>0 else 24
                _width+=20

                _nms = dpg.add_input_text(default_value=name,width=_width,callback=self.resize)
                self.nameSliceVis.append(_nms)
                       
                if i != len(self.convention.slices):
                    _del = dpg.add_text(self.convention.delim)
                    self.delimitorVis_A.append(_del)

        #tag dropdowns
        with dpg.group(horizontal=True) as self.dropdownWindow:
                
            for i,name in enumerate(self.convention.slices):

                try: # to format ~/_/Tag
                    _df_tag = self.convention.tags[i]
                    if _df_tag == "": 
                        _df_tag = self.default_option
                except Exception as e:
                    print(f'From Populate: {error = }')
                    _df_tag = self.default_option


                with dpg.group(horizontal=True):
                    _width = dpg.get_item_width(self.nameSliceVis[i])
                    _tv = dpg.add_combo(width=_width,items=self.availTags,callback=self.checkTags,default_value=_df_tag)
                    self.tagVis.append(_tv)

                    if i != len(self.convention.slices):
                        _del = dpg.add_text(self.convention.delim)
                        self.delimitorVis_B.append(_del)

        dpg.delete_item(self.delimitorVis_A[-1])
        dpg.delete_item(self.delimitorVis_B[-1])
        self.delimitorVis_A = self.delimitorVis_A[:-1]
        self.delimitorVis_B = self.delimitorVis_B[:-1]

    def setExample(self):

        self.example = ""
        for i,x in enumerate(self.convention.slices):
            self.example += f'{{{x}}}'
            if i!=len(self.convention.slices)-1:
                self.example+=f'{self.convention.delim}'
            else:

                if list(self.supported_extensions.values()).count(False) == len(self.supported_extensions.items()):
                    self.example+=f'.??? *No extensions selected!*****'
                else:
                    for ext,val in self.supported_extensions.items():
                        if val:
                            self.example+=f'.{ext}'
                            if ext!=list(self.supported_extensions.items())[-1]:
                                self.example+=f' \\ '

        dpg.configure_item(self.exampleVis,default_value=self.example)


    def resize(self,sender,app_data,user_data):
        #
        # Resizes the input fields based on length of input
        #
        _width = len(app_data)*8
        if _width < 40: _width = 40
        _index = self.nameSliceVis.index(sender)

        for item in [self.nameSliceVis[_index] , self.tagVis[_index]]:
            dpg.configure_item(item,width=_width)

        self.convention.slices[_index]=app_data
           
        self.setExample()

    def changeNumSlices(self,sender,app_data):
        #
        # Adds new fields to be extracted from 
        #
        def add_sliceToEnd(self):
            self.convention.slices.append("")
            self.convention.tags.append(self.default_option)

        def delete_sliceFromEnd(self):
            self.convention.slices=self.convention.slices[:-1]
            self.convention.tags = self.convention.tags[:-1]
           
        # Adding Columns
        if app_data > len(self.convention.slices):
            #for sliceIndex in range(len(self.name_slices),app_data):
            add_sliceToEnd(self)
             
        # Subtracting Columns
        elif app_data < len(self.convention.slices):
            #for sliceIndex in range(app_data,len(self.name_slices)):
            delete_sliceFromEnd(self)

        dpg.delete_item(self.fieldsParent,children_only=True)
        dpg.push_container_stack(self.fieldsParent)
        self.populateFields()
        self.setExample()


    def manageExtensions(self,sender):
        
        def setVal(sender,app_data,user_data):

            print(self.supported_extensions)
            self.supported_extensions[dpg.get_item_label(sender)]=app_data
            print(self.supported_extensions)
            self.setExample()
            dpg.configure_item(self.exampleVis,default_value=self.example)

        with dpg.window(popup=True):
            for ext,val in self.supported_extensions.items():
                dpg.add_checkbox(label=ext,default_value=val,callback=setVal)

    def updateDels(self,sender,app_data,user_data):

        for item in self.delimitorVis_A+self.delimitorVis_B:
            try:
                dpg.configure_item(item,default_value=app_data)
            except:
                print(self.delimitorVis_A+self.delimitorVis_B)

        self.convention.delim = app_data

        self.setExample()
        #dpg.configure_item(self.exampleVis,default_value=self.example)

    def checkTags(self,sender,app_data,user_data):
        
        # General callback for the tag dropdown

        if app_data=='' or app_data==self.default_option: return

        _alreadyChecked = False
        for item in self.tagVis + self.editor.dns.tagVis:

            if item == sender: continue

            if dpg.get_value(item)==app_data:
                _alreadyChecked=True
                break

        if _alreadyChecked:
            with dpg.window(popup=True):
                dpg.add_text(f"Tag selection '{app_data}' already chosen by another naming slice.")
                dpg.configure_item(sender,default_value=self.default_option)
            return
        else:
            self.convention.tags[self.tagVis.index(sender)] = app_data
    
        #self.editor.schemaEditor.colEditor.notifyDerived(tagName=app_data)

    def updateTagList(self,items):

        print(f"GETTING ITEMS FOR FILENAME:: {items}")
        dpg.configure_item(self._tagNote1,show=False)
        dpg.configure_item(self._tagNote2,show=False)

        # get unique elements
        # add the placeholder
        _newTags = [self.default_option]+[x.rstrip() for x in items]
        print(f'{self.availTags=}')

        #if len(_newTags)!=len(self.availTags):


        for i,tagSelector in enumerate(self.tagVis):

            try: # to format ~/_/Tag
                _df_tag = self.convention.tags[i]
                if _df_tag == "": 
                    _df_tag = self.default_option
                elif _df_tag not in _newTags:

                    _df_tag = self.default_option
                    self.convention.tags[i] = _df_tag

                    with dpg.window(popup=True):
                        dpg.add_text(f"TAG changed in a Filename Convention Extractor, Slice #{i+1}")

                    '''if len(_newTags)!=len(self.availTags):
                        _df_tag = self.default_option
                    else:
                        _df_tag = _newTags[self.availTags.index(_df_tag)]
                        self.convention.tags[i] = _df_tag'''

            except Exception as e:
                print(f'From updateTagList: {e = }')
                _df_tag = self.default_option

            dpg.configure_item(tagSelector,items=_newTags,default_value=_df_tag)
        
        self.availTags = _newTags


    # loading and saving
    def load_from_spreadsheet(self) -> FilenameConvention:
        ...

    def attemptToSave(self):

        def save():

            _supp = []

            for key,val in self.supported_extensions.items():
                if val: _supp.append(key)

            _tags = dpg.get_values(self.tagVis)
            print(f'{_tags=}')
            for i,x in enumerate(_tags):
                if x == self.default_option: 
                    _tags[i] = ""

            _new = FilenameConvention(
                slices  =   dpg.get_values(self.nameSliceVis),
                tags    =   _tags,
                delim   =   dpg.get_value(self.delimInput),
                supported_extensions=_supp
                )

            return _new

        if list(self.supported_extensions.values()).count(False)==len(self.supported_extensions.items()):
            with dpg.window(popup=True):
                dpg.add_text("No extensions selected in the filename convention editor. Please check at least one")
                _=None
        else:
            _ = save()
        
        return _

    

    

    
    

    