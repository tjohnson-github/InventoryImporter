
@dataclass
class Rubric:
    name: str
    description: str
    color: tuple
    col_to_tag_correspondence: dict

    height = 50

    def generate_mini(self,openeditor: callable):
        with dpg.child_window(height=self.height) as self._id:

            with dpg.group(horizontal=True):

                dpg.add_color_button(label=f"{self.name}'s Color",default_value=self.color,height=self.height-16,width=50)

                with dpg.group():

                    dpg.add_input_text(
                        label="Name",
                        default_value=self.name,
                        enabled=False,
                        width=200)

                    dpg.add_input_text(
                        label="Description",
                        default_value=self.desc,
                        enabled=False,
                        width=200)

                    dpg.add_button(
                        label="Edit",
                        callback=openeditor,
                        user_data=self)

    def openRubricLinker(self):
        LinkRubricToSchema(schema=self)