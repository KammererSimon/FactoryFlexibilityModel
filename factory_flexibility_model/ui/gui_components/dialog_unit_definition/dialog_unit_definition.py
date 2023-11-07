# IMPORTS
import numpy as np
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import (
    IconLeftWidget,
    IconLeftWidgetWithoutTouch,
    OneLineIconListItem,
    TwoLineIconListItem,
)
from kivymd.uix.snackbar import Snackbar

import factory_flexibility_model.factory.Unit as Unit
from factory_flexibility_model.ui.gui_components.info_popup.info_popup import show_info_popup
from factory_flexibility_model.ui.utility.window_handling import close_popup


# CLASSES
class DialogUnitDefinition(BoxLayout):
    pass


class PopupMagnitudeDefinition(BoxLayout):
    pass


# FUNCTIONS
def add_magnitude_to_unit(app):
    """
    This function adds the values currently written into the unit magnitude specification fields in the unit dialog into the magnitude-list of the selected unit

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """
    if (
        not app.popup.content_cls.ids.textfield_magnitude_flow.text == ""
        and not app.popup.content_cls.ids.textfield_magnitude_flowrate.text == ""
        and not app.popup.content_cls.ids.textfield_magnitude_dimension.text == ""
    ):
        # get the currently selected unit
        unit = app.blueprint.units[
            app.get_key(app.dialog.content_cls.ids.label_unit_name.text)
        ]
        try:

            # add magnitude values
            unit.magnitudes = np.append(
                unit.magnitudes,
                float(app.popup.content_cls.ids.textfield_magnitude_dimension.text),
            )
        except:
            app.popup.content_cls.ids.textfield_magnitude_dimension.error = True
            return

        unit.units_flow.append(app.popup.content_cls.ids.textfield_magnitude_flow.text)
        unit.units_flowrate.append(
            app.popup.content_cls.ids.textfield_magnitude_flowrate.text
        )
        app.popup.content_cls.ids.textfield_magnitude_dimension.error = False

        # reselect the unit to display the new magnitude table
        select_unit(app, unit)
        close_popup(app)


def add_unit(app, *args):
    """
    This function adds an unspecified unit to the factory and updates the unit dialog to display it

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """

    # assign a key to the new unit
    i = 1
    while f"unit_{i}" in app.blueprint.units.keys():
        i += 1
    unit_key = f"unit_{i}"
    app.blueprint.units[unit_key] = Unit.Unit(
        key=unit_key,
        quantity_type="other",
        conversion_factor=1,
        magnitudes=[],
        units_flow=[],
        units_flowrate=[],
        name=f"Unspecified Unit {i}",
    )

    update_unit_list(app)
    select_unit(app, app.blueprint.units[unit_key])

    # set unsaved changes to true
    app.unsaved_changes_on_session = True


def delete_unit(app):
    """
    This function deletes the currently selected unit from the blueprint.

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """
    # get key of the current unit
    unit_key = app.get_key(app.dialog.content_cls.ids.label_unit_name.text)

    if unit_key in ["energy", "mass"]:
        return

    # delete it from the units dict
    app.blueprint.units.pop(unit_key)

    # refresh unit list
    update_unit_list(app)

    # select basic unit
    select_unit(app, app.blueprint.units["energy"])


def save_changes_on_unit(app, *args):
    """
    This function checks the current user inputs in the unit definition window for validity and writes the values into the currently selected unit object.

    :param app: Pointer to the main factory_GUIApp-Object
    :param args: Just a dummy to accept values automatically handed over by lambda functions.
    :return: None
    """

    # get the current unit
    unit = app.blueprint.units[
        app.get_key(app.dialog.content_cls.ids.label_unit_name.text)
    ]

    # check, that the given name unique
    if not app.dialog.content_cls.ids.textfield_unit_name.text == unit.name:
        if app.get_key(app.dialog.content_cls.ids.textfield_unit_name.text):
            app.dialog.content_cls.ids.textfield_unit_name.error = True
            return
    app.dialog.content_cls.ids.textfield_unit_name.error = False

    # make sure that the conversion factor is a float
    try:
        unit.conversion_factor = float(
            app.dialog.content_cls.ids.textfield_unit_conversion_factor.text
        )
        app.dialog.content_cls.ids.textfield_unit_conversion_factor.error = False
    except:
        app.dialog.content_cls.ids.textfield_unit_conversion_factor.error = True
        return

    # write values from GUI to the unit
    unit.name = app.dialog.content_cls.ids.textfield_unit_name.text

    if app.dialog.content_cls.ids.switch_unit_energy.active:
        unit.quantity_type = "energy"
    if app.dialog.content_cls.ids.switch_unit_mass.active:
        unit.quantity_type = "mass"
    if app.dialog.content_cls.ids.switch_unit_other.active:
        unit.quantity_type = "other"

    app.dialog.content_cls.ids.label_unit_name.text = (
        app.dialog.content_cls.ids.textfield_unit_name.text
    )

    # no more unsaved changes on the current flow
    app.dialog.content_cls.ids.button_unit_save.disabled = True

    # set unsaved changes to true
    app.unsaved_changes_on_session = True

    # refresh list on screen
    update_unit_list(app)

    # inform the user
    Snackbar(text=f"{unit.name} updated!").open()


