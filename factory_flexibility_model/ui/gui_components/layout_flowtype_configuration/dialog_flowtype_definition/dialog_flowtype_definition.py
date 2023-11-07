# IMPORTS
from kivymd.uix.dialog import MDDialog
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivymd.uix.pickers import MDColorPicker
from factory_flexibility_model.ui.utility.window_handling import close_popup

# CLASSES
class DialogFlowtypeDefinition(BoxLayout):
    """
    This class represents a Boxlayout containing the layout of the flowtype_definition_dialog from dialog_flowtype_definition.kv
    """

    pass

# FUNCTIONS
def show_color_picker(app):
    """
    This function openes a popup that gives the user an interface to specify an RGB-color value.
    Once the user clicks on the confirm button the selected color is handed over to update_flowtype_color()

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """

    # create color picker
    app.popup = MDColorPicker(size_hint=(0.3, 0.5), background_color=[1, 1, 1, 1])

    # open popup
    app.popup.open()

    # bind update_flowtype_color_function
    app.popup.bind(
        on_release=lambda dummy1, dummy2, selected_color: update_flowtype_color(app, selected_color),
    )

def show_flowtype_config_dialog(app):
    """
    This function opens the dialog for configuring flowtypes. The function is being called when the user clicks on one entry within the flowtype list on the right of the main screen.
    The dialog allows the user to enter name and description for the flowtype, specify the unit and color and define, if the flowtype is meant to represent losses.

    All further actions like calling the colorpicker for color selection, input validations and the save-routine are called from the corresponding kivy file dialog_flowtypes_definition.kv

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """

    app.dialog = MDDialog(
        title="Flowtype Definition",
        type="custom",
        content_cls=DialogFlowtypeDefinition(),
        auto_dismiss=False,
    )

    app.dialog.size_hint = (None, None)
    app.dialog.width = dp(850)
    app.dialog.height = dp(700)

    app.dialog.open()
    app.dialog.background_click = False

def update_flowtype_color(app, selected_color):
    """
    This function takes the color that the user specified within the colorpicker and writes it to the color-attribute of the color preview icon within the flowtype definition dialog.

    :param app: Pointer to the main factory_GUIApp-Object
    :param selected_color: The color that the user selected in the colorpicker in (R, G, B, A) - format.
    :return: None
    """

    # set selected color as color for the color-icon. set the alpha channel on 1
    app.dialog.content_cls.ids.icon_flowtype_color.icon_color = selected_color[
        :-1
    ] + [1]

    #close color picker
    close_popup(app)

    # enable save button for the user
    app.dialog.content_cls.ids.button_flowtype_save.disabled = False
