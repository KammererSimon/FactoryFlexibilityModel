# This script is called on the following paths:
# -> fm.dash.create_dash() -> update_plots_overview()


def create_emission_overview(simulation):
    """
    This function takes a simulation object and creates a simple string that contains a formatted list of all the costs factors that determine the target function value of the solved simulation.

    :param simulation: [fm.simulation-object]
    :return: [str]
    """

    # get emission results from simulation
    emissions = simulation.result["total_emissions"]

    # initialize string
    detailed_emissions = "**Emission Sources:**"


    # iterate oer all components
    for component in simulation.factory.components.values():
        # only continue for sources and sinks
        if component.type in ["source", "sink"]:
            #calculate total emissions
            component_emissions = sum(simulation.result[component.key]["emissions"])
            if component_emissions > 0:
                # add line with component emissions to the string if the source or sink caused emissions
                detailed_emissions = detailed_emissions + f"\n * **{simulation.factory.get_name(component.key)}:** {round(component_emissions/1000,2)} tCO2\n"

    detailed_emissions = detailed_emissions + f"\n * **Total Emissions:** {round(sum(simulation.result['total_emissions'])/1000, 2)} tCO2\n"

    # return created string
    return detailed_emissions
