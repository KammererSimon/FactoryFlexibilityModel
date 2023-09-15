# IMPORTS
import numpy as np
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import IconLeftWidget, IconRightWidget, TwoLineAvatarIconListItem

# LAYOUTS
Builder.load_file(r"factory_flexibility_model\ui\dialogs\parameter_config_dialog.kv")

# CLASSES
class dialog_parameter_config(BoxLayout):
    parameter = None


# FUNCTIONS
def parameter_config_dialog(app, caller):
    """
    This function opens the dialog for configuring values of component parameters.
    """

    app.dialog = MDDialog(
        title=f"{app.selected_asset['name']}: {caller.text}",
        type="custom",
        content_cls=dialog_parameter_config(),
    )

    app.dialog.size_hint = (None, None)
    app.dialog.width = dp(850)
    app.dialog.height = dp(700)

    app.dialog.parameter = caller.parameter
    app.dialog.content_cls.ids.textfield_value.hint_text = f"{caller.value_description} [{app.selected_asset['flowtype'].unit.get_unit_flowrate()}]"

    update_parameter_value_list(app)
    app.dialog.open()


def add_static_parameter_value(app):
    """
    this function takes the value currently given by the user via the textfield_value and appends it to the parameter list of the component within app.parameters
    """
    # get the value to store
    value = app.dialog.content_cls.ids.textfield_value.text

    # get the asset and parameter keys
    asset_key = app.selected_asset["key"]
    parameter_key = app.dialog.parameter

    # create a key to adress the variation
    variation = 0
    while variation in app.parameters[asset_key][parameter_key].keys():
        variation += 1

    # store the value under the determined key
    app.parameters[asset_key][parameter_key][variation] = value

    update_parameter_value_list(app)


def delete_parameter_value(app, value_key):
    """
    This function takes a pointer to a currently running app and a key to one of the values in the currently opened parametervalue definitiondialog. It deletes the referenced parameter from the app.parameters dict and refreshes the value list in the dialog.
    :param app: Pointer to the currently running app instance
    :param value_key: [str] Key to one value within the parameterlist of the selected asset
    :return: true
    """
    del app.parameters[app.selected_asset["key"]][app.dialog.parameter][value_key]
    update_parameter_value_list(app)


def update_parameter_value_list(app):
    """
    This function updates the entries within the list of user specified parameters on the parameter_config_dialog.
    It reads out all the entries from app.parameters[selected component] and generates a set of iconlistitems out of them.
    """

    # get the key of the currently defined parameter
    parameter = app.dialog.parameter

    # clear the current list
    app.dialog.content_cls.ids.list_parameter_variations.clear_widgets()

    # if no value for the parameter has been defined yet: create an empty dict and abort
    if parameter not in app.parameters[app.selected_asset["key"]].keys():
        app.parameters[app.selected_asset["key"]][parameter] = {}
        return

    # iterate over all currently specified values for the component and parameter
    for variation, value in app.parameters[app.selected_asset["key"]][
        parameter
    ].items():

        # define list entry depending on the kind of value that is being handled
        if isinstance(value, np.ndarray):
            text = "Timeseries"
            secondary_text = "Timeseries Name"
            icon = "chart-line"
        else:
            text = "Static Value"
            icon = "numeric"
            secondary_text = (
                f"{value} {app.selected_asset['flowtype'].unit.get_unit_flowrate()}"
            )

        # create a list item with the current value
        item = TwoLineAvatarIconListItem(
            IconLeftWidget(icon=icon),
            IconRightWidget(
                icon="delete",
                on_release=lambda x, value_key=variation: delete_parameter_value(
                    app, value_key
                ),
            ),
            text=text,
            secondary_text=secondary_text,
        )
        # add list item to the value list
        app.dialog.content_cls.ids.list_parameter_variations.add_widget(item)
