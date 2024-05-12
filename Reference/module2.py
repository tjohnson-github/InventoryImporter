
import dearpygui.dearpygui as dpg



def main():
    #dpg.create_context()

    with dpg.window(label="Tutorial", pos=(20, 50), width=275, height=225) as win1:
        t1 = dpg.add_input_text(default_value="some text")
        t2 = dpg.add_input_text(default_value="some text")
        with dpg.child_window(height=100):
            t3 = dpg.add_input_text(default_value="some text")
            dpg.add_input_int()
        dpg.add_input_text(default_value="some text")

    with dpg.window(label="Tutorial", pos=(320, 50), width=275, height=225) as win2:
        dpg.add_input_text(default_value="some text")
        dpg.add_input_int()

    with dpg.theme() as item_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (200, 200, 100), category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0, category=dpg.mvThemeCat_Core)

    dpg.bind_item_theme(t2, item_theme)

    dpg.show_style_editor()

    #dpg.create_viewport(title='Custom Title', width=800, height=600)
    #dpg.setup_dearpygui()
    #dpg.show_viewport()
    #dpg.start_dearpygui()
    #dpg.destroy_context()

if __name__=="__main__":
    dpg.create_context()
    dpg.create_viewport(title='JFGC Import Inventory Assistant', width=900, height=700)
    dpg.setup_dearpygui()

    main()
    
    dpg.show_viewport()
    #dpg.set_primary_window("Primary Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()