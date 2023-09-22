from kivymd.uix.snackbar import Snackbar
import factory_flexibility_model.ui.utility.flowtype_determination as fd

def save_changes_on_source(app):
    """
    This function takes the user input from the source configuration tab and stores it in the blueprint
    """

    # get component_key
    key = app.selected_asset["key"]

    # make sure that the given name is not taken app
    if not app.blueprint.components[app.selected_asset["key"]][
               "name"
           ] == app.root.ids.textfield_source_name.text and app.get_key(
        app.root.ids.textfield_source_name.text
    ):
        app.show_info_popup(
            "The given name is already assigned within the factory!"
        )
        return

    # update general attributes and icon
    app.blueprint.components[key].update(
        {
            "name": app.root.ids.textfield_source_name.text,
            "description": app.root.ids.textfield_source_description.text,
        }
    )
    app.blueprint.components[key]["GUI"].update(
        {"icon": app.root.ids.image_source_configuration.source}
    )

    # change the flowtype if the user specified a new one
    flowtype_key = app.get_key(app.root.ids.textfield_source_flowtype.text)
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


def update_config_tab_source(app):
    asset_key = app.selected_asset["key"]

    # Update general info
    app.root.ids.label_source_name.text = app.selected_asset["name"]
    app.root.ids.textfield_source_name.text = app.selected_asset["name"]
    app.root.ids.textfield_source_description.text = app.selected_asset["description"]
    app.root.ids.textfield_source_flowtype.text = app.selected_asset["flowtype"].name
    app.root.ids.image_source_configuration.source = app.selected_asset["GUI"]["icon"]

    for parameter in app.session_data["parameters"][asset_key]:
        print(parameter)

    parameters = app.session_data["parameters"][asset_key]

    for parameter_key in [
        "capacity_charge",
        "cost",
        "power_max",
        "power_min",
        "availability",
        "co2_emission_per_unit",
        "determined_power",
    ]:

        list_item = getattr(app.root.ids, f"config_source_{parameter_key}")
        list_icon = getattr(app.root.ids, f"config_source_icon_{parameter_key}")

        if parameter_key in parameters.keys():
            if len(parameters[parameter_key]) == 1:
                if parameters[parameter_key][0]["type"] == "static":
                    list_item.secondary_text = f"{parameters[parameter_key][0]['value']} {app.selected_asset['flowtype'].unit.get_unit_flowrate()}"
                    list_icon.icon = "arrow-down-drop-circle-outline"
                else:
                    list_item.secondary_text = f"Timeseries: {parameters[parameter_key][0]['value']}"
                    list_icon.icon = "chart-line"
            else:
                list_item.secondary_text = f"{len(parameters[parameter_key])} Variations Specified"
                list_icon.icon = "cog"
        else:
            list_item.secondary_text = "Not Specified"
            list_icon.icon = "help"
