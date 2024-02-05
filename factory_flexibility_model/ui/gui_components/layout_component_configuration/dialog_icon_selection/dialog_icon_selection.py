# IMPORTS
from kivy.uix.image import Image
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog

from factory_flexibility_model.ui.gui_components.layout_canvas.factory_visualisation import (
    initialize_visualization,
)
from factory_flexibility_model.ui.utility.window_handling import close_dialog


# CLASSES
class DialogIconSelection(MDBoxLayout):
    pass


# FUNCTIONS


def show_icon_selection_dialog(app, caller):
    """
    This function creates a dialog giving the user the option to select one of the component icons out of the asset library.
    The origin path of the selected icon is set as image source path for the image widget that the menu has been called from.

    :param app: Pointer to the main factory_GUIApp-Object
    :param caller: Pointer to the gui component that called the flowtype dropdown menu
    :return: None
    """

    dialog_content = DialogIconSelection()

    # determine which selection of icons is displayed
    if app.selected_asset["type"] == "source":
        icon_list = app.config["assets"]["source_icons"]
        size = [100, 100]
    elif app.selected_asset["type"] == "sink":
        icon_list = app.config["assets"]["sink_icons"]
        size = [100, 100]
    else:
        icon_list = app.config["assets"]["component_icons"]
        size = [100, 100]

    for icon_name, icon_source in icon_list.items():
        image = Image(
            source=icon_source,
            size_hint=(None, None),
            size=size,
            on_touch_up=lambda instance, touch, icon_source=icon_source: set_image(
                instance, touch, caller, icon_source, app
            ),
        )
        dialog_content.ids.grid_icons.add_widget(image)

    app.dialog = MDDialog(
        type="custom",
        title="Icon Selection",
        content_cls=dialog_content,
    )

    app.dialog.open()


def set_image(instance, touch, caller, path, app):
    """
    This is a helper function that is used to write a user selected image source path from the icon_selection_dropdown to the target component.source.
    After the image path has been handed over the dropdown menu is being closed.

    :param app: Pointer to the main factory_GUIApp-Object
    :param caller: Pointer to the gui component that called the flowtype dropdown menu in the first place
    :param instance: The widget that triggered the function call via its on_touch_down event
    :param path: [String] Path to the icon that the user has selected
    :param touch: The touch event that triggered the function call
    :return: None
    """
    if not instance.collide_point(*touch.pos):
        return

    # return the selected icon to the iconlabel in the config-tab
    caller.source = path
    app.selected_asset["GUI"]["icon"] = caller.source
    initialize_visualization(app)

    # close icon selection dialog
    close_dialog(app)
