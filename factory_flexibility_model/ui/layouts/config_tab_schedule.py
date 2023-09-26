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


def update_config_tab_schedule(app):
    asset_key = app.selected_asset["key"]
    asset_type = app.selected_asset["type"]

    # Update general info
    app.root.ids.textfield_schedule_flowtype.text = app.selected_asset["flowtype"].name
    app.root.ids.label_schedule_name.text = app.selected_asset["name"].upper()
    app.root.ids.textfield_schedule_name.text = app.selected_asset["name"]
    app.root.ids.textfield_schedule_description.text = app.selected_asset["description"]
    app.root.ids.image_schedule_configuration.source = app.selected_asset["GUI"]["icon"]

    parameters = app.session_data["parameters"][asset_key]

    for parameter_key in [
        "power_max",
        "demands",
    ]:

        print(f"config_{asset_type}_{parameter_key}")
        list_item = getattr(app.root.ids, f"config_{asset_type}_{parameter_key}")
        list_icon = getattr(app.root.ids, f"config_{asset_type}_icon_{parameter_key}")

        list_item.secondary_text = "Not Specified"
        list_icon.icon = "help"
        list_icon.theme_text_color = "Custom"
        list_icon.text_color = [0.7, 0.7, 0.7, 1]
        list_item.theme_text_color = "Custom"
        list_item.text_color = [0.6, 0.6, 0.6, 1]
        list_item.font_style = "Subtitle1"
        list_item.secondary_theme_text_color = "Custom"
        list_item.secondary_text_color = [0.8, 0.8, 0.8, 1]

        if parameter_key in parameters.keys() and len(parameters[parameter_key]) > 0:
            list_icon.text_color = app.main_color.rgba
            list_item.text_color = app.main_color.rgba
            list_item.secondary_text_color = app.main_color.rgba
            list_item.font_style = "H6"

            if len(parameters[parameter_key]) == 1:
                value = parameters[parameter_key][next(iter(parameters[parameter_key]))]
                if value["type"] == "static":
                    list_item.secondary_text = f"{value['value']} {app.selected_asset['flowtype'].unit.get_unit_flowrate()}"
                    list_icon.icon = "ray-start-arrow"
                else:
                    list_item.secondary_text = f"Timeseries: {value['value']}"
                    list_icon.icon = "chart-line"
            elif len(parameters[parameter_key]) > 1:
                list_item.secondary_text = (
                    f"{len(parameters[parameter_key])} Variations Specified"
                )
                list_icon.icon = "multicast"


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
        app.session_data["scheduler_demands"][
            app.selected_asset["key"]
        ] = imported_demands

        # inform the user
        Snackbar(text=f"Excelfile successfully imported").open()
