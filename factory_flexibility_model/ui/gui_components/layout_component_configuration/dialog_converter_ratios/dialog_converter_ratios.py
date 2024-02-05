# IMPORTS
from kivy.metrics import dp
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import TwoLineAvatarListItem

from factory_flexibility_model.ui.gui_components.info_popup.info_popup import (
    show_info_popup,
)
from factory_flexibility_model.ui.utility.validate_textfield_inputs import (
    validate_float,
)
from factory_flexibility_model.ui.utility.window_handling import close_dialog


# CLASSES
class dialog_converter_ratios(BoxLayout):
    bilance_valid = BooleanProperty()
    primary_flow = StringProperty()


class TextfieldIconListItem(TwoLineAvatarListItem):
    connection_key = StringProperty()


class TextfieldCheckboxIconListItem(TwoLineAvatarListItem):
    connection_key = StringProperty()


# FUNCTIONS
def process_user_value_input(app, textfield):
    # make sure that user input is a valid float
    validate_float(textfield)
    # update the bilances of the converter
    update_bilance_calculation(app)


def show_converter_ratio_dialog(app):
    """
    This function opens the dialog to specify converter input/output ratios.
    :param app: kivy-app-object that the dialog is being called from
    """

    app.dialog = MDDialog(
        title=f"Input/Output Ratios at {app.selected_asset['name']}",
        type="custom",
        content_cls=dialog_converter_ratios(),
        auto_dismiss=False,
    )

    app.dialog.size_hint = (None, None)
    app.dialog.width = dp(1050)
    app.dialog.height = dp(1000)
    app.dialog.primary_flow = app.selected_asset["GUI"]["primary_flow"]
    update_connection_lists(app)
    update_bilance_calculation(app)
    app.dialog.open()


def select_ratio_type(app, segmented_control, segmented_item):
    """
    This function is being called when the user uses the segmentedcontrol to switch between energy and materila rations.
    It switches the screen displayed in the bottom area of the dialog according to the users selection.

    :param app: Pointer to the main factory_GUIApp-Object
    :param segmented_control: segmented control object -> unused
    :param segmented_item: item that the user clicked on -> is used to determine which screen to show
    :return: None
    """
    app.dialog.content_cls.ids.ratio_config_screens.current = segmented_item.text


def save_converter_ratios(app):
    """
    This function goes through all the list items within the converter ratio definition dialog and writes the user given values for the weights from the GUI into the corresponding connections within the blueprint.

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """

    # make sure that the current values are valid
    if not app.dialog.bilance_valid:
        show_info_popup(app, "The given ratios are invalid!")
        return

    # call the update primary flow routine to normalize all the ratio values in case the user changed the ratio of the primary flow manually
    update_primary_flow(app)

    # iterate over all connections and write their weighting factors into the blueprint
    for input in app.dialog.content_cls.ids.list_converter_inputs_energy.children:
        app.blueprint.connections[input.connection_key]["weight_destination"] = float(
            input.ids.list_item_textfield.text
        )
    for input in app.dialog.content_cls.ids.list_converter_inputs_mass.children:
        app.blueprint.connections[input.connection_key]["weight_destination"] = float(
            input.ids.list_item_textfield.text
        )
    for output in app.dialog.content_cls.ids.list_converter_outputs_energy.children:
        app.blueprint.connections[output.connection_key]["weight_origin"] = float(
            output.ids.list_item_textfield.text
        )
        app.blueprint.connections[output.connection_key][
            "to_losses"
        ] = output.ids.list_item_checkbox.active
    for output in app.dialog.content_cls.ids.list_converter_outputs_mass.children:
        app.blueprint.connections[output.connection_key]["weight_origin"] = float(
            output.ids.list_item_textfield.text
        )
        app.blueprint.connections[output.connection_key][
            "to_losses"
        ] = output.ids.list_item_checkbox.active

    # save the primary input/output of the converter
    app.selected_asset["GUI"]["primary_flow"] = app.dialog.primary_flow

    # close the dialog
    close_dialog(app)


