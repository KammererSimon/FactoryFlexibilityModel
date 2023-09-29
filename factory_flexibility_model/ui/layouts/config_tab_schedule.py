from tkinter import filedialog

import pandas as pd
from kivymd.uix.snackbar import Snackbar

import factory_flexibility_model.ui.utility.flowtype_determination as fd


def save_changes_on_schedule(app):
    """
    This function takes the user input from the schedule configuration tab and stores it in the blueprint
    """

    # get component_key
    key = app.selected_asset["key"]

    # make sure that the given name is not taken app
    if not app.blueprint.components[app.selected_asset["key"]][
        "name"
    ] == app.root.ids.textfield_schedule_name.text and app.get_key(
        app.root.ids.textfield_schedule_name.text
    ):
        app.show_info_popup("The given name is already assigned within the factory!")
        return

    # update general attributes and icon
    app.blueprint.components[key].update(
        {
            "name": app.root.ids.textfield_schedule_name.text,
            "description": app.root.ids.textfield_schedule_description.text,
        }
    )
    app.blueprint.components[key]["GUI"].update(
        {"icon": app.root.ids.image_schedule_configuration.source}
    )

    # change the flowtype if the user specified a new one
    flowtype_key = app.get_key(app.root.ids.textfield_schedule_flowtype.text)
    if not app.blueprint.components[key]["flowtype"].key == flowtype_key:
        fd.set_component_flowtype(
            app.blueprint, key, app.blueprint.flowtypes[flowtype_key]
        )

    # set unsaved changes parameters
    app.unsaved_changes_on_asset = False
    app.unsaved_changes_on_session = True

    # update connection names to adapt changes if the name of the source has changed
    app.update_connection_names()
    # update flowtype list to adapt changes if a flowtype has to be locked or unlocked
    app.update_flowtype_list()

    # redraw the preview:
    app.initialize_visualization()

    # inform the user
    Snackbar(text=f"{app.selected_asset['name']} updated!").open()


def import_scheduler_demands(app):
    """
    This function imports an xlsx file containing a matrix with demands and writes them as .demands for the currently selected scheduler
    :param app: pointer to the current FactoryGUI instance
    """

    # ask for filename
    filetype = [("xlsx", "*.xlsx")]
    filepath = filedialog.askopenfilename(defaultextension=filetype, filetypes=filetype)

    if not filepath == "":
        # import the excel sheet
        imported_demands = pd.read_excel(
            filepath, usecols="A:D", header=None, skiprows=1
        )

        # make sure that the key "demands" exists within the parameter list of the current compoent
        if (
            "demands"
            not in app.session_data["parameters"][app.selected_asset["key"]].keys()
        ):
            app.session_data["parameters"][app.selected_asset["key"]]["demands"] = {}

        # create a key to adress the variation
        # variation = 0
        # while variation in app.session_data["parameters"][app.selected_asset["key"]]["demands"].keys():
        #    variation += 1
        # TODO: activate multiple variations again when the model is capable of handling them

        variation = 0

        app.session_data["parameters"][app.selected_asset["key"]]["demands"][
            variation
        ] = {"type": "demands", "value": imported_demands.to_dict()}

        # inform the user
        Snackbar(text=f"Excelfile successfully imported").open()
