from kivy.metrics import dp
from kivymd.uix.datatables import MDDataTable


def create_simulation_list(parameters, simulation_list=None, index=0):

    # initialize simulation list on initial call
    if simulation_list is None:
        simulation_list = {}

    # abort if all parameters have been considered
    if index == len(parameters):
        yield dict(simulation_list)
        return

    parameter_name = list(parameters.keys())[index]
    for key in parameters[parameter_name]:
        simulation_list[parameter_name] = parameters[parameter_name][key]
        yield from create_scenario_table_data(parameters, simulation_list, index + 1)


def create_scenario_table_data(parameters, scenario_list=None, row_data=None, index=0):
    if scenario_list is None:
        # initialize scenario list
        scenario_list = {}
    if row_data is None:
        row_data = []

    # all combinations found?
    if index == len(parameters):
        yield dict(scenario_list), list(row_data)
        return

    parameter_name = list(parameters.keys())[index]
    for key in parameters[parameter_name]:

        row_data.append(parameters[parameter_name][key]["value"])
        scenario_list[parameter_name] = parameters[parameter_name][key]
        yield from create_scenario_table_data(
            parameters, scenario_list, row_data, index + 1
        )
        row_data.pop()


def update_scenario_list(app):

    static_parameters = {}
    variable_parameters = {}
    column_data = [("Simulation", dp(30)), ("Status", dp(30))]

    # iterate over all components that have parameters specified
    for component, parameters in app.session_data["parameters"].items():

        # iterate over all specified parameters
        for parameter, variations in parameters.items():

            # there may be empty keys if the user deleted parameters...ignore them
            if len(variations) == 0:
                continue

            # if the parameter is fixed: add it to the static parameter list
            if len(variations) == 1:
                if component not in static_parameters:
                    static_parameters[component] = {}
                static_parameters[component][parameter] = variations[
                    next(iter(variations))
                ]

            # else add it to the variable parameter list
            else:
                variable_parameters[f"{component}/{parameter}"] = variations
                column_data.append(
                    (
                        f"{app.blueprint.components[component]['name']}: {parameter}",
                        dp(45),
                    )
                )

    scenario_list, row_data_values = zip(
        *list(create_scenario_table_data(variable_parameters))
    )

    row_data = []
    index = 1
    for value in row_data_values:
        row_data.append(
            (index, ("alert", [255 / 256, 165 / 256, 0, 1], "Not Simulated"), *value)
        )
        index += 1

    # create the table with all scenarios
    data_table = MDDataTable(
        use_pagination=True,
        check=True,
        column_data=column_data,
        row_data=row_data,
        elevation=0,
    )

    # replace existing table with the new one
    app.root.ids.simulation_screens.clear_widgets()
    app.root.ids.simulation_screens.add_widget(data_table)

    simulations = list(create_simulation_list(variable_parameters))

    # #data_tables.bind(on_row_press=self.on_row_press)
    # #data_tables.bind(on_check_press=self.on_check_press)
