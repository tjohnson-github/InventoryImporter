

from DPGStage import DPGStage
import dearpygui.dearpygui as dpg
from dataclasses import dataclass,field,asdict
from DefaultPathing import DefaultPathing,DefaultPaths
from Directory_Selector import DirectorySelector

def setFixer(iterable):
    return list(set(iterable))

@dataclass
class DirnameConvention:

    path: str = field(default_factory=lambda: DefaultPathing.getPaths().input) 
    slices: list[str] = field(default_factory=lambda: ["Source ID","Operation Type","Example"]) # v        be      dimensionality v
    tags: list[str] = field(default_factory=lambda: ['','',''])   # ^ should    same                ^

    delim: str = "_"



    def saveToSpreadsheet(self):
        ...


class DirnameExtractor(DPGStage):

    cell_height = 80
    height=190

    delimitors = ["_","^"]
    default_option = '~'
    #delimitor = "_"
    delimitorVis: list[int]

    #name_slices = ["Source ID","Operation Type","Example"]

    disabled:bool
    absent: bool = False

    label = "Directory Naming Convention Extraction"
    scans = "directories"

    pathIsDefault = True

    def main(self,**kwargs):

        # if tutorial, use this list, else, use []
        #self.availTags = kwargs.get("tags",["~"])
        self.editor = kwargs.get("editor")

        self.convention = kwargs.get("dirnameConvention")

        if not self.convention: 
            self.absent = True
            self.convention = DirnameConvention()

        print (f'{self.convention.tags}')

        self.availTags = [self.default_option] + self.convention.tags


    def generate_id(self,**kwargs):

        _color = kwargs.get("color")
        with dpg.child_window(border=False,height=self.height) as self._id:
            with dpg.group(horizontal=True):

                self.color = dpg.add_color_button(height=self.height-30,width=30,default_value=_color,enabled=False)

                with dpg.group():

                    self.doNOtUse = dpg.add_checkbox(label=f"Do not Use {self.label}",default_value=False,callback=self.hide)
                    with dpg.tooltip(self.doNOtUse):
                        dpg.add_text("If used, the program will aid you in relaying what a given input file's SCAN LOCATION means and can benefit from TAGs.")
                        dpg.add_text("If unused, file scanning pre-load no TAGGED information from the DIRECTORY")
                    dpg.add_separator()

                    with dpg.child_window(border=False,height=160,horizontal_scrollbar=True) as self.tobeHidden:

                        dpg.add_separator()
                        with dpg.group(horizontal=True):

                            #paths = DefaultPathing.getPaths()
                            _default_path = getattr(self.convention,"path")#,DefaultPathing.getPaths().input)

                            self.pathInput = dpg.add_input_text(default_value = _default_path,enabled=False,width=550)
                            dpg.add_button(label="Specify New Path",callback=self.newPath)
                            dpg.add_spacer(width=50)
                            def reset():
                                dpg.configure_item(self.pathInput,default_value=DefaultPathing.getPaths().input)
                                self.pathIsDefault=True
                            dpg.add_button(label="-Reset-",callback=reset)
                        dpg.add_text("Reminder: You can specify a unique filepath without specifying convention tags. Just ignore the following:",bullet=True)

                        dpg.add_separator()
                        #with dpg.group() as :
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
                        #with dpg.child_window():
                        with dpg.group(horizontal=True):
                            with dpg.group():
                                _fnc = dpg.add_text("Dirname Convention:")
                                with dpg.tooltip(_fnc):
                                    dpg.add_text(f"Slices will be read from the -> LEFT -> , so {self.scans} may contain any number of additional slices. But only what is here will be visible to the program.")
                                _tag= dpg.add_text("Informs which Tag?::")
                                with dpg.tooltip(_tag):
                                    dpg.add_text("If a given named slice has a TAG specified (one made in the column editor) then, when loading from that directory, it will stage that value for manipulation in that column.")

                            with dpg.group() as self.fieldsParent:
                                #names
                                self.populateFields()
                            
                        with dpg.group(horizontal=True):
                            dpg.add_text("Example            :")
                            self.exampleVis = dpg.add_input_text(enabled=False)
                            self.setExample()
        
        if self.absent:

            dpg.configure_item(self.doNOtUse,default_value=True)
            self.hide(sender=self.doNOtUse,app_data=dpg.get_value(self.doNOtUse))

    def hide(self,sender,app_data):

        #self.editor.schemaEditor.colEditor.disableFilename(disabledState=app_data)

        dpg.configure_item(self.tobeHidden,show=not app_data)
        dpg.configure_item(self.color,height = self.height-30 if not app_data else 30)
        dpg.configure_item(self._id,height = self.height if not app_data else 35)

    def newPath(self):

        def updatePath(sender,app_data,user_data):

            _chosen = user_data

            if _chosen !=DefaultPathing.getPaths().input:
                self.pathIsDefault = False
            else:
                # IDK why someone would re-select the default, but here's the contingency lol.
                self.pathIsDefault = True

            dpg.configure_item(self.pathInput,default_value=_chosen)

        DirectorySelector(nextStage = updatePath, label="Choose new file for this Directory Convention")


    # dpg field changes            
    def populateFields(self):

        # Main iterator (similar to regenerateMoments)

        self.tagVis = []
        self.nameSliceVis = []
        self.delimitorVis_A = []
        self.delimitorVis_B = []

        with dpg.group(horizontal=True) as self.nameSliceWindow:
                
      
            for i,name in enumerate(self.convention.slices):
                #with dpg.group():
                
                _width = len(name)*10 if len(name)>0 else 24
                _width+=20

                _nms = dpg.add_input_text(default_value=name,width=_width,callback=self.resize)
                self.nameSliceVis.append(_nms)
                       
                #with dpg.group():
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
                    print(e)
                    _df_tag = self.default_option

                with dpg.group(horizontal=True):
                    _width = dpg.get_item_width(self.nameSliceVis[i])
                    #print(f"{_df_tag=}")
                    _tv = dpg.add_combo(width=_width,items=self.availTags,callback=self.checkTags,default_value=_df_tag)
                    self.tagVis.append(_tv)

                    if i != len(self.convention.slices):
                        _del = dpg.add_text(self.convention.delim)
                        self.delimitorVis_B.append(_del)

        dpg.delete_item(self.delimitorVis_A[-1])
        dpg.delete_item(self.delimitorVis_B[-1])
        self.delimitorVis_A = self.delimitorVis_A[:-1]
        self.delimitorVis_B = self.delimitorVis_B[:-1]
        #self.setExample()

    def setExample(self):

        self.example = ""
        for i,x in enumerate(self.convention.slices):
            self.example += f'{{{x}}}'
            if i!=len(self.convention.slices)-1:
                self.example+=f'{self.convention.delim}'
        
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
        #dpg.configure_item(self.exampleVis,default_value=self.example)

    def changeNumSlices(self,sender,app_data):
        #
        # Adds new fields to be extracted from 
        #
        def add_sliceToEnd(self):
            self.convention.slices.append("")
            self.convention.tags.append(self.default_option)

        def delete_sliceFromEnd(self):
            self.convention.slices  =   self.convention.slices[:-1]
            self.convention.tags    =   self.convention.tags[:-1]
           
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


    def updateDels(self,sender,app_data,user_data):

        # Updates both sets of delimitors with the new choice

        for item in self.delimitorVis_A+self.delimitorVis_B:
            try:
                dpg.configure_item(item,default_value=app_data)
            except:
                #print(item)
                print(self.delimitorVis_A+self.delimitorVis_B)

        self.convention.delim = app_data

        self.setExample()
        #dpg.configure_item(self.exampleVis,default_value=self.example)

    def checkTags(self,sender,app_data,user_data):
        
        # General callback for the tag dropdown

        if app_data=='' or app_data==self.default_option: return

        _alreadyChecked = False

        _allFNSTags = self.editor.fns.getTags()


        for item in self.tagVis + _allFNSTags:

            if item == sender: continue

            if dpg.get_value(item)==app_data:
                _alreadyChecked=True
                break

        if _alreadyChecked:
            with dpg.window(popup=True):
                dpg.add_text(f"Tag selection '{app_data}' already chosen by another naming slice.")
                dpg.configure_item(sender,default_value='')
            return
        else:
            self.convention.tags[self.tagVis.index(sender)] = app_data

        #self.editor.schemaEditor.colEditor.notifyDerived(tagName=app_data)

    def updateTagList(self,items):

        dpg.configure_item(self._tagNote1,show=False)
        #print(f"GETTING ITEMS FOR DIRNAME:: {items}")
        # get unique elements
        #minItems = list(set(items))
        # add the placeholder
        _newTags = [self.default_option]+items

        for i,tagSelector in enumerate(self.tagVis):

            try: # to format ~/_/Tag
                _df_tag = self.convention.tags[i]
                if _df_tag == "": 
                    _df_tag = self.default_option
                elif _df_tag not in _newTags:

                    _df_tag = self.default_option
                    self.convention.tags[i] = _df_tag

                    with dpg.window(popup=True):
                        dpg.add_text(f"TAG changed in Directory Convention Extractor Slice #{i+1}")


                    #_df_tag = _newTags[self.availTags.index(_df_tag)]
                    #self.convention.tags[i] = _df_tag
            except Exception as e:
                print(e)
                _df_tag = self.default_option

            

            dpg.configure_item(tagSelector,items=_newTags,default_value=_df_tag)

        self.availTags = _newTags


    # loading and saving
    def load_from_spreadsheet(self):
        ...

    def attemptToSave(self):

        def save():

            _supp = []

            _tags = dpg.get_values(self.tagVis)
            for i,x in enumerate(_tags):
                if x == self.default_option: 
                    _tags[i] = ""

            _new = DirnameConvention(
                path    =   dpg.get_value(self.pathInput),
                slices  =   dpg.get_values(self.nameSliceVis),
                tags    =   _tags,
                delim   =   dpg.get_value(self.delimInput),
                )

            #print(asdict(_new))

            return _new

       
        if dpg.get_value(self.doNOtUse):
            print("No DIRNAME CONVENTIONS used")
            _ = None
        else:
            print("Saving DIRNAME")
            _ = save()
        
        return _
