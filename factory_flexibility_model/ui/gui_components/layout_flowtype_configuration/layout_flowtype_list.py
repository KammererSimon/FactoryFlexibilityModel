# IMPORTS
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.list import (
    IconLeftWidget,
    IconLeftWidgetWithoutTouch,
    IconRightWidget,
    OneLineIconListItem,
    TwoLineAvatarIconListItem,
)

import factory_flexibility_model.factory.Flowtype as ft
from factory_flexibility_model.ui.gui_components.layout_canvas.factory_visualisation import (
    initialize_visualization,
)
from factory_flexibility_model.ui.gui_components.layout_flowtype_configuration.dialog_flowtype_definition.dialog_flowtype_definition import (
    show_flowtype_config_dialog,
)
from factory_flexibility_model.ui.utility.color import color
from factory_flexibility_model.ui.utility.GUI_logging import log_event
from factory_flexibility_model.ui.utility.window_handling import close_dialog


# CLASSES
class layout_flowtype_list(BoxLayout):
    """
    This class represents a Boxlayout containing the layout of the flowtype_list that is being displayed on the right of the main screen, taken from layout_flowtype_list.kv
    """


# FUNCTIONS
def add_flowtype(app):
    """
    This function ads a generic new flowtype to the factory and selects it for configuration

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """

    # create key for the new flow
    i = 0
    while f"flowtype_{i}" in app.blueprint.flowtypes.keys():
        i += 1
    flowtype_key = f"flowtype_{i}"

    # create initial name for the flowtype
    i = 1
    while app.get_key(f"Unspecified Flowtype {i}"):
        i += 1
    flowtype_name = f"Unspecified Flowtype {i}"

    # create a new flowtype:
    app.blueprint.flowtypes[flowtype_key] = ft.Flowtype(
        key=flowtype_key,
        name=flowtype_name,
        unit=app.blueprint.units["energy"],
        color="#999999",
    )

    # update list of flowtypes on screen
    update_flowtype_list(app)

    # set unsaved changes to true
    app.unsaved_changes_on_session = True

    # write log
    log_event(app, f"New flowtype added with key '{flowtype_key}'", "DEBUG")


def save_changes_on_flowtype(app):
    """
    This function checks the current user inputs in the flowetype definition window for validity and writes the values
    into the currently selected flowtype object.

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """
    # get the current flowtype
    flowtype = app.blueprint.flowtypes[
        app.get_key(app.dialog.content_cls.ids.label_flowtype_name.text)
    ]

    # check, that the given name is unique
    if not app.dialog.content_cls.ids.textfield_flowtype_name.text == flowtype.name:
        if app.get_key(app.dialog.content_cls.ids.textfield_flowtype_name.text):
            app.dialog.content_cls.ids.textfield_flowtype_name.error = True
            return
    app.dialog.content_cls.ids.textfield_flowtype_name.error = False

    # write values from GUI to the flowtype
    flowtype.name = app.dialog.content_cls.ids.textfield_flowtype_name.text
    flowtype.description = (
        app.dialog.content_cls.ids.textfield_flowtype_description.text
    )
    flowtype.unit = app.blueprint.units[
        app.get_key(app.dialog.content_cls.ids.textfield_flowtype_unit.text)
    ]
    flowtype.color = color(app.dialog.content_cls.ids.icon_flowtype_color.icon_color)
    flowtype.represents_losses = (
        app.dialog.content_cls.ids.checkbox_flowtype_losses.active
    )

    # update name-label of the gui
    app.dialog.content_cls.ids.label_flowtype_name.text = (
        app.dialog.content_cls.ids.textfield_flowtype_name.text
    )

    # no more unsaved changes on the current flow
    app.dialog.content_cls.ids.button_flowtype_save.disabled = True

    # set unsaved changes to true
    app.unsaved_changes_on_session = True

    # refresh list on screen
    update_flowtype_list(app)

    # refresh visualisation to adapt new color
    initialize_visualization(app)

    close_dialog(app)

    # inform the user
    log_event(app, f"Flowtype {flowtype.name} has been updated!", "INFO")


