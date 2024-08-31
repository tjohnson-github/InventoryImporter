
from dataclasses import dataclass,field
from dearpygui import dearpygui as dpg
from Color_Manager import randomColor

from DPGStage import DPGStage

@dataclass
class Rubric:
    name                        :   str     =   field(default="")
    description                 :   str     =   field(default="")
    color                       :   tuple   =   field(default_factory=lambda: randomColor())
    col_to_tag_correspondence   :   dict    =   field(default_factory=lambda: {})
    editorNames                 :   list    =   field(default_factory=lambda: [])
    editorTags                  :   list    =   field(default_factory=lambda: [])

    #dateAdded : str
    #dateEdited: str

# The connection between these two classes can be modified such that:
#   each field can have its own input /display suite
#       metadata in the field can signify:
#        -  whether or not it has/needs a suite
#        -  whether or not its a field that is mandatory ... can mix with optional?
#        -  what the callback should be 
#        - 
#        - 





class RubricDisplayForSchema(DPGStage):

    height = 50

    def main(self,**kwargs):

        self.rubric = kwargs.get("rubric")

    def generate_id(self,**kwargs):

        openEditor: callable = kwargs.get("openEditor",None)
        deleteRubric:callable = kwargs.get("deleteRubric",None)

        with dpg.group(horizontal=True) as self._id:

            dpg.add_color_button(label=f"{self.rubric.name}'s Color",default_value=self.rubric.color,height=16,width=50)

            with dpg.group():

                _= dpg.add_input_text(
                    label="Name",
                    default_value=self.rubric.name,
                    enabled=False,
                    width=130)

                if self.rubric.description:
                    with dpg.tooltip(_):
                        dpg.add_text(self.rubric.description)

            dpg.add_button(
                label="Edit",
                callback=openEditor,
                user_data=self.rubric)

            dpg.add_spacer(width=6)

            dpg.add_button(
                label="X",
                callback=deleteRubric,
                user_data=self.rubric)


from typing import Any
class StageFilter:

    object: Any
    filter = {
        }
    
    def __init__(self,object,requested="Normal"):

        self.filter[requested](object)


class RubricFilter(StageFilter):
    filter = {
        "forSchema": RubricDisplayForSchema,

        }