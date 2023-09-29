# This file contains the function that creates and displays the dialog to specify name and path for a new session

# IMPORTS
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog

import factory_flexibility_model.ui.utility.flowtype_determination as fd

# LAYOUTS
Builder.load_file(
    r"factory_flexibility_model\ui\dialogs\dialog_component_definition.kv"
)


# CLASSES
class DialogComponentDefinition(BoxLayout):
    pass


# FUNCTIONS
def show_component_definition_dialog(app):
    """
    This function creates a new dialog within app.dialog. The Dialog Layout is taken from ui.dialogs.dialog_component_definition.kv.
    It contains all the input fields required for the user to specify name, description and flowtype of the component
    """

    # close the previous dialog
    app.close_dialog()

    # create dialog
    btn_false = MDFlatButton(text="Cancel")
    btn_true = MDRaisedButton(text="Save Changes")
    app.dialog = MDDialog(
        title="Component Definition",
        buttons=[btn_false, btn_true],
        type="custom",
        content_cls=DialogComponentDefinition(),
    )
    # bind callbacks to buttons
    btn_true.bind(on_release=lambda instance: save_component_definition(app))
    btn_false.bind(on_release=app.dialog.dismiss)

    app.dialog.content_cls.ids.textfield_name.text = app.selected_asset["name"]
    app.dialog.content_cls.ids.textfield_description.text = app.selected_asset[
        "description"
    ]
    app.dialog.content_cls.ids.button_flowtype.text = app.selected_asset[
        "flowtype"
    ].name
    app.dialog.open()


def save_component_definition(app):

    # get name and description inputs
    name = app.dialog.content_cls.ids.textfield_name.text

    # make sure that the given name is not taken yet
    if not app.selected_asset["name"] == name and app.get_key(name):
        app.show_info_popup("The given name is already assigned within the factory!")
        return

    # write configuration into the blueprint
    app.selected_asset["name"] = app.dialog.content_cls.ids.textfield_name.text
    app.selected_asset[
        "description"
    ] = app.dialog.content_cls.ids.textfield_description.text

    # change the flowtype if the user specified a new one
    flowtype_key = app.get_key(app.dialog.content_cls.ids.button_flowtype.text)
    if not app.selected_asset["flowtype"].key == flowtype_key:
        fd.set_component_flowtype(
            app.blueprint,
            app.selected_asset["key"],
            app.blueprint.flowtypes[flowtype_key],
        )

    # update the GUI
    app.update_config_tab()
    app.initialize_visualization()
    app.close_dialog()