def select_flowtype(app, flowtype):
    """
    This function configures the flowtype-definition dialog in a way that it displays all the values of the flowtype handed over.

    :param app: Pointer to the main factory_GUIApp-Object
    :param flowtype: `Flowtype`_ Object that the user selected to view in the flowtype definition dialog.
    :return: None
    """
    # write values of unit into the gui
    app.dialog.content_cls.ids.label_flowtype_name.text = flowtype.name
    app.dialog.content_cls.ids.textfield_flowtype_name.text = flowtype.name
    app.dialog.content_cls.ids.textfield_flowtype_description.text = (
        flowtype.description
    )
    app.dialog.content_cls.ids.textfield_flowtype_unit.text = flowtype.unit.name
    app.dialog.content_cls.ids.icon_flowtype_color.icon_color = flowtype.color.tuple
    app.dialog.content_cls.ids.checkbox_flowtype_losses.active = (
        flowtype.represents_losses
    )

    # no more unsaved changes -> disable save button
    app.dialog.content_cls.ids.button_flowtype_save.disabled = True


def select_flowtype_list_item(app, list_item):
    """
    This function is called whenever the user clicks on a flowtype within the flowtype list on the flowtypet dialog. It checks, if there are any unsaved changes on the current selection. If yes the user is asked to save or discard them. Then a new flowtype is created or another flowtype is selected based on the list item clicked by the user.

    :param app: Pointer to the main factory_GUIApp-Object
    :param list_item: POinter to the list item that the user clicked on and that therefore called the function during its callback.
    :return: None
    """

    if list_item.text == "Add Flowtype":
        app.add_flowtype()
    elif list_item.text in ["Material Losses", "Energy Losses",  "Heat", "Unknown Flow"]:
        # TODO: change this list of keys to a dynamic list from the config file once the standard flowtypes are imported instead of hardcoded
        log_event(app, "Cannot change the predefined Flowtypes", "ERROR", f"User tried to alter Flowtype {list_item.text} and got the following message: ")
    else:
        show_flowtype_config_dialog(app)
        select_flowtype(app, app.blueprint.flowtypes[app.get_key(list_item.text)])


def update_flowtype_list(app):
    """
    This function creates a list of all existing flowtypes within the blueprint and adds it to the menu on the right of the sceen.
    It starts by deleting the existing list, then goes through blueprint.flowtypes and creates a list entry for every existing flowtype.
    All flowtypes are bound to a callback that calls the flowtype definitions dialog for them.

    After creating the list a last listitem is added which functions as the "new flowtype"-button.

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """

    # predefine icons for list entries
    icons = {"energy": "lightning-bolt", "mass": "weight", "other": "help"}

    # clear existing list
    app.root.ids.screen_flowtype_list.clear_widgets()

    layout = layout_flowtype_list()

    # iterate over all units
    for flowtype in app.blueprint.flowtypes.values():
        # create list item
        list_item = TwoLineAvatarIconListItem(
            IconLeftWidgetWithoutTouch(
                icon="circle",
                theme_icon_color="Custom",
                icon_color=flowtype.color.rgba,
            ),
            text=flowtype.name,
            secondary_text=flowtype.unit.quantity_type,
        )
        list_item.bind(
            on_release=lambda x, item=list_item: select_flowtype_list_item(app, item)
        )

        if app.flowtype_used(flowtype.key):
            lock_icon = IconRightWidget(icon="lock")
            list_item.add_widget(lock_icon)

        # append item to list
        layout.ids.list_flowtypes.add_widget(list_item)

    # create another list item acting as the "new flowtype" button
    list_item = OneLineIconListItem(
        IconLeftWidget(icon="plus"),
        text="Add Flowtype",
    )
    list_item.bind(on_release=lambda x: add_flowtype(app))

    # append item to list
    layout.ids.list_flowtypes.add_widget(list_item)

    # place the whole flowtype layout in the main screen
    app.root.ids.screen_flowtype_list.add_widget(layout)
