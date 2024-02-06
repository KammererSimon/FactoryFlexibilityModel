# This script is called on the following paths:
# -> fm.dash.create_dash() -> update_plots_overview()


def create_cost_overview(simulation):
    """
    This function takes a simulation object and creates a simple string that contains a formatted list of all the costs factors that determine the target function value of the solved simulation.

    :param simulation: [fm.simulation-object]
    :return: [str]
    """

    # get cost results from simulation
    costs = simulation.result["costs"]

    # get currency from factory
    currency = simulation.factory.currency

    # define cost_types and their display names
    cost_types = {
        "inputs": "Cost and revenue of inputs",
        "outputs": "Cost and revenue of outputs",
        "converter_ramping": "Converter operation cost",
        "capacity_provision": "Costs for capacity provision",
        "emission_allowances": "Emission cost",
        "slacks": "Slack cost",
    }

    # initialize string
    detailed_costs = ""

    # iterate over all cost types
    for cost_type, cost_items in costs.items():

        #  Skip iteration if no cost items of current type exist
        if cost_items == {}:
            continue

        # write headline for current cost type
        detailed_costs = detailed_costs + f"\n **{cost_types[cost_type]}:** \n"

        # iterate over all cost items
        for item, value in cost_items.items():

            # write line with bulletpoint for current cost item
            if value > 0:
                detailed_costs = (
                    detailed_costs
                    + f"\n * **Cost of {simulation.factory.get_name(item)}:** {value}{currency}\n"
                )
            else:
                detailed_costs = (
                    detailed_costs
                    + f"\n * **Revenue from {simulation.factory.get_name(item)}:** {value}{currency}\n"
                )

    return detailed_costs