def update_bilance_calculation(app):
    """
    This function calculates the sum of inputs and outputs for energy and material normalized to the standard units and writes the results into the textlabels within the dialog.

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """

    # Assume the bilance to be valid
    app.dialog.bilance_valid = True
    app.dialog.content_cls.ids.label_energy_out.theme_text_color = "Primary"
    app.dialog.content_cls.ids.label_mass_out.theme_text_color = "Primary"

    # Calculate energy input sum
    sum_energy_input = 0
    for input in app.dialog.content_cls.ids.list_converter_inputs_energy.children:
        try:
            sum_energy_input += app.blueprint.connections[input.connection_key][
                "flowtype"
            ].unit.conversion_factor * float(input.ids.list_item_textfield.text)
            input.ids.list_item_textfield.error = False
        except:
            # error detected...
            input.ids.list_item_textfield.error = True
            app.dialog.bilance_valid = False

    # Calculate energy output sum
    sum_energy_output = 0
    loss_connection = None
    for output in app.dialog.content_cls.ids.list_converter_outputs_energy.children:
        try:
            # if the connection is responsible for losses -> save it for later and continue
            if output.ids.list_item_checkbox.active:
                loss_connection = output
                continue

            # add the influence of the current connection to the output sum
            sum_energy_output += app.blueprint.connections[output.connection_key][
                "flowtype"
            ].unit.conversion_factor * float(output.ids.list_item_textfield.text)
            output.ids.list_item_textfield.error = False
        except:
            # error detected...
            app.dialog.bilance_valid = False
            output.ids.list_item_textfield.error = True

    if loss_connection is not None:
        loss_connection.ids.list_item_textfield.text = str(
            round(
                (sum_energy_input - sum_energy_output)
                / app.blueprint.connections[loss_connection.connection_key][
                    "flowtype"
                ].unit.conversion_factor,
                3,
            )
        )
        if sum_energy_input - sum_energy_output < 0:
            # error detected...
            app.dialog.bilance_valid = False
            loss_connection.ids.list_item_textfield.error = True
        else:
            sum_energy_output = sum_energy_input

    # Write results to GUI
    app.dialog.content_cls.ids.label_energy_in.text = f"{round(sum_energy_input,3)} kWh"
    if sum_energy_input == sum_energy_output:
        app.dialog.content_cls.ids.label_energy_out.text = (
            f"{round(sum_energy_output,3)} kWh"
        )
    elif sum_energy_input > sum_energy_output:
        app.dialog.content_cls.ids.label_energy_out.text = f"{round(sum_energy_output,3)} kWh (+ {round(sum_energy_input - sum_energy_output,3)} kWh losses)"
    else:
        app.dialog.content_cls.ids.label_energy_out.text = f"{round(sum_energy_output,3)} kWh ({round(sum_energy_output - sum_energy_input,3)} kWh too much!)"
        app.dialog.content_cls.ids.label_energy_out.theme_text_color = "Error"
        app.dialog.bilance_valid = False

    # Calculate mass input sum
    sum_mass_input = 0
    for input in app.dialog.content_cls.ids.list_converter_inputs_mass.children:
        try:
            sum_mass_input += app.blueprint.connections[input.connection_key][
                "flowtype"
            ].unit.conversion_factor * float(input.ids.list_item_textfield.text)
            input.ids.list_item_textfield.error = False
        except:
            # error detected...
            app.dialog.bilance_valid = False
            input.ids.list_item_textfield.error = True
    # Calculate mass output sum
    sum_mass_output = 0
    for output in app.dialog.content_cls.ids.list_converter_outputs_mass.children:
        try:
            # if the connection is responsible for losses -> save it for later and continue
            if output.ids.list_item_checkbox.active:
                loss_connection = output
                continue

            # add the influence of the current connection to the output sum
            sum_mass_output += app.blueprint.connections[output.connection_key][
                "flowtype"
            ].unit.conversion_factor * float(output.ids.list_item_textfield.text)
            output.ids.list_item_textfield.error = False
        except:
            # error detected...
            app.dialog.bilance_valid = False
            output.ids.list_item_textfield.error = True

    if loss_connection is not None:
        loss_connection.ids.list_item_textfield.text = str(
            round(
                (sum_mass_input - sum_mass_output)
                / app.blueprint.connections[loss_connection.connection_key][
                    "flowtype"
                ].unit.conversion_factor,
                3,
            )
        )
        if sum_mass_input - sum_mass_output < 0:
            # error detected...
            app.dialog.bilance_valid = False
            loss_connection.ids.list_item_textfield.error = True
        else:
            sum_mass_output = sum_mass_input

    # write results to GUI
    app.dialog.content_cls.ids.label_mass_in.text = f"{round(sum_mass_input,3)} kg"
    if sum_mass_input == sum_mass_output:
        app.dialog.content_cls.ids.label_mass_out.text = (
            f"{round(sum_mass_output,3)} kg"
        )
    elif sum_mass_input > sum_mass_output:
        app.dialog.content_cls.ids.label_mass_out.text = f"{round(sum_mass_output,3)} kg (+ {round(sum_mass_input - sum_mass_output,3)} kg losses)"
    else:
        app.dialog.content_cls.ids.label_mass_out.text = f"{round(sum_mass_output,3)} kg ({round(sum_mass_output - sum_mass_input,3)} kg too much!)"
        app.dialog.content_cls.ids.label_mass_out.theme_text_color = "Error"
        app.dialog.bilance_valid = False


