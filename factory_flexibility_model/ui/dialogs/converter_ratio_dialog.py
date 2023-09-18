# IMPORTS
import numpy as np
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import IconLeftWidget, IconRightWidget, TwoLineAvatarIconListItem
from kivy.properties import StringProperty

# LAYOUTS
Builder.load_file(r"factory_flexibility_model\ui\dialogs\converter_ratio_dialog.kv")

# CLASSES
class dialog_converter_ratios(BoxLayout):
    pass

class TextfieldLeftIconListItem(TwoLineAvatarIconListItem):
    connection_key = StringProperty()
    pass
class TextfieldRightIconListItem(TwoLineAvatarIconListItem):
    connection_key = StringProperty()
    pass

# FUNCTIONS

def save_converter_ratios(app):
    for input in app.dialog.content_cls.ids.list_converter_inputs_energy.children:
        app.blueprint.connections[input.connection_key]["weight_sink"] = float(input.ids.list_item_textfield.text)
    for input in app.dialog.content_cls.ids.list_converter_inputs_mass.children:
        app.blueprint.connections[input.connection_key]["weight_sink"] = float(input.ids.list_item_textfield.text)
    for output in app.dialog.content_cls.ids.list_converter_outputs_energy.children:
        app.blueprint.connections[output.connection_key]["weight_source"] = float(output.ids.list_item_textfield.text)
    for output in app.dialog.content_cls.ids.list_converter_outputs_mass.children:
        app.blueprint.connections[output.connection_key]["weight_source"] = float(output.ids.list_item_textfield.text)

def show_converter_ratio_dialog(app):
    """
    This function opens the dialog to specify converter input/output ratios.
    """

    app.dialog = MDDialog(
        title=f"{app.selected_asset['name']}: Input/Output Ratios",
        type="custom",
        content_cls=dialog_converter_ratios(),
        auto_dismiss=False
    )

    # display the icon of the current converter in the middle of the dialog
    app.dialog.content_cls.ids.image_converter_top.source = app.selected_asset["GUI"]["icon"]
    app.dialog.content_cls.ids.image_converter_bottom.source = app.selected_asset["GUI"]["icon"]

    app.dialog.size_hint = (None, None)
    app.dialog.width = dp(850)
    app.dialog.height = dp(700)
    update_connection_lists(app)
    app.dialog.open()

def update_connection_lists(app):
    """
    This function updates the lists of incoming and outgoing connections within the component_ratio dialog, filling in all the connections from/to the currently selected converter asset.
    """

    # clear the current lists
    app.dialog.content_cls.ids.list_converter_inputs_energy.clear_widgets()
    app.dialog.content_cls.ids.list_converter_outputs_energy.clear_widgets()
    app.dialog.content_cls.ids.list_converter_inputs_mass.clear_widgets()
    app.dialog.content_cls.ids.list_converter_outputs_mass.clear_widgets()

    # iterate over all connections within the current factory blueprint
    for connection in app.blueprint.connections.values():

        # check if the connection is an input to the selected converter:
        if connection["to"] == app.selected_asset["key"]:

            # create list item for the connection
            item = TextfieldLeftIconListItem(
                IconRightWidget(icon="arrow-right-bold",
                    theme_icon_color="Custom",
                    icon_color=connection["flowtype"].color.rgba,),
                text=app.blueprint.components[connection["from"]]["name"],
                secondary_text=connection["flowtype"].name,
                connection_key=connection["key"]
            )
            item.ids.list_item_textfield.helper_text = connection["flowtype"].unit.get_unit_flow()
            item.ids.list_item_textfield.text = str(connection["weight_sink"])
            # add list item to the correct  input_list
            if connection["flowtype"].unit.is_energy():
                app.dialog.content_cls.ids.list_converter_inputs_energy.add_widget(item)
            elif connection["flowtype"].unit.is_mass():
                app.dialog.content_cls.ids.list_converter_inputs_mass.add_widget(item)

        # check if the connection is an energy output of the selected converter:
        if connection["from"] == app.selected_asset["key"]:
            # create list item for the connection
            item = TextfieldRightIconListItem(
                IconLeftWidget(icon="arrow-right-bold",
                    theme_icon_color="Custom",
                    icon_color=connection["flowtype"].color.rgba,),
                text=app.blueprint.components[connection["to"]]["name"],
                secondary_text=connection["flowtype"].name,
                connection_key=connection["key"]
            )
            item.ids.list_item_textfield.helper_text = connection["flowtype"].unit.get_unit_flow()
            item.ids.list_item_textfield.text = str(connection["weight_source"])
            # add list item to the output_list
            if connection["flowtype"].unit.is_energy():
                app.dialog.content_cls.ids.list_converter_outputs_energy.add_widget(item)
            elif connection["flowtype"].unit.is_mass():
                app.dialog.content_cls.ids.list_converter_outputs_mass.add_widget(item)

