

import dearpygui.dearpygui as dpg

class DPGStage:

    label: str

    errorColor = (255, 68, 51)

    def __init__(self,stageOnly=False,**kwargs):


        self.main(**kwargs)
        #kwargs.get("tabView",self.)

        with dpg.stage() as self.stage:
           
           self.generate_id(**kwargs)


        if not stageOnly:
            self.submit()

        self.set_themes()

    def main(self,**kwargs):
        ...

    def submit(self):
        dpg.unstage(self.stage)

    def set_values(self,**kwargs):
            pass

    def generate_id(self,**kwargs):
       #f"This function should be defined in your custom class:\t{kwargs = }"
        ...

    def set_themes(self):
        from DPG_Themes import global_theme
        dpg.bind_theme(global_theme)

    def delete(self,**kwargs):
        dpg.delete_item(self._id)


def debugDPG(func): 

    def wrap_func(*args, **kwargs): 

        print(args)
        print(kwargs)

        sender = args.get("sender")
        app_data = args.get("app_data")
        user_data = args.get("user_data")

        print(f'Function {func.__name__!r}:')
        print(f"\t{sender=}")
        print(f"\t{app_data=}")
        print(f"\t{user_data=}")

        result = func(*args, **kwargs) 
        return result 
    return wrap_func 