def update_connection_lists(app):
    """
    This function updates the lists of incoming and outgoing connections within the component_ratio dialog, filling in all the connections from/to the currently selected converter asset.

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """

    # clear the current lists
    app.dialog.content_cls.ids.list_converter_inputs_energy.clear_widgets()
    app.dialog.content_cls.ids.list_converter_outputs_energy.clear_widgets()
    app.dialog.content_cls.ids.list_converter_inputs_mass.clear_widgets()
    app.dialog.content_cls.ids.list_converter_outputs_mass.clear_widgets()

    # track, if energy and material loss connections have been specified

    # iterate over all connections within the current factory blueprint
    for connection in app.blueprint.connections.values():

        # check if the connection is an input to the selected converter:
        if connection["to"] == app.selected_asset["key"]:

            # create list item for the connection
            item = TextfieldIconListItem(
                secondary_text=app.blueprint.components[connection["from"]]["name"],
                text=connection["flowtype"].name,
                connection_key=connection["key"],
                divider_color=(1, 1, 1, 1),
            )
            item.ids.list_item_textfield.helper_text = connection[
                "flowtype"
            ].unit.get_unit_flow()
            item.ids.list_item_textfield.text = str(connection["weight_destination"])
            # add list item to the correct  input_list
            if connection["flowtype"].unit.is_energy():
                if connection["from"] == app.dialog.primary_flow:
                    item.ids.list_item_primary.active = True
                app.dialog.content_cls.ids.list_converter_inputs_energy.add_widget(item)
            elif connection["flowtype"].unit.is_mass():
                if connection["from"] == app.dialog.primary_flow:
                    item.ids.list_item_primary.active = True
                app.dialog.content_cls.ids.list_converter_inputs_mass.add_widget(item)

        # check if the connection is an output of the selected converter:
        if connection["from"] == app.selected_asset["key"]:
            # create list item for the connection
            item = TextfieldCheckboxIconListItem(
                secondary_text=app.blueprint.components[connection["to"]]["name"],
                text=connection["flowtype"].name,
                connection_key=connection["key"],
                divider_color=(1, 1, 1, 1),
            )
            item.ids.list_item_textfield.helper_text = connection[
                "flowtype"
            ].unit.get_unit_flow()
            item.ids.list_item_textfield.text = str(connection["weight_origin"])

            # add list item to the output_list
            if connection["flowtype"].unit.is_energy():
                # add the checkbox to the correct group
                item.ids.list_item_checkbox.group = "energy"
                # check, if the current connection is meant to deduct losses
                if connection["to_losses"]:
                    item.ids.list_item_checkbox.active = True
                if connection["to"] == app.dialog.primary_flow:
                    item.ids.list_item_primary.active = True
                app.dialog.content_cls.ids.list_converter_outputs_energy.add_widget(
                    item
                )

            elif connection["flowtype"].unit.is_mass():
                # add the checkbox to the correct group
                item.ids.list_item_checkbox.group = "mass"
                # check, if the current connection is meant to deduct losses
                if connection["to_losses"]:
                    item.ids.list_item_checkbox.active = True
                if connection["to"] == app.dialog.primary_flow:
                    item.ids.list_item_primary.active = True
                app.dialog.content_cls.ids.list_converter_outputs_mass.add_widget(item)


