

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
        #dpg.bind_theme(disabled_theme)

    def delete(self,**kwargs):
        dpg.delete_item(self._id)

class ObjTabPattern(DPGStage):

    items: list[any]

    def main(self,**kwargs):

        self.itemDict = kwargs.get("itemsDict",{})
        self.addNewCallback = kwargs.get("addNewCallback",None)
        self.label = f' {kwargs.get("label","")}'

        #self.itemList = kwargs.get("items",[])
        self.itemsKeysSorted = list(self.itemDict.keys())
        self.itemsKeysSorted.sort()

    def generate_id(self,**kwargs):

        self.tab_dict = {}

        with dpg.tab_bar() as self._id:

            self.visualizeTabs()
    
    def clearTabs(self):

        for tab in list(self.tab_dict.values()):
            dpg.delete_item(tab)

        dpg.delete_item(self.new)

    def visualizeTabs(self):
      
        for i,objKey in enumerate(self.itemsKeysSorted):

            with dpg.tab(label=f"{objKey}") as _tab:

                self.itemDict[objKey].generate_mini()

            self.tab_dict.update({objKey:_tab})

        self.new = dpg.add_tab_button(label=f'+{self.label}',callback=self.addNewWrapper)
        print(self.new)

    def addNewWrapper(self,sender,app_data,user_data):
        self.addNewCallback(after = self.afterAddNew)

    def afterAddNew(self):
        self.clearTabs()
        dpg.push_container_stack(self._id)
        self.visualizeTabs()

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



def parametrized(dec):
    #https://stackoverflow.com/questions/5929107/decorators-with-parameters
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)
        return repl
    return layer

@parametrized
def multiply(f, n):
    def aux(*xs, **kws):
        return n * f(*xs, **kws)
    return aux

@multiply(2)
def function(a):
    return 10 + a

@parametrized
def dpg_group(fn,direction="↓"):

    if direction =="↓":
        horizontal=False
    elif direction == "→":
        horizontal=True


    def inner1(*args, **kwargs):
        
        print("before Execution")
        
        # getting the returned value

        with dpg.group(horizontal = horizontal) as group_id:

            returned_value = fn(*args, **kwargs)
            print("after Execution")
        
            # returning the value to the original frame
            return returned_value, group_id
    
    return inner1


def hello_decorator(func):
    def inner1(*args, **kwargs):
        
        print("before Execution")
        
        # getting the returned value
        returned_value = func(*args, **kwargs)
        print("after Execution")
        
        # returning the value to the original frame
        return returned_value
        
    return inner1


# adding decorator to the function
@hello_decorator
def sum_two_numbers(a, b):
    print("Inside the function")
    return a + b

a, b = 1, 2

# getting the value through return of the function
print("Sum =", sum_two_numbers(a, b))