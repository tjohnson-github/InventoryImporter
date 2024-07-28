
from dataclasses import dataclass
from dearpygui import dearpygui as dpg

@dataclass
class Rubric:
    name: str
    description: str
    color: tuple
    col_to_tag_correspondence: dict

    height = 50

    def generate_mini(self,openeditor: callable=None):
        #with dpg.child_window(height=self.height) as self._id:

            with dpg.group(horizontal=True) as self._id:

                dpg.add_color_button(label=f"{self.name}'s Color",default_value=self.color,height=self.height-16,width=50)

                with dpg.group():

                    dpg.add_input_text(
                        label="Name",
                        default_value=self.name,
                        enabled=False,
                        width=200)

                    dpg.add_input_text(
                        label="Description",
                        default_value=self.description,
                        enabled=False,
                        width=200)

                    dpg.add_button(
                        label="Edit",
                        callback=openeditor,
                        user_data=self)