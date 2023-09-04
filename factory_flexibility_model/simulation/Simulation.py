# FACTORY SIMULATION
# This Script contains the Simulation class of the factory factory. It is used to store Factory-Scenario-Combinations and to perform the Simulation itself on them
# The following Methods are meant to be used by external Scripts to prepare a Simulation:
# self.__init__
# self.set_factory
# self.set_name
# self.set_scenario

# The Simulation itself is conducted by the Method:
# self.simulate
# -> This method calls all the other internal functions to build an optimization problem out of the components specified in the factory

# To get the results use:
# self.create_dash
# self.show_results

# IMPORTS
import logging
import pickle
import time
from datetime import datetime
from pathlib import Path

import gurobipy as gp
import numpy as np
from gurobipy import GRB

import factory_flexibility_model.input_validations as iv
from factory_flexibility_model.ui import dash as fd

logging.basicConfig(level=logging.WARNING)


class Simulation:
    def __init__(
        self,
        *,
        scenario=None,
        factory=None,
        enable_time_tracking=False,
        name="Unspecified Simulation",
    ):
        """
        :param enable_time_tracking: Set to true if you want to track the time required for Simulation
        """
        # set general data for the Simulation
        self.date_simulated = None
        self.enable_time_tracking = enable_time_tracking
        self.factory = factory  # Variable to store the factory for the Simulation
        self.interval_length = None  # realtime length of one Simulation interval...to be taken out of the scenario
        self.info = None  # Free attribute to store additional information
        self.m = None  # Placeholder for the Gurobi-Model to be created
        self.name = name
        self.scenario = scenario  # Variable to store the scenario for the Simulation
        self.simulated = False  # Tracks, if the Simulation has been calculated or not
        self.simulation_result = (
            None  # Variable for storing the results of the Simulation
        )
        self.simulation_valid = None  # Is being set by self.validate_results
        self.T = None  # To be set during Simulation
        self.time_reference_factor = None  # To be set during Simulation

        # initialize tracking of resulting problem class
        self.problem_class = {
            "grade": 1,
            "type": "float",
        }  # variable to keep track of the resulting problem class - used for logging purposes

        # create timestamp of Simulation setup
        now = datetime.now()
        self.date_created = now.strftime(
            "%d/%m/%Y %H:%M:%S"
        )  # date/time of the creation of the Simulation object

    def __add_converter(self, component):
        """
        This function adds all necessary MVARS and constraints to the optimization problem that are
        required to integrate the converter handed over as 'Component'
        :param component: components.converter-object
        :return: self.m is beeing extended
        """
        # create a timeseries of decision variables to represent the utilization U(t)
        self.MVars[f"P_{component.key}"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"P_{component.name}"
        )
        logging.debug(
            f"        - Variable:     P_{component.key} timeseries of the nominal power of {component.name}"
        )

        # add variables to express the positive and negative deviations from the nominal operating point
        self.MVars[f"P_{component.key}_devpos"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"P_{component.name}_devpos"
        )
        self.MVars[f"P_{component.key}_devneg"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"P_{component.name}_devneg"
        )

        # is the operating power of the converter limited? If yes: add power_max and power_min constraints
        if component.power_max_limited:
            self.m.addConstr(
                self.MVars[f"P_{component.key}"]
                <= component.power_max * component.availability
            )
            logging.debug(
                f"        - Constraint:   P_{component.key} <= P_{component.name}_max"
            )

        if component.power_min_limited:
            self.m.addConstr(
                self.MVars[f"P_{component.key}"]
                >= component.power_min * component.availability
            )
            logging.debug(
                f"        - Constraint:   P_{component.key} >= P_{component.key}_min"
            )

        # Calculate the efficiency of operation for each timestep based on the deviations
        self.MVars[f"Eta_{component.key}"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"Eta_{component.name}"
        )
        logging.debug(
            f"        - Variable:     Eta_{component.key}                              "
            f"(Operating efficiency of {component.name}"
        )

        if component.eta_variable:
            if self.problem_class["grade"] < 2:
                self.problem_class["grade"] = 2
            self.m.addConstrs(
                self.MVars[f"Eta_{component.key}"][t]
                == component.eta_max
                - self.MVars[f"P_{component.key}_devpos"][t] * component.delta_eta_high
                - self.MVars[f"P_{component.key}_devneg"][t] * component.delta_eta_low
                for t in range(self.T)
            )
            logging.debug(
                f"        - Constraint:   Calculate Eta(t) for {component.name}"
            )
        else:
            self.m.addConstrs(
                self.MVars[f"Eta_{component.key}"][t] == 1 for t in range(self.T)
            )
            logging.debug(
                f"        - Constraint:   Eta(t) for {component.name} fixed to 100%"
            )

        # calculate the absolute operating point out of the nominal operating point, the deviations and the switching state
        # Can the Converter be turned on/off regardless of the power constraints?
        if component.switchable:
            self.problem_class["type"] = "mixed integer"
            # introduce a variable representing the switching state of the converter
            self.MVars[f"Bool_{component.key}_state"] = self.m.addMVar(
                self.T, vtype=GRB.BINARY, name=f"{component.name}_state"
            )

            # calculate the operating point concerning the switching state
            self.m.addConstrs(
                self.MVars[f"P_{component.key}"][t]
                == (
                    component.power_nominal
                    - self.MVars[f"P_{component.key}_devneg"][t]
                    + self.MVars[f"P_{component.key}_devpos"][t]
                )
                * self.MVars[f"Bool_{component.key}_state"][t]
                for t in range(self.T)
            )
        else:
            # calculate the operating point without a switching state
            self.m.addConstr(
                self.MVars[f"P_{component.key}"]
                == component.power_nominal
                - self.MVars[f"P_{component.key}_devneg"]
                + self.MVars[f"P_{component.key}_devpos"]
            )

        # set ramping constraints if needed:
        if component.ramp_power_limited:
            self.m.addConstr(
                self.MVars[f"P_{component.key}"][1 : self.T]
                <= self.MVars[f"P_{component.key}"][0 : self.T - 1]
                + component.max_pos_ramp_power
            )  # restrict ramping up
            self.m.addConstr(
                self.MVars[f"P_{component.key}"][1 : self.T]
                >= self.MVars[f"P_{component.key}"][0 : self.T - 1]
                - component.max_neg_ramp_power
            )  # restrict ramping down
            logging.debug(
                f"        - Constraint:   Ramping constraints for {component.name}"
            )

        # set the flows of incoming connections
        for connection in component.inputs:
            self.m.addConstr(
                self.MVars[connection.key]
                == self.MVars[f"P_{component.key}"]
                * connection.weight_sink
                * self.interval_length
            )

        # set the flows of outgoing connections
        for connection in component.outputs:
            if connection.flowtype.is_energy():
                self.m.addConstr(
                    self.MVars[connection.key]
                    == self.MVars[f"P_{component.key}"]
                    * connection.weight_source
                    * self.interval_length
                    * self.MVars[f"Eta_{component.key}"]
                )
                logging.debug(
                    f"        - added energy output calculation with losses for {connection.name}"
                )
            else:
                self.m.addConstr(
                    self.MVars[connection.key]
                    == self.MVars[f"P_{component.key}"]
                    * connection.weight_source
                    * self.interval_length
                )
                logging.debug(
                    f"        - added material output calculation for {connection.name}"
                )

        # calculate the resulting energy losses: losses(t) = sum(inputs(t)) - sum(outputs(t))
        self.m.addConstr(
            self.MVars[component.to_Elosses.key]
            == sum(self.MVars[input_i.key] for input_i in component.inputs_energy)
            - sum(self.MVars[output_i.key] for output_i in component.outputs_energy)
        )

        # calculate the resulting material losses: losses(t) = sum(inputs(t)) - sum(outputs(t))
        if not component.to_Mlosses == []:
            self.m.addConstr(
                self.MVars[component.to_Mlosses.key]
                == sum(self.MVars[input_i.key] for input_i in component.inputs_material)
                - sum(
                    self.MVars[output_i.key] for output_i in component.outputs_material
                )
            )

    def __add_deadtime(self, component):
        """
        This function adds all necessary MVARS and constraints to the optimization problem that are
        required to integrate the deadtime handed over as 'Component'
        :param component: components.deadtime-object
        :return: self.m is beeing extended
        """

        # calculate the number of timesteps required to match the scenario - timescale:
        delay = component.delay / self.time_reference_factor
        if not delay % 1 == 0:
            logging.warning(
                f"Warning: The delay of {component.name} has been rounded to {delay}, since to clean conversion to the scenario timestep length is possible"
            )
        delay = int(delay)

        # check, if the deadtime is slacked:
        if len(component.outputs) == 1:
            # no slacks...
            # set output_flow = slack for start interval
            self.m.addConstr(self.MVars[component.outputs[0].key][0:delay] == 0)

            # set output(t) = validate(t-delay) for middle interval
            self.m.addConstr(
                self.MVars[component.outputs[0].key][delay : self.T]
                == self.MVars[component.inputs[0].key][0 : self.T - delay]
            )

            # set validate(t) = slack for end interval
            self.m.addConstr(
                self.MVars[component.inputs[0].key][self.T - delay : self.T - 1] == 0
            )

        else:
            # set output_flow = slack for start interval
            self.m.addConstrs(
                self.MVars[component.outputs[1].key][t]
                == self.MVars[component.inputs[0].key][t]
                for t in range(delay)
            )

            # set output(t) = validate(t-delay) for middle interval
            self.m.addConstrs(
                self.MVars[component.outputs[1].key][t + delay]
                == self.MVars[component.inputs[1].key][t]
                for t in range(self.T - delay)
            )

            # set validate(t) = slack for end interval
            self.m.addConstrs(
                self.MVars[component.inputs[1].key][self.T - t - 1]
                == self.MVars[component.outputs[0].key][t]
                for t in range(delay)
            )

    def __add_schedule(self, component):
        """
        This function adds all necessary MVARS and constraints to the optimization problem that are
        required to integrate the schedule handed over as 'Component'
        :param component: components.schedule-object
        :return: self.m is beeing extended
        """

        # get number of individual flexible demands:
        rows = len(component.demands)

        # create availability matrix for the demands
        availability = np.zeros((self.T, rows))
        for row in range(rows):
            for column in range(
                component.demands[row, 0], component.demands[row, 1] + 1
            ):
                availability[column - 1, row] = 1
        self.MVars[f"X_{component.key}_availability"] = availability

        # create decision variables for the demands
        self.MVars[f"E_{component.key}_in"] = self.m.addMVar(
            (self.T, rows), vtype=GRB.CONTINUOUS, name=f"{component.name}_Pin"
        )
        logging.debug(
            f"        - Variable(s):  Ein for {rows} part demands of {component.name}"
        )

        # define constraint: validate and output must be equal at any timestep to ensure, that the Component just does flowtype control
        self.m.addConstr(
            self.MVars[component.outputs[0].key] == self.MVars[component.inputs[0].key]
        )
        logging.debug(f"        - Constraint:   E_in == E_out for {component.name}")
        # TODO: doesnt this have to be fulfilled for every timestep??!

        # define constraint: taken inputs for demand fulfillment must equal the used validate in every timestep
        self.m.addConstrs(
            gp.quicksum(self.MVars[f"E_{component.key}_in"][t][:])
            == self.MVars[component.inputs[0].key][t]
            for t in range(self.T)
        )
        logging.debug(
            f"        - Constraint:   E_demands must be fed by inputs within {component.name}"
        )

        # define constraint: each part demand d must have it's individual demand fulfilled
        self.m.addConstrs(
            self.MVars[f"E_{component.key}_in"][0 : self.T, i]
            @ availability[0 : self.T, i]
            == component.demands[i, 2]
            for i in range(rows)
        )
        logging.debug(
            f"        - Constraint:   Each part demand of {component.name} must have its demand fulfilled"
        )

        # define constraint: adhere power_max constraints per part demand
        self.m.addConstrs(
            self.MVars[f"E_{component.key}_in"][t, i] / self.interval_length
            <= component.demands[i, 3]
            for t in range(self.T)
            for i in range(rows)
        )
        logging.debug(
            f"        - Constraint:   Adhere the power_max constraints for every part demand of {component.name}"
        )

        # define constraint: adhere power_max for total power if needed
        if component.power_max_limited:
            self.m.addConstrs(
                gp.quicksum(self.MVars[f"E_{component.key}_in"][t][:])
                / self.interval_length
                <= component.power_max[t]
                for t in range(self.T)
            )
            logging.debug(
                f"        - Constraint:   power_total(t) <= power_max for {component.name}"
            )

    def __add_pool(self, component):
        """
        This function adds all necessary MVARS and constraints to the optimization problem that are
        required to integrate the pool handed over as 'Component'
        :param component: components.pool-object
        :return: self.m is beeing extended
        """
        # create constraint that ensures, that the sum of inputs equals the sum of outputs in every timestep
        self.m.addConstr(
            gp.quicksum(
                self.MVars[component.inputs[input_id].key]
                for input_id in range(len(component.inputs))
            )
            == gp.quicksum(
                self.MVars[component.outputs[output_id].key]
                for output_id in range(len(component.outputs))
            )
        )
        logging.debug(
            f"        - Constraint:   Energy equilibrium for Pool {component.name}"
        )

    def __add_sink(self, component):
        """
        This function adds all necessary MVARS and constraints to the optimization problem that are
        required to simulate the sink handed over as 'Component'
        :param component: components.sink-object
        :return: self.m is beeing extended
        """
        # Sinks may be determined in their power intake or the power consumption may be calculated during the optimization.
        # In the first case a constraint is created, that forces all connected inputs to meet the desired power in total
        # In the second case a MVar reflecting the resulting inflow is created, together with a constraint to calculate it

        # create a timeseries of decision variables to represent the total inflow (energy/material) going into the sink
        self.MVars[f"E_{component.key}"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"E_{component.name}"
        )
        logging.debug(
            f"        - Variable:     E_{component.key}                                  (timeseries of global outflows to {component.name}"
        )

        if component.determined:
            # set the sum of incoming flows to meet the power demand
            self.m.addConstr(
                gp.quicksum(
                    component.inputs[o].weight_sink
                    * self.MVars[component.inputs[o].key]
                    for o in range(len(component.inputs))
                )
                == component.demand
            )
            logging.debug(
                f"        - Constraint:   Sum of incoming flows == determined total demand              (E_{component.name} determined by timeseries)"
            )

        # add constraints to calculate the total outflow from the system as the sum of all weighted energys of incoming connections
        self.m.addConstr(
            gp.quicksum(
                self.MVars[component.inputs[o].key]
                for o in range(len(component.inputs))
            )
            == self.MVars[f"E_{component.key}"]
        )
        logging.debug(
            f"        - Constraint:   E_{component.key} == sum of incoming flows"
        )

        # is the maximum output power of the sink limited? If yes: Add power_max constraint
        if component.power_max_limited:
            self.m.addConstr(
                self.MVars[f"E_{component.key}"]
                <= component.power_max * component.availability * self.interval_length
            )
            logging.debug(
                f"        - Constraint:   P_{component.key} <= P_{component.name}_max"
            )

        # is the minimum output power of the source limited? If yes: Add power_min constraint
        if component.power_min_limited:
            self.m.addConstrs(
                self.MVars[f"E_{component.key}"] / self.interval_length
                >= component.power_min[t]
                for t in range(self.T)
            )
            logging.debug(
                f"        - Constraint:   P_{component.key} >= P_{component.key}_min"
            )

        # does the utilization of the sink cost something? If yes: Add the corresponding cost factors
        if component.chargeable:
            self.C_objective.append(
                self.m.addMVar(1, vtype=GRB.CONTINUOUS, name=f"C_{component.key}")
            )
            self.m.addConstr(
                self.C_objective[-1]
                == component.cost[0 : self.T] @ self.MVars[f"E_{component.key}"]
            )
            logging.debug(
                f"        - CostFactor:   Cost for dumping into {component.name}"
            )

        # does the utilization of the sink create revenue? If yes: Add the corresponding negative cost factors
        if component.refundable:
            self.R_objective.append(
                self.m.addMVar(1, vtype=GRB.CONTINUOUS, name=f"R_{component.key}")
            )
            self.m.addConstr(
                self.R_objective[-1]
                == component.revenue[0 : self.T] @ self.MVars[f"E_{component.key}"]
            )
            logging.debug(
                f"        - CostFactor:   Revenue for sales generated by {component.name}"
            )

        if component.avoids_emissions:
            # avoided emissions
            self.R_objective.append(
                self.m.addMVar(
                    1, vtype=GRB.CONTINUOUS, name=f"R_{component.key}_emissions"
                )
            )
            self.m.addConstr(
                self.R_objective[-1]
                == component.co2_refund_per_unit[0 : self.T]
                @ self.MVars[f"E_{component.key}"]
                * self.scenario.cost_co2_per_kg
            )
            logging.debug(
                f"        - CostFactor:   Revenue from reduced CO2-emissions due to usage of {component.name}"
            )
        if component.causes_emissions:
            # additional emissions
            self.C_objective.append(
                self.m.addMVar(
                    1, vtype=GRB.CONTINUOUS, name=f"C_{component.key}_emissions"
                )
            )
            self.m.addConstr(
                self.C_objective[-1]
                == component.co2_emission_per_unit[0 : self.T]
                @ self.MVars[f"E_{component.key}"]
                * self.scenario.cost_co2_per_kg
            )
            logging.debug(
                f"        - CostFactor:   Costs for CO2-emissions due to usage of {component.name}"
            )

    def __add_slack(self, component):
        """
        This function adds all necessary MVARS and constraints to the optimization problem that are
        required to integrate the slack handed over as 'Component'
        :param component: components.slack-object
        :return: self.m is beeing extended
        """
        # slacks don't need any power restrictions or other constraints.
        # All they basically have to do is to be usable in any situation but be very expensive then.
        # So just two cost terms are being created here

        # add a cost term for negative slack usage to the target function
        for i in range(len(component.inputs)):
            self.C_objective.append(
                self.m.addMVar(1, vtype=GRB.CONTINUOUS, name=f"C_{component.key}_neg")
            )
            self.m.addConstr(
                self.C_objective[-1]
                == component.cost[0 : self.T]
                @ self.MVars[component.inputs[i].key][0 : self.T]
            )
            logging.debug(f"        - CostFactor:   C_{component.key}_negative")

        # add a cost term for negative slack usage to the target function
        for i in range(len(component.outputs)):
            self.C_objective.append(
                self.m.addMVar(1, vtype=GRB.CONTINUOUS, name=f"C_{component.key}_pos")
            )
            self.m.addConstr(
                self.C_objective[-1]
                == component.cost[0 : self.T]
                @ self.MVars[component.outputs[i].key][0 : self.T]
            )
            logging.debug(f"        - CostFactor:   C_{component.key}_positive")

    def __add_storage(self, component):
        """
        This function adds all necessary MVARS and constraints to the optimization problem that are
        required to integrate the slack handed over as 'Component'
        :param component: components.slack-object
        :return: self.m is beeing extended
        """
        # create  variable for initial SOC
        self.MVars[f"SOC_{component.key}_start"] = self.m.addMVar(
            1, vtype=GRB.CONTINUOUS, name=f"SOC_{component.key}_start"
        )
        if component.soc_start_determined:
            self.m.addConstr(
                self.MVars[f"SOC_{component.key}_start"] == component.soc_start
            )
            logging.debug(
                f"        - Constraint:   SOC_start == {component.soc_start} for storage {component.key}"
            )
        else:
            self.m.addConstr(self.MVars[f"SOC_{component.key}_start"] <= 1)
            logging.debug(
                f"        - Variable:     SOC_start for storage {component.name}"
            )

        # create variable for Echarge
        self.MVars[f"E_{component.key}_charge"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"E_{component.key}_charge"
        )
        self.m.addConstr(
            self.MVars[f"E_{component.key}_charge"]
            == gp.quicksum(
                self.MVars[component.inputs[input_id].key]
                for input_id in range(len(component.inputs))
            )
        )
        logging.debug(f"        - Variable:     ECharge for storage {component.key} ")

        # create variable for Edischarge
        self.MVars[f"E_{component.key}_discharge"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"E_{component.key}_discharge"
        )
        self.m.addConstr(
            self.MVars[f"E_{component.key}_discharge"]
            == gp.quicksum(
                self.MVars[component.outputs[output_id].key]
                + self.MVars[component.to_losses.key]
                for output_id in range(len(component.outputs))
            )
        )
        logging.debug(
            f"        - Variable:     EDischarge for storage {component.name} "
        )

        # create variable for SOC
        self.MVars[f"SOC_{component.key}"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"SOC_{component.key}"
        )
        logging.debug(f"        - Variable:     SOC for storage {component.name} ")

        # calculate SOC for every timestep using cumsum + SOC_start
        cumsum_matrix = np.tril(
            np.ones(self.T)
        )  # create a matrix with ones on- and under the main diagonal to quickly perform cumsum-calculations in matrix form
        self.m.addConstr(
            self.MVars[f"SOC_{component.key}"]
            == cumsum_matrix
            @ (
                self.MVars[f"E_{component.key}_charge"]
                - self.MVars[f"E_{component.key}_discharge"]
            )
            + component.capacity * self.MVars[f"SOC_{component.key}_start"][0]
        )

        logging.debug(
            f"        - Constraint:   Calculate SOC_end(t) for storage {component.name} "
        )

        # set SOC_end = SOC_start
        self.m.addConstr(
            self.MVars[f"SOC_{component.key}"][self.T - 1]
            == self.MVars[f"SOC_{component.key}_start"][0] * component.capacity
        )
        logging.debug(
            f"        - Constraint:   SOC_end == SOC_start for storage {component.name}"
        )

        # don't violate the capacity boundary: cumsum of all inputs and outputs plus initial soc must not be more than the capacity in any timestep
        self.m.addConstr(self.MVars[f"SOC_{component.key}"] <= component.capacity)
        logging.debug(
            f"        - Constraint:   Cumsum(E) <= Capacity for {component.name} "
        )

        # don't take out more than stored: cumsum of all inputs and outputs plus initial soc must be more than zero in any timestep
        self.m.addConstr(self.MVars[f"SOC_{component.key}"] >= 0)
        logging.debug(f"        - Constraint:   Cumsum(E) >= 0 for {component.name} ")

        # create Pcharge_max-constraint
        if component.power_max_charge > 0:
            self.m.addConstr(
                self.MVars[f"E_{component.key}_charge"]
                <= component.power_max_charge * self.interval_length
            )
            logging.debug(
                f"        - Constraint:   power_charge <= power_charge_max for {component.name}"
            )

        # create Pdischarge_max-constraint
        if component.power_max_discharge > 0:
            self.m.addConstr(
                self.MVars[f"E_{component.key}_discharge"]
                <= component.power_max_discharge * self.interval_length
            )
            logging.debug(
                f"        - Constraint:   power_discharge <= power_discharge_max for {component.name}"
            )

        # create constraint to calculate the occuring losses if necessary
        if component.leakage_SOC > 0 or component.leakage_time > 0:
            soc_leakage = component.leakage_SOC**self.time_reference_factor
            lin_leakage = (
                component.leakage_time * component.capacity * self.time_reference_factor
            )
            self.m.addConstrs(
                (
                    self.MVars[component.to_losses.key][t]
                    == self.MVars[f"SOC_{component.key}"][t] * soc_leakage
                    + lin_leakage
                    + gp.quicksum(  # TODO: BUG! This creates problems once the storage is empty! #TODO: The introduction of the timefactor in the soc-term causes a difference between 1*1h and 4*0.25h simulations
                        self.MVars[component.outputs[output_id].key][t]
                        for output_id in range(len(component.outputs))
                    )
                    * (1 / component.efficiency - 1)
                )
                for t in range(self.T)
            )
            logging.debug(
                f"        - Constraint:   E_losses = E_discharge * (1-efficiency) for {component.name}"
            )

    def __add_source(self, component):
        """
        This function adds all necessary MVARS and constraints to the optimization problem that are
        required to integrate the source handed over as 'Component'
        :param component: components.source-object
        :return: self.m is being extended
        """

        # create a timeseries of decision variables to represent the total inflow coming from the source
        self.MVars[f"E_{component.key}"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"P_{component.key}"
        )

        logging.debug(
            f"        - Variable:     E_{component.key}                              (timeseries of global inputs from E_{component.name}"
        )

        # set the sum of outgoing flows to meet the fixed supply
        if component.determined:
            self.m.addConstr(
                gp.quicksum(
                    component.outputs[o].weight_source
                    * self.MVars[component.outputs[o].key]
                    for o in range(len(component.outputs))
                )
                == component.determined_power
            )

        # add constraints to calculate the total inflow to the system as the sum of all flows of connected regions
        self.m.addConstr(
            gp.quicksum(
                self.MVars[component.outputs[o].key]
                for o in range(len(component.outputs))
            )
            == self.MVars[f"E_{component.key}"]
        )

        logging.debug(
            f"        - Constraint:   E_{component.key} == sum of outgoing flows"
        )

        # is the maximum output power of the source limited? If yes: Add power_max constraint
        if component.power_max_limited:
            self.m.addConstr(
                gp.quicksum(
                    component.outputs[o].weight_source
                    * self.MVars[component.outputs[o].key]
                    for o in range(len(component.outputs))
                )
                / self.interval_length
                <= component.power_max * component.availability
            )
            logging.debug(
                f"        - Constraint:   P_{component.key} <= P_{component.key}_max"
            )
        elif self.factory.enable_slacks:
            self.m.addConstr(
                gp.quicksum(
                    component.outputs[o].weight_source
                    * self.MVars[component.outputs[o].key]
                    for o in range(len(component.outputs))
                )
                <= 10000000
            )
            logging.debug(
                f"        - Constraint:   P_{component.key} <= P_SECURITY                            -> Prevent Model from being unbounded"
            )

        # is the minimum output power of the source limited? If yes: Add power_min constraint
        if component.power_min_limited:
            self.m.addConstr(
                gp.quicksum(
                    component.outputs[o].weight_source
                    * self.MVars[component.outputs[o].key]
                    for o in range(len(component.outputs))
                )
                / self.interval_length
                >= component.power_min
            )

            logging.debug(
                f"        - Constraint:   P_{component.key} >= P_{component.key}_min"
            )

        # does the utilization of the source cost something? If yes: Add the corresponding cost factors
        if component.chargeable:
            self.C_objective.append(
                self.m.addMVar(1, vtype=GRB.CONTINUOUS, name=f"C_{component.key}")
            )
            self.m.addConstr(
                self.C_objective[-1]
                == component.cost[0 : self.T] @ self.MVars[f"E_{component.key}"]
            )
            logging.debug(f"        - CostFactor:   Cost for usage of {component.name}")

        # is the source afflicted with a capacity charge?
        # If yes: Add an MVar for the maximum used Power and add cost factor
        if component.capacity_charge > 0:

            # create single float Mvar
            self.MVars[f"P_max_{component.key}"] = self.m.addMVar(
                1, vtype=GRB.CONTINUOUS, name=f"P_max_{component.key}"
            )

            # define the Mvar as the maximum used output power
            self.m.addConstr(
                self.MVars[f"P_max_{component.key}"][0]
                == gp.max_(
                    (self.MVars[f"E_{component.key}"][t] for t in range(self.T)),
                    constant=0,
                )
            )

            # create new cost term
            self.C_objective.append(
                self.m.addMVar(
                    1, vtype=GRB.CONTINUOUS, name=f"C_Capacity_{component.key}"
                )
            )

            # define the costs -> capacity_charge is specified on yearly basis, so only
            self.m.addConstr(
                self.C_objective[-1]
                == self.interval_length
                * self.T
                / 8760
                * component.capacity_charge
                * self.MVars[f"P_max_{component.key}"]
            )

            logging.debug(
                f"        - CostFactor:   Cost for capacity charge of {component.name}"
            )

        # does the source cause direct or indirect emissions when used?
        if component.causes_emissions:
            # create new cost term for the emissions
            self.C_objective.append(
                self.m.addMVar(
                    1, vtype=GRB.CONTINUOUS, name=f"C_{component.key}_emissions"
                )
            )

            # calculate the costs
            self.m.addConstr(
                self.C_objective[-1]
                == component.co2_emissions_per_unit[0 : self.T]
                @ self.MVars[f"E_{component.key}"]
                * self.scenario.cost_co2_per_kg
            )

            logging.debug(
                f"        - CostFactor:   Cost for CO2-emissions due to usage of {component.name}"
            )

    def __add_thermalsystem(self, component):
        """
        This function adds all necessary MVARS and constraints to the optimization problem that are
        required to integrate the thermalsystem handed over as 'Component'
        :param component: components.thermalsystem-object
        :return: self.m is beeing extended
        """
        # create a timeseries of decision variables to represent the total inflow going into the thermal demand:
        self.MVars[f"E_{component.key}_in"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"E_{component.key}_in"
        )
        self.m.addConstrs(
            (
                self.MVars[f"E_{component.key}_in"][t]
                == gp.quicksum(
                    self.MVars[component.inputs[input_id].key][t]
                    for input_id in range(len(component.inputs))
                )
            )
            for t in range(self.T)
        )
        logging.debug(
            f"        - Variable:     E_{component.key}_in                                 (timeseries of incoming thermal energy at {component.name})"
        )

        # create a timeseries of decision variables to represent the total outflow going out of the thermal demand:
        self.MVars[f"E_{component.key}_out"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"E_{component.key}_out"
        )
        self.m.addConstrs(
            (
                self.MVars[f"E_{component.key}_out"][t]
                == gp.quicksum(
                    self.MVars[component.outputs[output_id].key][t]
                    for output_id in range(len(component.outputs))
                )
            )
            for t in range(self.T)
        )
        logging.debug(
            f"        - Variable:     E_{component.key}_out                                  (timeseries of removed thermal energy at {component.name})"
        )

        # create a timeseries for the internal temperature:
        self.MVars[f"T_{component.key}"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"T_{component.key}"
        )
        logging.debug(
            f"        - Variable:     T_{component.key}                                  (Internal Temperature of {component.name})"
        )

        # set the starting temperature:
        self.m.addConstr(
            self.MVars[f"T_{component.key}"][0] == component.temperature_start
        )
        logging.debug(f"        - Constraint:   T_{component.key}[0] = Tstart")

        # add constraint for the thermal R-C-factory
        self.m.addConstrs(
            (
                self.MVars[f"T_{component.key}"][t]
                == self.MVars[f"T_{component.key}"][t - 1]
                + (  # t-1 temperature
                    component.temperature_ambient[t - 1]
                    - self.MVars[f"T_{component.key}"][t - 1]
                )
                * self.time_reference_factor
                / (component.R * component.C)
                + (  # thermal inertia
                    self.MVars[f"E_{component.key}_in"][t - 1]
                    - self.MVars[f"E_{component.key}_out"][t - 1]
                )
                * self.time_reference_factor
                / component.C
            )
            for t in range(1, self.T)
        )  # heating/cooling impact

        # keep the temperature within the allowed boundaries during Simulation interval:
        self.m.addConstrs(
            (self.MVars[f"T_{component.key}"][t] >= component.temperature_min[t])
            for t in range(self.T)
        )
        self.m.addConstrs(
            (self.MVars[f"T_{component.key}"][t] <= component.temperature_max[t])
            for t in range(self.T)
        )
        logging.debug(
            f"        - Constraint:   Tmin < T_{component.key} < Tmax for {component.key}"
        )

        # set the end temperature:
        if component.sustainable:
            self.m.addConstr(
                self.MVars[f"T_{component.key}"][self.T - 1]
                + (
                    component.temperature_ambient[self.T - 1]
                    - self.MVars[f"T_{component.key}"][self.T - 1]
                )
                * self.time_reference_factor
                / (component.R * component.C)
                + (
                    self.MVars[f"E_{component.key}_in"][self.T - 1]
                    - self.MVars[f"E_{component.key}_out"][self.T - 1]
                )
                * self.time_reference_factor
                / component.C
                == component.temperature_start
            )
            logging.debug(f"        - Constraint:   T_{component.key}[T] = Tstart")
        else:
            # keep the temperature within allowed boundaries at timestep T+1
            self.m.addConstr(
                self.MVars[f"T_{component.key}"][self.T - 1]
                + (
                    component.temperature_ambient[self.T - 1]
                    - self.MVars[f"T_{component.key}"][self.T - 1]
                )
                * self.time_reference_factor
                / (component.R * component.C)
                + (
                    self.MVars[f"E_{component.key}_in"][self.T - 1]
                    - self.MVars[f"E_{component.key}_out"][self.T - 1]
                )
                * self.time_reference_factor
                / component.C
                >= component.temperature_min[self.T - 1]
            )

            self.m.addConstr(
                self.MVars[f"T_{component.key}"][self.T - 1]
                + (
                    component.temperature_ambient[self.T - 1]
                    - self.MVars[f"T_{component.key}"][self.T - 1]
                )
                * self.time_reference_factor
                / (component.R * component.C)
                + (
                    self.MVars[f"E_{component.key}_in"][self.T - 1]
                    - self.MVars[f"E_{component.key}_out"][self.T - 1]
                )
                * self.time_reference_factor
                / component.C
                <= component.temperature_max[self.T - 1]
            )

        # calculate the losses:
        self.m.addConstrs(
            self.MVars[component.to_losses.key][t]
            - self.MVars[component.from_gains.key][t]
            == (self.MVars[f"T_{component.key}"][t] - component.temperature_ambient[t])
            * self.time_reference_factor
            / component.R
            for t in range(self.T)
        )

        logging.debug(
            f"        - Constraint:     calculation of thermal losses for {component.name}"
        )

    def __add_triggerdemand(self, component):
        """
        This function adds all necessary MVARS and constraints to the optimization problem that are
        required to integrate the triggerdemand handed over as 'Component'
        :param component: components.triggerdemand-object
        :return: self.m is beeing extended
        """

        # create Matrix with all executable load-profiles
        possibilities = component.Tend - component.Tstart - component.profile_length + 2
        if component.input_energy:
            profiles_energy = np.zeros(
                [possibilities, component.Tend - component.Tstart + 1]
            )
        if component.input_material:
            profiles_material = np.zeros(
                [possibilities, component.Tend - component.Tstart + 1]
            )
        parallelcheck = np.zeros([possibilities, component.Tend - component.Tstart + 1])

        for i in range(possibilities):
            if component.input_energy:
                profiles_energy[
                    i, i : i + component.profile_length
                ] = component.load_profile_energy
            if component.input_material:
                profiles_material[
                    i, i : i + component.profile_length
                ] = component.load_profile_material
            parallelcheck[i, i : i + component.profile_length] = np.ones(
                component.profile_length
            )

        # create decision variable vector
        self.MVars[f"{component.key}_executions"] = self.m.addMVar(
            possibilities, vtype=GRB.INTEGER, name=f"{component.key}_executions"
        )
        logging.debug(
            f"        - Variable:     {component.key}_executions                                 (List of triggered events at triggerdemand {component.name})"
        )

        # guarantee the required amount of executions
        if component.executions > 0:
            self.m.addConstr(
                sum(self.MVars[f"{component.key}_executions"]) == component.executions
            )
            logging.debug(
                f"        - Constraint:     Guarantee the required amount of process executions at {component.name}"
            )

        # limit the number of parallel executions
        if component.max_parallel > 0:
            self.m.addConstr(
                parallelcheck.transpose() @ self.MVars[f"{component.key}_executions"]
                <= np.ones(component.Tend - component.Tstart + 1)
                * component.max_parallel
            )
            logging.debug(
                f"        - Constraint:   Limit the maximum parallel executions at {component.name}"
            )

        # calculate resulting load profile
        if component.input_energy:
            self.MVars[f"{component.key}_loadprofile_energy"] = self.m.addMVar(
                self.T,
                vtype=GRB.CONTINUOUS,
                name=f"{component.key}_loadprofile_energy",
            )
        if component.input_material:
            self.MVars[f"{component.key}_loadprofile_material"] = self.m.addMVar(
                self.T,
                vtype=GRB.CONTINUOUS,
                name=f"{component.key}_loadprofile_material",
            )
        logging.debug(
            f"        - Variable:     {component.key}_loadprofile                                 (resulting load profile of triggerdemand {component.name})"
        )

        if component.Tstart > 1:
            if component.input_energy:
                self.m.addConstr(
                    self.MVars[f"{component.key}_loadprofile_energy"][
                        : component.Tstart - 1
                    ]
                    == 0
                )
            if component.input_material:
                self.m.addConstr(
                    self.MVars[f"{component.key}_loadprofile_material"][
                        : component.Tstart - 1
                    ]
                    == 0
                )

        if component.input_energy:
            self.m.addConstr(
                self.MVars[f"{component.key}_loadprofile_energy"][
                    component.Tstart - 1 : component.Tend
                ]
                == profiles_energy.transpose()
                @ self.MVars[f"{component.key}_executions"]
            )
        if component.input_material:
            self.m.addConstr(
                self.MVars[f"{component.key}_loadprofile_material"][
                    component.Tstart - 1 : component.Tend
                ]
                == profiles_material.transpose()
                @ self.MVars[f"{component.key}_executions"]
            )

        if component.Tend < self.T:
            if component.input_energy:
                self.m.addConstr(
                    self.MVars[f"{component.key}_loadprofile_energy"][
                        component.Tend + 1 :
                    ]
                    == 0
                )
            if component.input_material:
                self.m.addConstr(
                    self.MVars[f"{component.key}_loadprofile_material"][
                        component.Tend + 1 :
                    ]
                    == 0
                )
        logging.debug(
            f"        - Constraint:   Calculate load profile at {component.name}"
        )

        # set validate and output connection to match the load profile
        if component.input_energy:
            self.m.addConstr(
                self.MVars[component.input_energy.key]
                == self.MVars[f"{component.key}_loadprofile_energy"]
                * self.interval_length
            )
            self.m.addConstr(
                self.MVars[component.output_energy.key]
                == self.MVars[f"{component.key}_loadprofile_energy"]
                * self.interval_length
            )
        if component.input_material:
            self.m.addConstr(
                self.MVars[component.input_material.key]
                == self.MVars[f"{component.key}_loadprofile_material"]
            )
            self.m.addConstr(
                self.MVars[component.output_material.key]
                == self.MVars[f"{component.key}_loadprofile_material"]
            )

    def __add_flows(self):
        """This function adds a MVar for the flowtype on every existing connection to te optimization problem
        :return: self.m is beeing extended
        """

        # iterate over all existing connections
        for connection in self.factory.connections.values():

            # create a timeseries of decision variables for the flowtype on every connection in the graph
            self.MVars[connection.key] = self.m.addMVar(
                self.T, vtype=GRB.CONTINUOUS, name=connection.key
            )

            logging.debug(
                f"        - Variable:     E_Flow_{connection.key}                                (timeseries of flowtype on connection {connection.name})"
            )

    def __collect_results(
        self, *, threshold: float = None, rounding_decimals: int = None
    ):
        """
        This function collects all the Simulation results of the Simulation object and writes them in a
        single dictionary under Simulation.results.
        :param threshold: [float] Threshold under which numerical values are considered as zero
        :param rounding_decimals: [int] Number of decimals that values are rounded to
        :return: self.results is being created
        """

        logging.info("COLLECTING RESULTS")

        # check, if Simulation has been conducted yet
        if not self.simulated:
            # if not: raise an Exception
            logging.critical(
                f"Cannot collect results for Simulation {self.name} because it has not been calculated yet"
            )
            raise Exception

        # initialize a dict to store all the results
        self.result = {}

        # Initialize threshold under which numeric results are interpreted as 0
        if threshold is None:
            threshold = 0

        # Initialize the number of decimals that the results are rounded to
        if rounding_decimals is None:
            rounding_decimals = 10

        # initialize counter- and summing variables:
        total_emissions = 0
        total_emission_cost = 0

        # collect timeseries of all flows in the factory: iterate over all connections
        for connection in self.factory.connections.values():

            # get the result timeseries for the current connection
            result_i = self.MVars[connection.key].X

            # apply threshold and round
            result_i = self.__apply_threshold_and_rounding(
                result_i, threshold, rounding_decimals
            )

            # write the result into the result-dictionary
            self.result[connection.key] = result_i

        # prepare summing variables for differentiation of onsite and offsite generation/consumption
        self.result["energy_generated_onsite"] = np.zeros(self.T)
        self.result["energy_generated_offsite"] = np.zeros(self.T)
        self.result["energy_consumed_onsite"] = np.zeros(self.T)
        self.result["energy_consumed_offsite"] = np.zeros(self.T)

        # collect all Component specific timeseries: iterate over all components
        for component in self.factory.components.values():

            # handle pools
            if component.type == "pool":

                # get the sum of the throughput as timeseries
                utilization = sum(
                    component.inputs[input_id].weight_sink
                    * self.MVars[component.inputs[input_id].key].X
                    for input_id in range(len(component.inputs))
                )

                # apply threshold and rounding
                utilization = self.__apply_threshold_and_rounding(
                    utilization, threshold, rounding_decimals
                )

                # write the results into the result dictionary
                self.result[component.key] = {"utilization": utilization}

            # handle converters
            if component.type == "converter":

                # get the result values, round them to the specified number of digits
                utilization = self.MVars[f"P_{component.key}"].X
                efficiency = self.MVars[f"Eta_{component.key}"].X

                # apply threshold and rounding on all values
                utilization = self.__apply_threshold_and_rounding(
                    utilization, threshold, rounding_decimals
                )
                efficiency = self.__apply_threshold_and_rounding(
                    efficiency, threshold, rounding_decimals
                )

                # write results into the result-dictionary
                self.result[component.key] = {
                    "utilization": utilization,
                    "efficiency": efficiency,
                }

            # handle sinks
            if component.type == "sink":

                # is the power of the sink determined?
                if component.determined:
                    # if yes: use the demand timeseries
                    utilization = component.demand[0 : self.T]

                else:
                    # if no: use the Simulation result
                    utilization = self.MVars[f"E_{component.key}"].X

                # apply rounding and threshold
                utilization = self.__apply_threshold_and_rounding(
                    utilization, threshold, rounding_decimals
                )

                # calculate the emissions avoided by the sink
                if component.avoids_emissions:
                    # if the sink can avoid emissions: calculate them
                    emissions = utilization * component.co2_refund_per_unit[0 : self.T]
                    emission_cost = sum(emissions) * self.scenario.cost_co2_per_kg

                    # add avoided costs and emissions to the summing variables
                    total_emissions -= emissions
                    total_emission_cost -= emission_cost

                    logging.info(
                        f"Sink {component.key} avoided total emissions of {round(sum(emissions), 2)} kgCO2, refunding {round(emission_cost, 2)}€"
                    )

                elif component.causes_emissions:
                    emissions = (
                        utilization * component.co2_emission_per_unit[0 : self.T]
                    )
                    emission_cost = sum(emissions) * self.scenario.cost_co2_per_kg

                    # add avoided costs and emissions to the summing variables
                    total_emissions += emissions
                    total_emission_cost += emission_cost

                    logging.info(
                        f"Sink {component.key} caused total emissions of {round(sum(emissions), 2)} kgCO2, costing {round(emission_cost, 2)}€"
                    )

                else:
                    # otherwise set zeros:
                    emissions = 0
                    emission_cost = 0

                # write the result into the result-dictionary
                self.result[component.key] = {
                    "utilization": utilization,
                    "emissions": emissions,
                    "emission_cost": emission_cost,
                }

                # add the sinks contribution to onsite/offsite demand calculation
                if component.is_onsite:
                    self.result["energy_consumed_onsite"] += self.result[component.key][
                        "utilization"
                    ]
                else:
                    self.result["energy_consumed_offsite"] += self.result[
                        component.key
                    ]["utilization"]

            # handle sources
            elif component.type == "source":

                # is the power of the source determined by a timeseries?
                if component.determined:
                    # if yes: use the given timeseries
                    utilization = component.determined_power[0 : self.T]
                else:
                    # if no: use Simulation result
                    utilization = self.MVars[f"E_{component.key}"].X

                # apply rounding and threshold
                utilization = self.__apply_threshold_and_rounding(
                    utilization, threshold, rounding_decimals
                )

                # calculate the emissions caused by the source
                if component.causes_emissions:
                    # if the source can generate emissions: calculate the emissions and the corresponding costs
                    emissions = (
                        utilization * component.co2_emissions_per_unit[0 : self.T]
                    )
                    emission_cost = sum(emissions) * self.scenario.cost_co2_per_kg

                    # add the emissions and cost to the summing variables:
                    total_emissions += emissions
                    total_emission_cost += emission_cost

                    logging.info(
                        f"Source {component.key} caused total emissions of {round(sum(emissions),2)} kgCO2, costing additional {round(emission_cost,2)}€"
                    )
                else:
                    emissions = 0
                    emission_cost = 0

                # write the result into the result-dictionary
                self.result[component.key] = {
                    "utilization": utilization,
                    "emissions": emissions,
                    "emission_cost": emission_cost,
                }

                # add the sources contribution to onsite/offsite generation calculation
                if component.is_onsite:
                    self.result["energy_generated_onsite"] += self.result[
                        component.key
                    ]["utilization"]
                else:
                    self.result["energy_generated_offsite"] += self.result[
                        component.key
                    ]["utilization"]

            # handle slacks
            elif component.type == "slack":
                # read the result timeseries of the Simulation
                sum_energy_pos = sum(
                    self.MVars[i_input.key].X[0 : self.T]
                    for i_input in component.inputs
                )
                sum_energy_neg = sum(
                    self.MVars[i_output.key].X[0 : self.T]
                    for i_output in component.outputs
                )
                utilization = sum(
                    self.MVars[i_input.key].X[0 : self.T]
                    for i_input in component.inputs
                ) - sum(
                    self.MVars[i_output.key].X[0 : self.T]
                    for i_output in component.outputs
                )

                # apply rounding and threshold
                sum_energy_pos = self.__apply_threshold_and_rounding(
                    sum_energy_pos, threshold, rounding_decimals
                )
                sum_energy_neg = self.__apply_threshold_and_rounding(
                    sum_energy_neg, threshold, rounding_decimals
                )
                utilization = self.__apply_threshold_and_rounding(
                    utilization, threshold, rounding_decimals
                )

                # write the results to the result dictionary
                self.result[component.key] = {
                    "EPos": sum_energy_pos,
                    "ENeg": sum_energy_neg,
                    "utilization": utilization,
                }

            # handle storages
            elif component.type == "storage":
                # read the result timeseries from the Simulation
                power_charge = (
                    self.MVars[f"E_{component.key}_charge"].X / self.interval_length
                )
                power_discharge = (
                    self.MVars[f"E_{component.key}_discharge"].X / self.interval_length
                )
                soc = self.MVars[f"SOC_{component.key}"].X
                soc_start = self.MVars[f"SOC_{component.key}_start"].X

                # apply rounding and threshold
                power_charge = self.__apply_threshold_and_rounding(
                    power_charge, threshold, rounding_decimals
                )
                power_discharge = self.__apply_threshold_and_rounding(
                    power_discharge, threshold, rounding_decimals
                )
                soc = self.__apply_threshold_and_rounding(
                    soc, threshold, rounding_decimals
                )
                soc_start = self.__apply_threshold_and_rounding(
                    soc_start, threshold, rounding_decimals
                )

                # write the results to the result dictionary
                self.result[component.key] = {
                    "Pcharge": power_charge,
                    "Pdischarge": power_discharge,
                    "SOC": soc,
                    "utilization": power_discharge - power_charge,
                    "SOC_start": soc_start,
                }

            # handle schedulers
            elif component.type == "schedule":
                # read the result timeseries from the Simulation
                utilization = self.MVars[f"E_{component.key}_in"].X
                availability = self.MVars[f"X_{component.key}_availability"]

                # apply rounding and threshold
                utilization = self.__apply_threshold_and_rounding(
                    utilization, threshold, rounding_decimals
                )
                availability = self.__apply_threshold_and_rounding(
                    availability, threshold, rounding_decimals
                )

                # write the results to the result dictionary
                self.result[component.key] = {
                    "utilization": utilization,
                    "availability": availability,
                }

            # handle thermalsystems
            elif component.type == "thermalsystem":
                # read the result timeseries from the Simulation
                utilization = (
                    self.MVars[f"E_{component.key}_in"].X
                    - self.MVars[f"E_{component.key}_out"].X
                )
                temperature = self.MVars[f"T_{component.key}"].X

                # apply rounding and threshold
                utilization = self.__apply_threshold_and_rounding(
                    utilization, threshold, rounding_decimals
                )
                temperature = self.__apply_threshold_and_rounding(
                    temperature, threshold, rounding_decimals
                )

                # write the results to the result dictionary
                self.result[component.key] = {
                    "utilization": utilization,
                    "temperature": temperature,
                }

            # handle triggerdemand
            elif component.type == "triggerdemand":
                pass
                # TODO: write result collection for triggerdemands

        # calculate self sufficiency
        if sum(self.result["energy_generated_onsite"]) > 0:
            self.result["self_sufficiency"] = sum(
                self.result["energy_generated_onsite"]
            ) / sum(self.result["energy_generated_onsite"])
        else:
            self.result["self_sufficiency"] = 0

        # write the total emission values to the result-dictionary
        self.result["total_emissions"] = total_emissions
        self.result["total_emission_cost"] = total_emission_cost

        # collect achieved costs/revenues (objective of target function - ambient_gain_punishment_term)
        self.result["objective"] = self.m.objVal - sum(
            self.result["ambient_gains"]["utilization"]
            * self.factory.components["ambient_gains"].cost[0 : self.T]
        )

        # validate results
        self.__validate_results()

        # set results_collected to true
        self.results_collected = True

        logging.info(" -> Results processed")

    def create_dash(self) -> object:
        """This function calls the factory_dash.create_dash()-routine to bring the dashboard online for the just conducted Simulation"""
        logging.info("CREATING DASHBOARD")
        fd.create_dash(self)

    def __read_scenario_data(self):
        """This function checks the factory for scenario paramater arguments and configures concerning
        components with the requested parameters from self.scenario"""

        # iterate components and search for scenario data keys
        for key, config in self.scenario.configurations.items():
            # set parameters for components
            if key in self.factory.components.keys():
                self.factory.set_configuration(key, parameters=config)

            # set weights of connections
            if key in self.factory.connections.keys():
                if "weight_sink" in config:
                    self.factory.connections[key].weight_sink = config["weight_sink"]
                if "weight_source" in config:
                    self.factory.connections[key].weight_sink = config["weight_source"]

            # set all configurations for the component
            # self.factory.set_configuration(component.key, parameters=required_configs)

            # iterate over all connections to get weights from scenario
            # for input_connection in component.inputs:
            #    if input_connection.weight_sink == "$parameter$":
            #        input_connection.weight_sink = self.scenario.parameters[
            #            f"{input_connection.key}/weight_sink"
            #        ]

            # for output_connection in component.outputs:
            #    if output_connection.weight_source == "$parameter$":
            #        output_connection.weight_source = self.scenario.parameters[
            #            f"{output_connection.key}/weight_source"
            #        ]

    def save(self, file_path: str, *, overwrite: bool = False):
        """
        This function saves a Simulation-object under the specified filepath as a single file.
        :param file_path: [string] Path to the file to be created
        :param override: [boolean] Set True to allow the method to overwrite existing files.
        Otherwise an error will occur when trying to overwrite a file
        :return: Nothing
        """

        # check, if file already exists
        file = Path(file_path)
        if file.is_file():
            if overwrite:
                logging.warning(
                    f"WARNING: The specified file already exists and will be overwritten"
                )
            else:
                logging.critical(
                    f"ERROR: The specified file already exists! Saving Factory aborted!"
                )
                raise Exception

        # create a copy of the Simulation without the gurobi_model
        simulation_data = self
        simulation_data.m = []
        simulation_data.MVars = []
        simulation_data.C_objective = []
        simulation_data.R_objective = []

        # save the factory at the given path
        with open(file_path, "wb") as f:
            pickle.dump(simulation_data, f)

        logging.info(f"SIMULATION SAVED under{file_path}")

    def set_factory(self, factory):
        """This function sets a factory_model.factory-object as the factory for the Simulation
        :param factory: [factory.factory] Factory-object to be simulated
        :return: [True] -> self.factory is set
        """

        self.factory = factory
        logging.debug("Factory for Simulation set")

    def set_name(self, name=str):
        """This function sets a name for the Simulation object
        :param name: [factory.factory] Factory-object to be simulated
        :return: [True] -> self.name is set
        """
        self.name = iv.validate(name, "string")

    def set_scenario(self, scenario):
        """This function sets a Simulation.scenario-object as the scenario for the Simulation
        :param scenario: [Simulation.scenario] Scenario-object to be used for Simulation
        :return: [True] -> self.scenario is set
        """
        self.scenario = scenario
        logging.debug("scenario for Simulation set")

    def simulate(
        self,
        *,
        threshold: float = None,
        rounding_decimals: int = None,
        log_solver: bool = False,
        solver_config: dict = {},
    ):
        """
        This function builds an optimization problem out of the factory and scenario and calls gurobi to solve it.
        :param solver_config: [dict] Optional dict with configuration parameters for the solver (max_solver_time, barrier_tolerance, solver_method)
        :param rounding_decimals: [int] Number of decimals that the results are rounded to
        :param threshold: [float] Threshold under whoch results are interpreted as zero
        :return: [True] -> Adds an attribute .result to the Simulation object
        """

        # ENABLE LOGGING/TIMETRACKING?
        if self.enable_time_tracking:
            self.t_start = time.time()

        # PREPARATIONS
        self.problem_class = {"grade": 1, "type": "float"}

        # Write timestamp
        now = datetime.now()
        self.date_simulated = now.strftime("%d/%m/%Y %H:%M:%S")  # write timestamp

        # Validate factory architecture
        self.__validate_factory_architecture()

        # Configure the timefactor as specified in the scenario:
        self.interval_length = (
            self.scenario.timefactor
        )  # The length of one Simulation timesten in hours is taken from the scenario
        self.T = self.factory.timesteps

        # calculate time_reference_factor
        self.time_reference_factor = (
            self.scenario.timefactor / self.factory.timefactor
        )  # a conversion factor that implies, how many factory related timesteps are represented by one Simulation timestep

        # writelog
        logging.debug(
            f"   Timefactor of the Simulation set to: 1 timestep == {self.scenario.timefactor} hours ({self.scenario.timefactor*60} minutes)"
        )

        # INITIALIZE GUROBI MODEL
        logging.info("INITIALIZING GUROBI")

        # create new gurobi model
        self.m = gp.Model("Factory")

        # initialize variables for collecting parts of the optimization problem
        self.MVars = {}  # Initialize a dict to store all the factory variables
        self.C_objective = (
            list()
        )  # List of cost terms that need to be summed up for the target function
        self.R_objective = (
            list()
        )  # List of revenue terms that need to be summed up for the target function

        # ADAPTING SCENARIO DATA
        logging.info("SETTING SCENARIO_DATA")
        self.__read_scenario_data()
        logging.debug(" -> Scenario data collection successful")

        # BUILDING OPTIMIZATION PROBLEM
        logging.info("BUILDING OPTIMIZATION PROBLEM")

        if self.enable_time_tracking:
            logging.info(f"Preperations: {round(time.time()-self.t_start,2)}s")
            self.t_step = time.time()

        # CREATE MVARS FOR ALL FLOWS IN THE FACTORY
        self.__add_flows()
        if self.enable_time_tracking:
            logging.info(f"Creating Flows: {round(time.time() - self.t_step, 2)}s")
            self.t_step = time.time()

        # CREATE MVARS AND CONSTRAINTS FOR ALL COMPONENTS IN THE FACTORY
        for component in self.factory.components.values():
            if component.type == "source":
                self.__add_source(component)
            elif component.type == "pool":
                self.__add_pool(component)
            elif component.type == "sink":
                self.__add_sink(component)
            elif component.type == "slack":
                self.__add_slack(component)
            elif component.type == "converter":
                self.__add_converter(component)
            elif component.type == "deadtime":
                self.__add_deadtime(component)
            elif component.type == "storage":
                self.__add_storage(component)
            elif component.type == "thermalsystem":
                self.__add_thermalsystem(component)
            elif component.type == "triggerdemand":
                self.__add_triggerdemand(component)
            elif component.type == "schedule":
                self.__add_schedule(component)

            if self.enable_time_tracking:
                logging.info(
                    f"Adding {component.type} {component.name}: {round(time.time() - self.t_step, 2)}s"
                )
                self.t_step = time.time()

        # SET OBJECTIVE FUNCTION
        self.m.setObjective(
            (
                sum(self.C_objective[i] for i in range(len(self.C_objective)))
                - sum(self.R_objective[i] for i in range(len(self.R_objective)))
            ),
            GRB.MINIMIZE,
        )  # ...as sum of all created cost components
        if self.enable_time_tracking:
            logging.info(
                f"Creating objective function: {round(time.time() - self.t_step, 2)}s"
            )
            self.t_step = time.time()

        logging.info(f" -> Building optimization problem finished ")
        logging.debug(
            f"-> The resulting problem is of type {self.problem_class['type']} with grade {self.problem_class['grade']}!"
        )
        if self.enable_time_tracking:
            logging.info(
                f"Time Required for factory setup: {time.time() - self.t_start}s"
            )
            self.t_start = time.time()  # reset timer

        # CONFIGURE SOLVER

        # adjust gurobi configuration if the problem is non-convex / quadratic
        if self.problem_class["grade"] > 1:
            self.m.params.NonConvex = 2

        # set maximum runtime if specified
        if "max_solver_time" in solver_config:
            self.m.setParam(
                GRB.Param.TimeLimit,
                iv.validate(solver_config["max_solver_time"], "float"),
            )

        # set solver method if specified
        if "solver_method" in solver_config:
            self.m.setParam(
                gp.GRB.Param.Method, iv.validate(solver_config["solver_method"], "int")
            )

        # set barrier solve tolerance if specified
        if "barrier_tolerance" in solver_config:
            self.m.setParam(
                gp.GRB.Param.BarConvTol,
                iv.validate(solver_config["barrier_tolerance"], "0..1"),
            )

        # set solver logging
        if not log_solver:
            self.m.Params.LogToConsole = 0

        logging.info(f"CALLING THE SOLVER")

        # CALL SOLVER
        self.m.optimize()
        if self.enable_time_tracking:
            logging.info(f"Solver Time: {round(time.time() - self.t_step, 2)}s")
            self.t_step = time.time()

        if not self.m.Status == GRB.TIME_LIMIT:
            # mark Simulation as solved
            self.simulated = True
            logging.info(" -> Simulation solved")
            if self.enable_time_tracking:
                logging.info(
                    f"Time Required for factory solving: {time.time() - self.t_start}s"
                )
                self.t_start = time.time()  # reset timer

            # COLLECT THE RESULTS
            self.__collect_results(
                threshold=threshold, rounding_decimals=rounding_decimals
            )
            if self.enable_time_tracking:
                logging.info(
                    f"Time Required for collecting results: {time.time() - self.t_start}s"
                )
        else:
            logging.warning("Solver time exceeded. Calculation aborted")

    def __validate_component(self, component):
        """
        This function checks, if the energy/material - conservation at a Component has been fulfilled during Simulation
        :param component: [factory.components.Component-object]
        :return: [Boolean] True if Component result is valid
        """

        # check, if the Simulation has been simulated already
        if not self.simulated:
            logging.critical(
                f"ERROR: Cannot validate the results of the Simulation, because it has not been simualted yet!"
            )
            raise Exception

        # skip the routine if the Component is a sink, source or slack
        if (
            component.type == "sink"
            or component.type == "source"
            or component.type == "slack"
        ):
            return True  # Sinks, sources and slacks don't have to be balanced

        # calculate the sum of inputs at the Component
        [input_sum_energy, input_sum_material] = self.__calculate_component_input_sum(
            component
        )

        # calculate the sum of outputs at the Component
        [
            output_sum_energy,
            output_sum_material,
        ] = self.__calculate_component_output_sum(component)

        # check the energy validate/output equilibrium
        if not round(input_sum_energy, 3) == round(
            output_sum_energy, 3
        ):  # round to 3 digits to avoid false positives due to solver tolerances
            logging.warning(
                f"WARNING: Energy is not conserved at Component {component.name}! Input: {round(input_sum_energy)}    Output: {round(output_sum_energy)}"
            )
            return False

        # check the material validate/output equilibrium
        if not round(input_sum_material, 3) == round(
            output_sum_material, 3
        ):  # round to 3 digits to avoid false positives due to solver tolerances
            logging.warning(
                f"WARNING: Material is not conserved at Component {component.name}! Input: {round(input_sum_material)}    Output: {round(output_sum_material)}"
            )
            return False

        return True

    def __validate_factory_architecture(self):
        """
        This function calls the factory.check_validity-method for the given factory
        """
        self.factory.check_validity()

    def __validate_results(self):
        """
        This function takes a look at all the results of a Simulation and performs some basic checks to confirm,
        that every equilibrium is met, no slacks have been used etc...
        :return: Sets self.simulation_valid as true or false
        """

        if not self.simulated:
            logging.critical(
                f"ERROR: Cannot validate the results of the Simulation, "
                f"because it has not been simualted yet!"
            )
            raise Exception
        logging.info("CHECKING RESULT CONSISTENCY")
        self.simulation_valid = True

        slacks_used = False
        values_energy_in = []
        values_energy_out = []
        names_energy_in = []
        names_material_out = []

        values_material_in = []
        values_material_out = []
        names_material_in = []
        names_energy_out = []

        values_slacks = []
        names_slacks = []

        # Collect all global inputs and outputs + detect slack usage
        for component_i in self.factory.components:
            component = self.factory.components[component_i]

            if not self.__validate_component(component):
                self.simulation_valid = False

            if component.type == "source":
                if component.flowtype.is_energy():
                    values_energy_in = np.append(
                        values_energy_in,
                        sum(self.result[component.key]["utilization"]),
                    )
                    names_energy_in.append(component.key)

                if component.flowtype.is_material():
                    values_material_in = np.append(
                        values_material_in,
                        sum(self.result[component.key]["utilization"]),
                    )
                    names_material_in.append(component.key)

            if component.type == "sink":
                if component.flowtype.is_energy():
                    values_energy_out = np.append(
                        values_energy_out,
                        sum(self.result[component.key]["utilization"]),
                    )
                    names_energy_out.append(component.key)

                if component.flowtype.is_material():
                    values_material_out = np.append(
                        values_material_out,
                        sum(self.result[component.key]["utilization"]),
                    )
                    names_material_out.append(component.key)

            if component.type == "slack":
                slack_utilization = round(
                    sum(self.result[component.key]["utilization"]), 3
                )
                if slack_utilization > 0:
                    values_slacks = np.append(values_slacks, slack_utilization)
                    names_slacks.append(component.key)
                    slacks_used = True
                    self.simulation_valid = False

        sum_energy_in = round(sum(values_energy_in), 2)
        sum_energy_out = round(sum(values_energy_out), 2)
        sum_material_in = round(sum(values_material_in), 2)
        sum_material_out = round(sum(values_material_out), 2)

        if sum_energy_in < sum_energy_out:
            logging.warning(
                f"WARNING: There is Energy being created within the system! Input: {round(sum_energy_in)}   Output: {round(sum_energy_out)}"
            )
            self.simulation_valid = False

        if sum_energy_in > sum_energy_out:
            logging.warning(
                f"WARNING: There is Energy being lost within the system! Input: {round(sum_energy_in)}   Output: {round(sum_energy_out)}"
            )
            self.simulation_valid = False

        if sum_material_in < sum_material_out:
            logging.warning(
                f"WARNING: There is Material being created within the system! Input: {round(sum_energy_in)}   Output: {round(sum_energy_out)}"
            )
            self.simulation_valid = False

        if sum_material_in > sum_material_out:
            logging.warning(
                f"WARNING: There is Material being lost within the system! Input: {round(sum_energy_in)}   Output: {round(sum_energy_out)}"
            )
            self.simulation_valid = False

        if slacks_used:
            df_slacks = {"values": values_slacks, "names": names_slacks}
            logging.warning(
                f"WARNING: Slacks were needed to solve the optimization: {df_slacks}"
            )

        # Check, if the punishment term for ambient gains was chosen high enough
        if max(self.result["ambient_gains"]["utilization"]) > 10000000:
            logging.warning(
                f"Warning: There is a high utilization of ambient gains! "
                f"This could be due to a numerical issue with the punishment-"
                f"term within factory_model.create_essentials(). "
                f"You should check the results for numerical issues!"
            )
            self.simulation_valid = False

        if self.simulation_valid:
            logging.info(" -> Simulation is valid!")
        else:
            logging.warning(" -> Simulation is invalid!")

    def __calculate_component_input_sum(self, component):
        """
        This function calculates the sum of energy and material inputs that arrived at a Component
        :param component: factory_components.Component-object
        :return: input_sum_energy, input_sum_material: float
        """

        # prepare summing variables for energy and material
        input_sum_energy = 0
        input_sum_material = 0

        # iterate over all regular inputs
        for input_i in component.inputs:

            # add the total flowtype of the validate to the sum of energy balance if it is an energy-validate
            if input_i.flowtype.is_energy():
                input_sum_energy += sum(self.result[input_i.key])

            # add the total flowtype of the validate to the sum of material balance if it is a material-validate
            if input_i.flowtype.is_material():
                input_sum_material += sum(self.result[input_i.key])

        # if the components is a thermalsystem: add the thermal-gains validate as well!
        if component.type == "thermalsystem":
            input_sum_energy += sum(self.result[component.from_gains.key])

        return input_sum_energy, input_sum_material

    def __calculate_component_output_sum(self, component):
        """
        This function calculates the sum of energy and material outputs that leave at a Component
        :param component: factory_comonents.Component-object
        :return: output_sum_energy, output_sum_material: float
        """

        # prepare summing variables for the outputs of energy and material
        output_sum_energy = 0
        output_sum_material = 0

        # iterate over all outputs
        for output_i in component.outputs:

            # add the flowtype of the output to the sum of energy outputs if it is an energy output
            if output_i.flowtype.is_energy():
                output_sum_energy += sum(self.result[output_i.key])

            # add the flowtype of the output to the sum of material outputs if it is a material output
            if output_i.flowtype.is_material():
                output_sum_material += sum(self.result[output_i.key])

        # if the Component is a converter: add the energy and material losses as well
        if component.type == "converter":
            if not component.to_Elosses == []:
                output_sum_energy += sum(self.result[component.to_Elosses.key])
            if not component.to_Mlosses == []:
                output_sum_material += sum(self.result[component.to_Mlosses.key])

        # if the Component is a storage or a thermalsystem: ad the energy or material losses as well
        if component.type == "storage" or component.type == "thermalsystem":

            # check, if the flowtype is energy or material and add the losses to the correct bilance
            if component.flowtype.is_energy():
                output_sum_energy += sum(self.result[component.to_losses.key])
            if component.flowtype.is_material():
                output_sum_material += sum(self.result[component.to_losses.key])

        # return calculated outputs
        return output_sum_energy, output_sum_material

    def __apply_threshold_and_rounding(
        self, data, threshold=float, rounding_decimals=int
    ):
        """
        This factory takes some numerical data, a threshold and an integer. All values of the data smaller than the
        threshold are set to 0. All values are rounded to the number of specified decimals
        :param data: a single value or timeseries of numerical data
        :param threshold: float, all values in the data > threshold will be set to 0
        :param decimals: number of decimals to round to
        :return: rounded data with applied threshold
        """

        # if data is a single integer it can just be returned
        if isinstance(data, int):
            return data

        # round the data to the specified number of digits
        data = data.astype(float)
        data = data.round(rounding_decimals)

        # set all values < threshold to 0
        data[data < threshold] = 0

        # return results
        return data
