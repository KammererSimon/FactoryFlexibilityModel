#  CALLING PATH:
#  -> Simulation.simulate() -> Simulation.create_optimization_problem()

# IMPORTS
import logging


# CODE START
def add_deadtime(simulation, component):
    """
    This function adds all necessary MVARS and constraints to the optimization problem that are
    required to integrate the deadtime handed over as 'Component'

    :param component: components.deadtime-object
    :return: simulation.m is beeing extended
    """

    # calculate the number of timesteps required to match the scenario - timescale:
    delay = component.delay / simulation.time_reference_factor
    if not delay % 1 == 0:
        logging.warning(
            f"Warning: The delay of {component.name} has been rounded to {delay}, since to clean conversion to the scenario timestep length is possible"
        )
    delay = int(delay)

    # check, if the deadtime is slacked:
    if len(component.outputs) == 1:
        # no slacks...
        # set output_flow = slack for start interval
        simulation.m.addConstr(simulation.MVars[component.outputs[0].key][0:delay] == 0)

        # set output(t) = validate(t-delay) for middle interval
        simulation.m.addConstr(
            simulation.MVars[component.outputs[0].key][delay : simulation.T]
            == simulation.MVars[component.inputs[0].key][0 : simulation.T - delay]
        )

        # set validate(t) = slack for end interval
        simulation.m.addConstr(
            simulation.MVars[component.inputs[0].key][
                simulation.T - delay : simulation.T - 1
            ]
            == 0
        )

    else:
        # set output_flow = slack for start interval
        simulation.m.addConstrs(
            simulation.MVars[component.outputs[1].key][t]
            == simulation.MVars[component.inputs[0].key][t]
            for t in range(delay)
        )

        # set output(t) = validate(t-delay) for middle interval
        simulation.m.addConstrs(
            simulation.MVars[component.outputs[1].key][t + delay]
            == simulation.MVars[component.inputs[1].key][t]
            for t in range(simulation.T - delay)
        )

        # set validate(t) = slack for end interval
        simulation.m.addConstrs(
            simulation.MVars[component.inputs[1].key][simulation.T - t - 1]
            == simulation.MVars[component.outputs[0].key][t]
            for t in range(delay)
        )