def select_unit_list_item(app, list_item):
    """
    This function is called whenever the user clicks on a unit within the unit list on the unit dialog. It checks, if there are any unsaved changes on the current selection. If yes the user is asked to save or discard them. Then a new unit is created or another unis is selected based on the list item clicked by the user.

    :param app: Pointer to the main factory_GUIApp-Object
    :param list_item: POinter to the list item that triggert the function call with a callback
    :return: None
    """

    # create a subfunction to bind
    def select(*args):
        close_popup(app)
        if list_item.text == "Add Unit":
            add_unit(app)
        else:
            select_unit(app, app.blueprint.units[app.get_key(list_item.text)])

    def save_and_select(*args):
        save_changes_on_unit(app)
        select()

    # check if there are unsaved changes
    if not app.dialog.content_cls.ids.button_unit_save.disabled:
        # create popup
        btn_dismiss = MDRaisedButton(text="Dismiss changes")
        btn_save = MDRaisedButton(text="Save changes")
        app.popup = MDDialog(
            title="Warning",
            buttons=[btn_dismiss, btn_save],
            text="There are unsaved changes on the currenttly selevted unit. Do you want to save them?",
        )
        btn_dismiss.bind(on_release=select)
        btn_save.bind(on_release=save_and_select)

        app.popup.open()
    else:
        select()


def select_unit(app, unit):
    """
    This function configures the unit-definition gui in a way that it displays all the values of the unit handed over

    :param app: Pointer to the main factory_GUIApp-Object
    :param unit: Pointer to the fm.unit object that the user requested to display withing the dialog
    :return: None
    """

    # write values of unit into the gui
    app.dialog.content_cls.ids.label_unit_name.text = unit.name
    app.dialog.content_cls.ids.textfield_unit_conversion_factor.text = str(
        unit.conversion_factor
    )
    if unit.quantity_type == "energy":
        app.dialog.content_cls.ids.switch_unit_energy.active = True
    elif unit.quantity_type == "mass":
        app.dialog.content_cls.ids.switch_unit_mass.active = True
    else:
        app.dialog.content_cls.ids.switch_unit_other.active = True

    # insert magnitude data into table
    row_data = []
    for i in range(len(unit.magnitudes)):
        row_data.append(
            (unit.magnitudes[i], unit.units_flow[i], unit.units_flowrate[i])
        )
    app.dialog.content_cls.ids.table_unit.row_data = row_data

    app.dialog.content_cls.ids.textfield_unit_name.text = unit.name

    # no more unsaved changes -> disable save button
    app.dialog.content_cls.ids.button_unit_save.disabled = True


def show_magnitude_creation_popup(app):
    """
    This function creates a popup that allows the user to specify a single magnitude of a unit via three input parameters: "magnitude", "unit flow" and "unit flowrate". An exemplary input dataset could be ("1000", "kWh", "kW")
    The layout for the popup is taken from dialog_unit_definition.kv via the PopupMagnitudeDefinition - class.

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """
    app.popup = MDDialog(
        title="Magnitude definition",
        type="custom",
        content_cls=PopupMagnitudeDefinition(),
    )
    app.popup.open()


def show_unit_config_dialog(app):
    """
    This function opens the popup-dialog for unit configuration

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """

    # abort if there is no session yet
    if app.session_data["session_path"] is None:
        show_info_popup(app,
            "Cannot configure units before creating or importing a session!"
        )
        return

    table = MDDataTable(
        column_data=[
            ("Magnitude", dp(40)),
            ("Unit Flow", dp(20)),
            ("Unit Flowrate", dp(20)),
        ],
        rows_num=20,
        elevation=0,
    )

    app.dialog = MDDialog(
        title="Unit definition",
        type="custom",
        content_cls=DialogUnitDefinition(),
        auto_dismiss=False,
    )

    app.dialog.size_hint = (None, None)
    app.dialog.width = dp(950)
    app.dialog.height = dp(800)
    app.dialog.content_cls.ids.table_container.add_widget(table)
    app.dialog.content_cls.ids["table_unit"] = table

    update_unit_list(app)

    select_unit(app, app.blueprint.units["energy"])
    app.dialog.open()


def update_unit_list(app):
    """
    This function creates a list of all existing units within the current blueprint to display it in the unit definition dialog. it starts with clearing the existing list, then goes thorugh the blueprint.unit-dicts and creates a list entry for every existing unit.

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """

    # predefine icons for list entries
    icons = {"energy": "lightning-bolt", "mass": "weight", "other": "help"}

    # clear existing list
    app.dialog.content_cls.ids.list_units.clear_widgets()

    # iterate over all units
    for unit in app.blueprint.units.values():
        # create list item
        item = TwoLineIconListItem(
            IconLeftWidgetWithoutTouch(icon=icons[unit.quantity_type]),
            text=unit.name,
            secondary_text=unit.quantity_type,
        )
        item.bind(on_release=lambda x, list_item=item: select_unit_list_item(app, list_item))

        # append item to list
        app.dialog.content_cls.ids.list_units.add_widget(item)

    item = OneLineIconListItem(
        IconLeftWidget(icon="plus"),
        text="Add Unit",
    )
    item.bind(on_release=lambda x, list_item=item: select_unit_list_item(app, list_item))
    # append item to list
    app.dialog.content_cls.ids.list_units.add_widget(item)
