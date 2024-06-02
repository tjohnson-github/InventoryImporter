import dearpygui.dearpygui as dpg
 
with dpg.theme() as global_theme:

    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (185, 140, 23), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,(155,100,100),  category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
      
    with dpg.theme_component(dpg.mvButton, enabled_state=False):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_Button, (155, 40, 80))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,   (155, 40, 80),   category=dpg.mvThemeCat_Core)


    '''with dpg.theme_component(dpg.mvThemeCol_Button, enabled_state=False):
        dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 0, 0])
        dpg.add_theme_color(dpg.mvThemeCol_Button, [255, 0, 0], category=dpg.mvThemeCat_Core)
        #dpg.add_theme_color(dpg.mvThemeCol_Button, (185, 140, 23), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered,(155,100,100),  category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)'''

    #   with dpg.theme() as disabled_theme:
    with dpg.theme_component(dpg.mvThemeCol_Button, enabled_state=False):
        dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 0, 0])
        dpg.add_theme_color(dpg.mvThemeCol_Button, [255, 0, 0])

    with dpg.theme_component(dpg.mvThemeCol_CheckMark,enabled_state=False):
        dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 0, 0])
        dpg.add_theme_color(dpg.mvThemeCol_Button, [255, 0, 0])