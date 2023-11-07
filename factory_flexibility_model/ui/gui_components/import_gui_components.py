# IMPORTS
from kivy.lang import Builder

# FUNCTIONS
def import_gui_components():
    """
    .. _import_gui_components:

    This function uses the kivy-Builder-method to read in all required individual layouts, dialogs and widgets that are specified within separate .kv files.

    It is being called by the main gui during the `build`_ function on GUI startup.

    The following kivy-widget-trees are imported:
    - `dialog_session_options.kv`_
    - `dialog_unit_definition.kv`_
    - `dialog_converter_ratios.kv`_
    - `dialog_component_definition.kv`_
    - `dialog_flowtype_definition.kv`_
    - `dialog_icon_selection.kv`_
    - `dialog_new_session.kv`_
    - `dialog_parameter_configuration.kv`_
    - `dialog_save_session_as.kv`_
    - `draglabel.kv`_
    - `popup_add_static_value.kv`_
    - `layout_component_configuration_tab.kv`_
    - `layout_flowtype_list.kv`_
    - `layout_main_menu.kv`_
    - `popup_add_timeseries.kv`_

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """
    # specify relative path of gui elements within the project folder
    gui_components_path = "factory_flexibility_model\\ui\\gui_components"

    # specify all layouts to import
    gui_components = ["dialog_session_options\\dialog_session_options.kv",
                      "dialog_unit_definition\\dialog_unit_definition.kv",
                      "layout_component_configuration\\dialog_converter_ratios\\dialog_converter_ratios.kv",
                      "layout_component_configuration\\dialog_component_definition\\dialog_component_definition.kv",
                      "layout_component_configuration\\dialog_icon_selection\\dialog_icon_selection.kv",
                      "layout_component_configuration\\dialog_parameter_configuration\\dialog_parameter_configuration.kv",
                      "layout_component_configuration\\dialog_parameter_configuration\\popup_add_static_value.kv",
                      "layout_component_configuration\\dialog_parameter_configuration\\popup_add_timeseries.kv",
                      "layout_component_configuration\\layout_component_configuration_tab.kv",
                      "layout_flowtype_configuration\\dialog_flowtype_definition\\dialog_flowtype_definition.kv",
                      "layout_flowtype_configuration\\layout_flowtype_list.kv",
                      "main_menu\\dialog_new_session.kv",
                      "main_menu\\dialog_save_session_as.kv",
                      "main_menu\\layout_main_menu.kv",
                      "layout_canvas\\drag_label\\draglabel.kv"
                      ]

    # iterate over all layouts and call Builder-method
    for component_file in gui_components:
        Builder.load_file(rf"{gui_components_path}\{component_file}")