def update_primary_flow(app):
    """
    This function is being called, whenever the user activates one of the checkboxes in the dialog and thereby decides
    to use another flow as the primary flow for the converter. The function first gets the information on the new
    primary flow, calculates a conversion factor to adjust all other inputs. Then it sets the ratio value of the new
    primary input to 1 and scales all other values accordingly so that the relative ratios do not change.

    :param app: Pointer to the main factory_GUIApp-Object
    :return: None
    """

    # get the list_item of the new primary flow and the corresponding numeric value
    scaling_factor = 1
    primary_flow_item = None
    for input in app.dialog.content_cls.ids.list_converter_inputs_energy.children:
        if input.ids.list_item_primary.active:
            scaling_factor = float(input.ids.list_item_textfield.text)
            primary_flow_item = input
            app.dialog.primary_flow = app.blueprint.connections[
                primary_flow_item.connection_key
            ]["from"]
    for input in app.dialog.content_cls.ids.list_converter_inputs_mass.children:
        if input.ids.list_item_primary.active:
            scaling_factor = float(input.ids.list_item_textfield.text)
            primary_flow_item = input
            app.dialog.primary_flow = app.blueprint.connections[
                primary_flow_item.connection_key
            ]["from"]
    for output in app.dialog.content_cls.ids.list_converter_outputs_energy.children:
        if output.ids.list_item_primary.active:
            scaling_factor = float(output.ids.list_item_textfield.text)
            primary_flow_item = output
            app.dialog.primary_flow = app.blueprint.connections[
                primary_flow_item.connection_key
            ]["to"]
    for output in app.dialog.content_cls.ids.list_converter_outputs_mass.children:
        if output.ids.list_item_primary.active:
            scaling_factor = float(output.ids.list_item_textfield.text)
            primary_flow_item = output
            app.dialog.primary_flow = app.blueprint.connections[
                primary_flow_item.connection_key
            ]["to"]

    # scale all ratios
    for input in app.dialog.content_cls.ids.list_converter_inputs_energy.children:
        input.ids.list_item_textfield.text = str(
            round(float(input.ids.list_item_textfield.text) / scaling_factor, 5)
        )
    for input in app.dialog.content_cls.ids.list_converter_inputs_mass.children:
        input.ids.list_item_textfield.text = str(
            round(float(input.ids.list_item_textfield.text) / scaling_factor, 5)
        )
    for output in app.dialog.content_cls.ids.list_converter_outputs_mass.children:
        output.ids.list_item_textfield.text = str(
            round(float(output.ids.list_item_textfield.text) / scaling_factor, 5)
        )
    for input in app.dialog.content_cls.ids.list_converter_outputs_energy.children:
        input.ids.list_item_textfield.text = str(
            round(float(input.ids.list_item_textfield.text) / scaling_factor, 5)
        )
