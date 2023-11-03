# CALCULATE SENSITIVITIES
# This script is used to do sensitivity-analysis on a factory layout.
# The main function is calculate_sensitivities(factory, scenarios, **kwargs), which you can hand over a factory layout,
# a list of scenarios and a list of sensitivities you want to analyze. The script then optimizes the factory in all
# given scenarios and with all specified sensitivities and returns a list with all the results.

from factory_flexibility_model.io import input_validations as iv

# IMPORT ENDOGENOUS COMPONENTS
from factory_flexibility_model.simulation import simulation as sm


# MAIN FUNCTIONS
def calculate_sensitivities(factory, scenarios, **kwargs):
    """
    This function takes a factory layout, a list of scenarios and a list of factory variations (called sensitivities).
    It performs the factory Simulation for all combination of factories and scenarios implied in the given data
    :param factory: factory_model.factory - object
    :param scenarios: list of scenario.scenario-objects
    :param kwargs:   only possible kwarg: "sensitivities" = list of component parameter variations in the format:
                           sensitivities[""] = {component, attribute_name, value_min, value_max, number_of_steps)
    :return: list with all simulated factory.simulation_objects
    """

    # TODO: Write some validate validation!

    # check if logging shall be enabled
    log = False
    if "enable_log" in kwargs:
        log = iv.validate(kwargs["enable_log"], "boolean")

    # check, if there are any sensitivities handed over
    if "sensitivities" not in kwargs:

        # write log_simulation
        if log:
            print(
                "No sensitivities were handed over. Calculations will just handle different scenarios"
            )

        # if no: just calculate the given factory in all given scenarios
        results = __calculate_scenarios(factory, scenarios)

    else:
        # if yes: make sure that the kwargs attribute is not empty
        if not kwargs["sensitivities"]:
            raise Exception("ERROR: The given list of sensitivities is empty!")

        # write log_simulation
        if log:
            print(
                "Sensitivities have been specified. Starting the recursive factory alternation"
            )

        # start the recursive scenario-building
        results = __recursive_simulation_setup(
            factory, {}, scenarios, kwargs["sensitivities"], log
        )

    # write log_simulation
    if log:
        print(
            f"Simulations finished. A total of {len(results)} calculations has been performed."
        )

    # return the results
    return results


# UTILITY FUNCTIONS
def __recursive_simulation_setup(
    factory, simulation_description, scenarios, sensitivities, log
):
    """
    This function calls itself in a recursion to build all the desired scenario- and factory sensitivities.
    Every layer sweeps through one parameter and then calls the function again for the next one.
    If one call gets the last remaining sensitivity it calls the .__calculate_scenarios()-function to optimize the
    current factory layout in all existing scenarios. The results are collected and returned as a list
    :param factory: factory_model.factory - object
    :param simulation_description: a dictionary that keeps track of all the variations that are applied to a factory
                                during the recursive alternation process
    :param scenarios: list of scenario.scenario-objects
    :param sensitivities:   list of component parameter variations in the format:
                            {component, attribute_name, value_min, value_max, number_of_steps}
    :return: a list with all simulated factory_simulation.Simulation-objects
    """

    # initialize a variable to collect results
    result = []

    # take the first sensitivity of the current list
    sensitivity = sensitivities[0]

    # iterate over the parameter range of the current attribute with the desired number of steps
    for i_step in range(sensitivity["number_of_steps"]):

        # calculate next value for current parameter
        parameter_value_i = (
            sensitivity["value_min"]
            + (sensitivity["value_max"] - sensitivity["value_min"])
            / (sensitivity["number_of_steps"] - 1)
            * i_step
        )

        # add the current sensitivity and the next parameter value to the simulation_description
        simulation_description[
            f"{sensitivity['component']}.{sensitivity['attribute']}"
        ] = parameter_value_i

        # set the desired parameter to the next value:
        kwargs = {sensitivity["attribute"]: parameter_value_i}
        factory.set_configuration(sensitivity["component"], **kwargs)

        # check, if there are any further sensitivities to handle:
        if len(sensitivities) > 1:
            # call the next recursion level for the next sensitivity
            result = result + __recursive_simulation_setup(
                factory, simulation_description, scenarios, sensitivities[1:], log
            )

        # if no: start calculations
        else:

            # calculate the current factory layout in all scenarios
            result += __calculate_scenarios(
                factory, simulation_description, scenarios, log
            )

    # return all collected results
    return result


def __calculate_scenarios(factory, simulation_description, scenarios, log):
    """
    This function takes a factory and a list of scenarios. It simulates the given factory within all scenarios and
    returns a list with all solved Simulation objects
    :param factory: factory_model.factory-object
    :param scenarios: list of factory_scenario.scenario-objects
    :return: list of solved factory_simulation.Simulation-objects
    """

    # initialize a variable to collect the results
    results = []

    # iterate over all scenarios
    for scenario in scenarios:

        # add the name of the current scenario to the simulation_description
        simulation_description["Scenario"] = scenario.name

        # write log_simulation
        if log:
            print(f"Simulating {simulation_description}")

        # create a new Simulation object
        simulation = sm.Simulation(
            factory, scenario, enable_simulation_log=False, enable_solver_log=False
        )

        # solve the Simulation
        simulation.simulate(treshold=0.00001)

        # append the last Simulation result to the list of solved simulations
        results = results + [
            {"Simulation": simulation, "description": simulation_description.copy()}
        ]

    # return th results
    return results
