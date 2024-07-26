
from DPGStage import DPGStage
from dearpygui import dearpygui as dpg
from File_Operations import csv_to_list,excel_to_list,mkdirWrapper
from File_Selector import FileSelector

#from Schema import Schema

from Color_Manager import randomColor


class LinkRubricToSchema(DPGStage):  #SchemaRubricZipper
 
    label="Test Adding a Rubric"

    height = 500
    width=1000

    #schema: Schema

    names: list[str]
    items: list[int]

    null_item = '~'

    def main(self,**kwargs):

        self.schema=kwargs.get("schema")
        self.allSupportedinputTypes = []
        if self.schema.filenameConventions:
            for fnc in self.schema.filenameConventions:
                self.allSupportedinputTypes.extend(fnc.supported_extensions)
        
        # TAGS
        _uncleanedTags = self.schema.outputSchemaDict["Tag"]
        _cleanedTags = [t for t in _uncleanedTags if t!=""]
        self.tags = _cleanedTags
        self.tags.insert(0,self.null_item)

        _necessary = self.schema.outputSchemaDict["Necessary?"]
        print (zip(_uncleanedTags,_necessary))

    def generate_id(self,**kwargs):

        with dpg.window(height=self.height,width=self.width,label=self.label):

             self.generateCells()
             #"Column Name",
             #"Tag",
             #"Necessary?",
             #"Derived from Filename?",
             #"Operations",

    def changeColor(self,sender,app_data):
        
        def propColors(sender,app_data):

            _newColor = tuple(i*255 for i in app_data)
            dpg.configure_item(self.color,default_value=_newColor)

        with dpg.window(popup=True):
            dpg.add_color_picker(
                no_small_preview=False,
                no_side_preview = True,
                callback=propColors)

    def generateCells(self):
        
        with dpg.group(horizontal=True):
            dpg.add_text("Adding an Input File to the Rubric: ")
            dpg.add_input_text(default_value=self.schema.name,enabled=False)
        dpg.add_separator

        with dpg.group(horizontal=True):
            with dpg.group():
                with dpg.group(horizontal=True):
                    self.nameInput = dpg.add_input_text(label="Name of Rubric",width=150)
                    dpg.add_text("*",color=(255,0,0))
                self.desc = dpg.add_input_text(label="Description",width=150,height=80,multiline=True)
                with dpg.group(horizontal=True):
                    _c = dpg.add_color_button(width=50,default_value=self.schema.color,enabled=False)
                    with dpg.tooltip(_c): dpg.add_text(f"{self.schema.name}'s Color")
                    self.color = dpg.add_color_button(width=92,default_value=randomColor(),callback=self.changeColor)
                    with dpg.tooltip(self.color): dpg.add_text(f"This Rubric's Color")
                    dpg.add_text("Color")
            with dpg.group():
                dpg.add_button(label="Save",callback=self.addRubricToSchema)
            #self.scansFrom = dpg.add_combo(label="Scans From",items = self.scannableLocations,default_value=self.scannableLocations[0],width=300)
        dpg.add_separator()
        #===============================================
        # Display DirnameConvention here
        #   does the imported file come from this dirname? y/n
        if self.schema.dirnameConvention:
            dpg.add_text("DirnameConvention Found!")
        else:
            dpg.add_text("No Dirname Convention used in this Schema")

        #===============================================
        dpg.add_separator()
        # Display Filenme Convention:
        #   based on filename: show its breakdown into the tag list:
        if self.schema.filenameConventions:
            dpg.add_text(f"{len(self.schema.filenameConventions)} FilenameConventions Found!")
        else:
            dpg.add_text("No Filename Conventions used in this Schema")

        #===============================================
        dpg.add_separator()

        #dpg.add_combo(items=self.tags)
        self.suggest = dpg.add_checkbox(label="Suggest Tags based on Input?",default_value=True)
        dpg.add_separator

        dpg.add_button(label="Load File",callback=self.loadFile) 
        dpg.add_button(label="Build Input File Schema")
        
        # can also build from scratch like before:::
        # make a decoupled column editor??
        dpg.add_separator()
        
        with dpg.child_window(border=False,horizontal_scrollbar=True) as self.rubricEditor:
            pass

    def addRubricToSchema(self):

        _names = dpg.get_values(self.names)
        _items = dpg.get_values(self.items)
        print("<><><><><><><>")
        print(_names)
        print(_items)
        print("<><><><><><><>")
        for x in _items:
            if x==self.null_item: x = "" 

        _col_to_tag_correspondence = dict(zip(self.names,_items))

        print(_col_to_tag_correspondence)

        _rubric = Rubric(
            name        =   dpg.get_value(self.nameInput),
            description =   dpg.get_value(self.desc),
            color       =   dpg.get_value(self.color),
            col_to_tag_correspondence = _col_to_tag_correspondence
            )

        self.schema.rubrics.update({_rubric.name:_rubric})

    def loadFile(self):

        def manipulateFile():

            dpg.delete_item(self.fs._id)
            _filepath = self.fs.selectedFile 

            readArray = []
            error = ''

            if _filepath[-3:] == 'csv':
                readArray,error = csv_to_list(_filepath)
            elif _filepath[-4:] == 'xlsx':
                readArray,error = excel_to_list(_filepath)

            if readArray:
                self.populateCols(readArray)
           
            else:
                with dpg.window(popup=True):
                    dpg.add_text(error)


        if self.allSupportedinputTypes:
            self.fs = FileSelector(
                label="Load Spreadsheet file to begin column correspondence with desired output schema",
                nextStage=manipulateFile,
                inputTypes = self.allSupportedinputTypes)
        else:
            self.fs = FileSelector(
                label="Load Spreadsheet file to begin column correspondence with desired output schema",
                nextStage=manipulateFile)

  
    def populateCols(self,readArray):

        header = readArray.pop(0)    
        rows = readArray
            
        dpg.push_container_stack(self.rubricEditor)

        with dpg.group(horizontal=True) as headerGroup:
            dpg.add_text("Imported File Header:")
            dpg.add_spacer(width=20)
            dpg.add_text("|")

        with dpg.group(horizontal=True) as TagGroup:
            dpg.add_text("Available Tags ::::::")
            dpg.add_spacer(width=20)
            dpg.add_text("|")

        self.names = []
        self.items = []

        for colName in header:

            component_width=8*len(f"{colName}")
            if component_width < 50: component_width+=40
            
            _name = dpg.add_input_text(default_value=f"{colName}", readonly=True,parent=headerGroup,width=component_width)
            self.names.append(_name)

            with dpg.group(horizontal=True,parent=headerGroup):
                dpg.add_spacer(width=20)
                dpg.add_text("|")
                dpg.add_spacer(width=20)

            default_tag = self.tags[0]

            if self.suggest:
                if colName in self.tags:
                    default_tag = self.tags[self.tags.index(colName)]
                else:
                    pass
                    # do other suggest mechanics here
    
            _combo = dpg.add_combo(items=self.tags,default_value = default_tag,parent=TagGroup,width=component_width)
            self.items.append(_combo)

            with dpg.group(horizontal=True,parent=TagGroup):
                dpg.add_spacer(width=20)
                dpg.add_text("|")
                dpg.add_spacer(width=20)