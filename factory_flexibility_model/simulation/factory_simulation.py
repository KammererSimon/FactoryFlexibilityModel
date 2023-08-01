# FACTORY SIMULATION
# This Script contains the simulation class of the factory factory. It is used to store Factory-Scenario-Combinations and to perform the simulation itself on them
# The following Methods are meant to be used by external Scripts to prepare a simulation:
# self.__init__
# self.set_factory
# self.set_name
# self.set_scenario

# The simulation itself is conducted by the Method:
# self.simulate
# -> This method calls all the other internal functions to build an optimization problem out of the components specified in the factory

# To get the results use:
# self.create_dash
# self.show_results

import pickle
import time
import warnings
from datetime import datetime
from pathlib import Path

import gurobipy as gp

# IMPORT 3RD PARTY PACKAGES
import numpy as np
import scenario as sc
import xlsxwriter
from gurobipy import GRB

import factory_flexibility_model.input_validations as iv

# IMPORT ENDOGENOUS COMPONENTS
from factory_flexibility_model.factory import factory_model as fm
from factory_flexibility_model.web import factory_dash as fd

# import xlsxwriter


class simulation:
    def __init__(self, *args, **kwargs):
        # set general data for the simulation
        self.date_simulated = (
            None  # date/time of the last simulation conducted on the object
        )
        self.factory = None  # Variable to store the factory for the simulation
        self.interval_length = None  # realtime length of one simulation interval...to be taken out of the scenario
        self.info = None  # Free attribute to store additional information
        self.m = None  # Placeholder for the Gurobi-Model to be created
        self.scenario = None  # Variable to store the scenario for the simulation
        self.simulated = False  # Tracks, if the simulation has been calculated or not
        self.simulation_result = (
            None  # Variable for storing the results of the simulation
        )
        self.simulation_valid = None  # Is being set by self.validate_results
        self.T = None  # To be set during simulation
        self.time_reference_factor = None  # To be set during simulation
        self.version = 20221201  # Version number used to automatically throw errors when incompatible scripts are being used together

        # Check, if factory or scenario have been handed over: iterate over all kwargs-parameters
        for parameter in args:

            # check if current parameter is a scenario
            if isinstance(parameter, sc.scenario):
                self.scenario = parameter

            # check if current parameter is a factory
            if isinstance(parameter, fm.factory):
                self.factory = parameter

        # handle kwargs: set logging options
        self.log = False
        if (
            "enable_simulation_log" in kwargs
        ):  # set to True, if the simulation routine shall write a log in the console
            if kwargs["enable_simulation_log"] == "True":
                self.log = True

        self.log_solver = False
        if (
            "enable_solver_log" in kwargs
        ):  # set to True, if gurobi shall write a log in the console
            if kwargs["enable_solver_log"] == "True":
                self.log_solver = True

        self.enable_time_tracking = False
        if "enable_time_tracking" in kwargs:
            if kwargs["enable_time_tracking"] == "True":
                self.enable_time_tracking = True

        # initialize tracking of resulting problem class
        self.problem_class = {
            "grade": 1,
            "type": "float",
        }  # variable to keep track of the resulting problem class - used for logging purposes

        # create timestamp of simulation setup
        now = datetime.now()
        self.date_created = now.strftime(
            "%d/%m/%Y %H:%M:%S"
        )  # date/time of the creation of the simulation object

        if "name" in kwargs:
            self.name = kwargs["name"]  # unique name for the conducted simulation

    def __add_converter(self, component):
        # create a timeseries of decision variables to represent the utilization U(t)
        self.MVars[f"P_{component.name}"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"P_{component.name}"
        )
        if self.log:
            print(
                f"        - Variable:     P_{component.name}                              "
                f"(timeseries of the nominal power of {component.name}"
            )

        # add variables to express the positive and negative deviations from the nominal operating point
        self.MVars[f"P_{component.name}_devpos"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"P_{component.name}_devpos"
        )
        self.MVars[f"P_{component.name}_devneg"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"P_{component.name}_devneg"
        )

        # is the operating power of the converter limited? If yes: add power_max and power_min constraints
        if component.power_max_limited:
            self.m.addConstr(
                self.MVars[f"P_{component.name}"]
                <= component.power_max * component.availability
            )
            if self.log:
                print(
                    f"        - Constraint:   P_{component.name} <= P_{component.name}_max"
                )

        if component.power_min_limited:
            self.m.addConstr(
                self.MVars[f"P_{component.name}"]
                >= component.power_min * component.availability
            )
            if self.log:
                print(
                    f"        - Constraint:   P_{component.name} >= P_{component.name}_min"
                )

        # Calculate the efficiency of operation for each timestep based on the deviations
        self.MVars[f"Eta_{component.name}"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"Eta_{component.name}"
        )
        if self.log:
            print(
                f"        - Variable:     Eta_{component.name}                              "
                f"(Operating efficiency of {component.name}"
            )

        if component.eta_variable:
            if self.problem_class["grade"] < 2:
                self.problem_class["grade"] = 2
            self.m.addConstrs(
                self.MVars[f"Eta_{component.name}"][t]
                == component.eta_max
                - self.MVars[f"P_{component.name}_devpos"][t] * component.delta_eta_high
                - self.MVars[f"P_{component.name}_devneg"][t] * component.delta_eta_low
                for t in range(self.T)
            )
            if self.log:
                print(f"        - Constraint:   Calculate Eta(t) for {component.name}")
        else:
            self.m.addConstrs(
                self.MVars[f"Eta_{component.name}"][t] == 1 for t in range(self.T)
            )
            if self.log:
                print(
                    f"        - Constraint:   Eta(t) for {component.name} fixed to 100%"
                )

        # calculate the absolute operating point out of the nominal operating point, the deviations and the switching state
        # Can the Converter be turned on/off regardless of the power constraints?
        if component.switchable:
            if self.log:
                self.problem_class["type"] = "mixed integer"
            # introduce a variable representing the switching state of the converter
            self.MVars[f"Bool_{component.name}_state"] = self.m.addMVar(
                self.T, vtype=GRB.BINARY, name=f"{component.name}_state"
            )

            # calculate the operating point concerning the switching state
            self.m.addConstrs(
                self.MVars[f"P_{component.name}"][t]
                == (
                    component.power_nominal
                    - self.MVars[f"P_{component.name}_devneg"][t]
                    + self.MVars[f"P_{component.name}_devpos"][t]
                )
                * self.MVars[f"Bool_{component.name}_state"][t]
                for t in range(self.T)
            )
        else:
            # calculate the operating point without a switching state
            self.m.addConstr(
                self.MVars[f"P_{component.name}"]
                == component.power_nominal
                - self.MVars[f"P_{component.name}_devneg"]
                + self.MVars[f"P_{component.name}_devpos"]
            )

        # set ramping constraints if needed:
        if component.ramp_power_limited:
            self.m.addConstr(
                self.MVars[f"P_{component.name}"][1 : self.T]
                <= self.MVars[f"P_{component.name}"][0 : self.T - 1]
                + component.max_pos_ramp_power
            )  # restrict ramping up
            self.m.addConstr(
                self.MVars[f"P_{component.name}"][1 : self.T]
                >= self.MVars[f"P_{component.name}"][0 : self.T - 1]
                - component.max_neg_ramp_power
            )  # restrict ramping down
            if self.log:
                print(
                    f"        - Constraint:   Ramping constraints for {component.name}"
                )

        # set the flows of incoming connections
        for connection in component.inputs:
            self.m.addConstr(
                self.MVars[connection.name]
                == self.MVars[f"P_{component.name}"]
                * connection.weight_sink
                * self.interval_length
            )

        # set the flows of outgoing connections
        for connection in component.outputs:
            if connection.flow.is_energy():
                self.m.addConstr(
                    self.MVars[connection.name]
                    == self.MVars[f"P_{component.name}"]
                    * connection.weight_source
                    * self.interval_length
                    * self.MVars[f"Eta_{component.name}"]
                )
                if self.log:
                    print(
                        f"        - added energy output calculation with losses for {connection.name}"
                    )
            else:
                self.m.addConstr(
                    self.MVars[connection.name]
                    == self.MVars[f"P_{component.name}"]
                    * connection.weight_source
                    * self.interval_length
                )
                if self.log:
                    print(
                        f"        - added material output calculation for {connection.name}"
                    )

        # calculate the resulting energy losses: losses(t) = sum(inputs(t)) - sum(outputs(t))
        self.m.addConstr(
            self.MVars[component.to_Elosses.name]
            == sum(self.MVars[input_i.name] for input_i in component.inputs_energy)
            - sum(self.MVars[output_i.name] for output_i in component.outputs_energy)
        )

        # calculate the resulting material losses: losses(t) = sum(inputs(t)) - sum(outputs(t))
        if not component.to_Mlosses == []:
            self.m.addConstr(
                self.MVars[component.to_Mlosses.name]
                == sum(
                    self.MVars[input_i.name] for input_i in component.inputs_material
                )
                - sum(
                    self.MVars[output_i.name] for output_i in component.outputs_material
                )
            )

    def __add_deadtime(self, component):

        # calculate the number of timesteps required to match the scenario - timescale:
        delay = component.delay / self.time_reference_factor
        if not delay % 1 == 0:
            warnings.warn(
                f"Warning: The delay of {component.name} has been rounded to {delay}, since to clean conversion to the scenario timestep length is possible"
            )
        delay = int(delay)

        # check, if the deadtime is slacked:
        if len(component.outputs) == 1:
            # no slacks...
            # set output_flow = slack for start interval
            self.m.addConstr(self.MVars[component.outputs[0].name][0:delay] == 0)

            # set output(t) = input(t-delay) for middle interval
            self.m.addConstr(
                self.MVars[component.outputs[0].name][delay : self.T]
                == self.MVars[component.inputs[0].name][0 : self.T - delay]
            )

            # set input(t) = slack for end interval
            self.m.addConstr(
                self.MVars[component.inputs[0].name][self.T - delay : self.T - 1] == 0
            )

        else:
            # set output_flow = slack for start interval
            self.m.addConstrs(
                self.MVars[component.outputs[1].name][t]
                == self.MVars[component.inputs[0].name][t]
                for t in range(delay)
            )

            # set output(t) = input(t-delay) for middle interval
            self.m.addConstrs(
                self.MVars[component.outputs[1].name][t + delay]
                == self.MVars[component.inputs[1].name][t]
                for t in range(self.T - delay)
            )

            # set input(t) = slack for end interval
            self.m.addConstrs(
                self.MVars[component.inputs[1].name][self.T - t - 1]
                == self.MVars[component.outputs[0].name][t]
                for t in range(delay)
            )

    def __add_schedule(self, component):
        # get number of individual flexible demands:
        rows = len(component.demands)

        # create availability matrix for the demands
        availability = np.zeros((self.T, rows))
        for row in range(rows):
            for column in range(
                component.demands[row, 0], component.demands[row, 1] + 1
            ):
                availability[column - 1, row] = 1
        self.MVars[f"X_{component.name}_availability"] = availability

        # create decision variables for the demands
        self.MVars[f"E_{component.name}_in"] = self.m.addMVar(
            (self.T, rows), vtype=GRB.CONTINUOUS, name=f"{component.name}_Pin"
        )
        if self.log:
            print(
                f"        - Variable(s):  Ein for {rows} part demands of {component.name}"
            )

        # define constraint: input and output must be equal at any timestep to ensure, that the component just does flow control
        self.m.addConstr(
            self.MVars[component.outputs[0].name]
            == self.MVars[component.inputs[0].name]
        )
        if self.log:
            print(f"        - Constraint:   E_in == E_out for {component.name}")
            # TODO: doesnt this have to be fulfilled for every timestep??!

        # define constraint: taken inputs for demand fulfillment must equal the used input in every timestep
        self.m.addConstrs(
            gp.quicksum(self.MVars[f"E_{component.name}_in"][t][:])
            == self.MVars[component.inputs[0].name][t]
            for t in range(self.T)
        )
        if self.log:
            print(
                f"        - Constraint:   E_demands must be fed by inputs within {component.name}"
            )

        # define constraint: each part demand d must have it's individual demand fulfilled
        self.m.addConstrs(
            self.MVars[f"E_{component.name}_in"][0 : self.T, i]
            @ availability[0 : self.T, i]
            == component.demands[i, 2]
            for i in range(rows)
        )
        if self.log:
            print(
                f"        - Constraint:   Each part demand of {component.name} must have its demand fulfilled"
            )

        # define constraint: adhere power_max constraints per part demand
        self.m.addConstrs(
            self.MVars[f"E_{component.name}_in"][t, i] / self.interval_length
            <= component.demands[i, 3]
            for t in range(self.T)
            for i in range(rows)
        )
        if self.log:
            print(
                f"        - Constraint:   Adhere the power_max constraints for every part demand of {component.name}"
            )

        # define constraint: adhere power_max for total power if needed
        if component.power_max_limited:
            self.m.addConstrs(
                gp.quicksum(self.MVars[f"E_{component.name}_in"][t][:])
                / self.interval_length
                <= component.power_max[t]
                for t in range(self.T)
            )
            if self.log:
                print(
                    f"        - Constraint:   power_total(t) <= power_max for {component.name}"
                )

    def __add_pool(self, component):
        # create constraint that ensures, that the sum of inputs equals the sum of outputs in every timestep
        self.m.addConstr(
            gp.quicksum(
                self.MVars[component.inputs[input_id].name]
                for input_id in range(len(component.inputs))
            )
            == gp.quicksum(
                self.MVars[component.outputs[output_id].name]
                for output_id in range(len(component.outputs))
            )
        )
        if self.log:
            print(
                f"        - Constraint:   Energy equilibrium for Pool {component.name}"
            )

    def __add_sink(self, component):
        """
        This function adds all necessary MVARS and constraints to the optimization problem that are
        required to factory the sink handed over as 'component'
        :param component: factory_model.sink-object
        :return: self.m is beeing extended
        """
        # Sinks may be determined in their power intake or the power consumption may be calculated during the optimization.
        # In the first case a constraint is created, that forces all connected inputs to meet the desired power in total
        # In the second case a MVar reflecting the resulting inflow is created, together with a constraint to calculate it

        # create a timeseries of decision variables to represent the total inflow (energy/material) going into the sink
        self.MVars[f"E_{component.name}"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"E_{component.name}"
        )
        if self.log:
            print(
                f"        - Variable:     E_{component.name}                                  (timeseries of global outflows to {component.name}"
            )

        if component.determined:
            # set the sum of incoming flows to meet the power demand
            self.m.addConstr(
                gp.quicksum(
                    component.inputs[o].weight_sink
                    * self.MVars[component.inputs[o].name]
                    for o in range(len(component.inputs))
                )
                == component.demand
            )
            if self.log:
                print(
                    f"        - Constraint:   Sum of incoming flows == determined total demand              (E_{component.name} determined by timeseries)"
                )

        # add constraints to calculate the total outflow from the system as the sum of all weighted energys of incoming connections
        self.m.addConstr(
            gp.quicksum(
                self.MVars[component.inputs[o].name]
                for o in range(len(component.inputs))
            )
            == self.MVars[f"E_{component.name}"]
        )
        if self.log:
            print(
                f"        - Constraint:   E_{component.name} == sum of incoming flows"
            )

        # is the maximum output power of the sink limited? If yes: Add power_max constraint
        if component.power_max_limited:
            self.m.addConstr(
                self.MVars[f"E_{component.name}"]
                <= component.power_max * component.availability * self.interval_length
            )
            if self.log:
                print(
                    f"        - Constraint:   P_{component.name} <= P_{component.name}_max"
                )

        # is the minimum output power of the source limited? If yes: Add power_min constraint
        if component.power_min_limited:
            self.m.addConstrs(
                self.MVars[f"E_{component.name}"] / self.interval_length
                >= component.power_min[t]
                for t in range(self.T)
            )
            print(
                f"        - Constraint:   P_{component.name} >= P_{component.name}_min"
            )

        # does the utilization of the sink cost something? If yes: Add the corresponding cost factors
        if component.chargeable:
            self.C_objective.append(
                self.m.addMVar(1, vtype=GRB.CONTINUOUS, name=f"C_{component.name}")
            )
            self.m.addConstr(
                self.C_objective[-1]
                == component.cost[0 : self.T] @ self.MVars[f"E_{component.name}"]
            )
            if self.factory.log:
                print(f"        - CostFactor:   Cost for dumping into {component.name}")

        # does the utilization of the sink create revenue? If yes: Add the corresponding negative cost factors
        if component.refundable:
            self.R_objective.append(
                self.m.addMVar(1, vtype=GRB.CONTINUOUS, name=f"R_{component.name}")
            )
            self.m.addConstr(
                self.R_objective[-1]
                == component.revenue[0 : self.T] @ self.MVars[f"E_{component.name}"]
            )
            if self.factory.log:
                print(
                    f"        - CostFactor:   Revenue for sales generated by {component.name}"
                )

        if component.avoids_emissions:
            # avoided emissions
            self.R_objective.append(
                self.m.addMVar(
                    1, vtype=GRB.CONTINUOUS, name=f"R_{component.name}_emissions"
                )
            )
            self.m.addConstr(
                self.R_objective[-1]
                == component.co2_refund_per_unit[0 : self.T]
                @ self.MVars[f"E_{component.name}"]
                * self.scenario.cost_co2_per_kg
            )
            if self.log:
                print(
                    f"        - CostFactor:   Revenue from reduced CO2-emissions due to usage of {component.name}"
                )
        if component.causes_emissions:
            # additional emissions
            self.C_objective.append(
                self.m.addMVar(
                    1, vtype=GRB.CONTINUOUS, name=f"C_{component.name}_emissions"
                )
            )
            self.m.addConstr(
                self.C_objective[-1]
                == component.co2_emission_per_unit[0 : self.T]
                @ self.MVars[f"E_{component.name}"]
                * self.scenario.cost_co2_per_kg
            )
            if self.log:
                print(
                    f"        - CostFactor:   Costs for CO2-emissions due to usage of {component.name}"
                )

    def __add_slack(self, component):
        # slacks don't need any power restrictions or other constraints.
        # All they basically have to do is to be usable in any situation but be very expensive then.
        # So just two cost terms are being created here

        # add a cost term for negative slack usage to the target function
        for i in range(len(component.inputs)):
            self.C_objective.append(
                self.m.addMVar(1, vtype=GRB.CONTINUOUS, name=f"C_{component.name}_neg")
            )
            self.m.addConstr(
                self.C_objective[-1]
                == component.cost[0 : self.T]
                @ self.MVars[component.inputs[i].name][0 : self.T]
            )
            if self.log:
                print(f"        - CostFactor:   C_{component.name}_negative")

        # add a cost term for negative slack usage to the target function
        for i in range(len(component.outputs)):
            self.C_objective.append(
                self.m.addMVar(1, vtype=GRB.CONTINUOUS, name=f"C_{component.name}_pos")
            )
            self.m.addConstr(
                self.C_objective[-1]
                == component.cost[0 : self.T]
                @ self.MVars[component.outputs[i].name][0 : self.T]
            )
            if self.log:
                print(f"        - CostFactor:   C_{component.name}_positive")

    def __add_storage(self, component):
        # create  variable for initial SOC
        self.MVars[f"SOC_{component.name}_start"] = self.m.addMVar(
            1, vtype=GRB.CONTINUOUS, name=f"SOC_{component.name}_start"
        )
        if component.soc_start_determined:
            self.m.addConstr(
                self.MVars[f"SOC_{component.name}_start"] == component.soc_start
            )
            if self.log:
                print(
                    f"        - Constraint:   SOC_start == {component.soc_start} for storage {component.name}"
                )
        else:
            self.m.addConstr(self.MVars[f"SOC_{component.name}_start"] <= 1)
            if self.log:
                print(f"        - Variable:     SOC_start for storage {component.name}")

        # create variable for Echarge
        self.MVars[f"E_{component.name}_charge"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"E_{component.name}_charge"
        )
        self.m.addConstr(
            self.MVars[f"E_{component.name}_charge"]
            == gp.quicksum(
                self.MVars[component.inputs[input_id].name]
                for input_id in range(len(component.inputs))
            )
        )
        if self.log:
            print(f"        - Variable:     ECharge for storage {component.name} ")

        # create variable for Edischarge
        self.MVars[f"E_{component.name}_discharge"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"E_{component.name}_discharge"
        )
        self.m.addConstr(
            self.MVars[f"E_{component.name}_discharge"]
            == gp.quicksum(
                self.MVars[component.outputs[output_id].name]
                + self.MVars[component.to_losses.name]
                for output_id in range(len(component.outputs))
            )
        )
        if self.log:
            print(f"        - Variable:     EDischarge for storage {component.name} ")

        # create variable for SOC
        self.MVars[f"SOC_{component.name}"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"SOC_{component.name}"
        )
        if self.log:
            print(f"        - Variable:     SOC for storage {component.name} ")

        # calculate SOC for every timestep using cumsum + SOC_start
        cumsum_matrix = np.tril(
            np.ones(self.T)
        )  # create a matrix with ones on- and under the main diagonal to quickly perform cumsum-calculations in matrix form
        self.m.addConstr(
            self.MVars[f"SOC_{component.name}"]
            == cumsum_matrix
            @ (
                self.MVars[f"E_{component.name}_charge"]
                - self.MVars[f"E_{component.name}_discharge"]
            )
            + component.capacity * self.MVars[f"SOC_{component.name}_start"][0]
        )

        if self.log:
            print(
                f"        - Constraint:   Calculate SOC_end(t) for storage {component.name} "
            )

        # set SOC_end = SOC_start
        self.m.addConstr(
            self.MVars[f"SOC_{component.name}"][self.T - 1]
            == self.MVars[f"SOC_{component.name}_start"][0] * component.capacity
        )
        if self.log:
            print(
                f"        - Constraint:   SOC_end == SOC_start for storage {component.name}"
            )

        # don't violate the capacity boundary: cumsum of all inputs and outputs plus initial soc must not be more than the capacity in any timestep
        self.m.addConstr(self.MVars[f"SOC_{component.name}"] <= component.capacity)
        if self.log:
            print(
                f"        - Constraint:   Cumsum(E) <= Capacity for {component.name} "
            )

        # don't take out more than stored: cumsum of all inputs and outputs plus initial soc must be more than zero in any timestep
        self.m.addConstr(self.MVars[f"SOC_{component.name}"] >= 0)
        if self.log:
            print(f"        - Constraint:   Cumsum(E) >= 0 for {component.name} ")

        # create Pcharge_max-constraint
        if component.power_max_charge > 0:
            self.m.addConstr(
                self.MVars[f"E_{component.name}_charge"]
                <= component.power_max_charge * self.interval_length
            )
            if self.log:
                print(
                    f"        - Constraint:   power_charge <= power_charge_max for {component.name}"
                )

        # create Pdischarge_max-constraint
        if component.power_max_discharge > 0:
            self.m.addConstr(
                self.MVars[f"E_{component.name}_discharge"]
                <= component.power_max_discharge * self.interval_length
            )
            if self.log:
                print(
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
                    self.MVars[component.to_losses.name][t]
                    == self.MVars[f"SOC_{component.name}"][t] * soc_leakage
                    + lin_leakage
                    + gp.quicksum(  # TODO: BUG! This creates problems once the storage is empty! #TODO: The introduction of the timefactor in the soc-term causes a difference between 1*1h and 4*0.25h simulations
                        self.MVars[component.outputs[output_id].name][t]
                        for output_id in range(len(component.outputs))
                    )
                    * (1 / component.efficiency - 1)
                )
                for t in range(self.T)
            )
            if self.log:
                print(
                    f"        - Constraint:   E_losses = E_discharge * (1-efficiency) for {component.name}"
                )

    def __add_source(self, component):
        """
        This function adds all necessary MVARS and constraints to the optimization problem that are
        required to factory the source handed over as 'component'
        :param component: factory_model.source-object
        :return: self.m is being extended
        """

        # create a timeseries of decision variables to represent the total inflow coming from the source
        self.MVars[f"E_{component.name}"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"P_{component.name}"
        )

        # write log
        if self.log:
            print(
                f"        - Variable:     E_{component.name}                              (timeseries of global inputs from E_{component.name}"
            )

        # set the sum of outgoing flows to meet the fixed supply
        if component.determined:
            self.m.addConstr(
                gp.quicksum(
                    component.outputs[o].weight_source
                    * self.MVars[component.outputs[o].name]
                    for o in range(len(component.outputs))
                )
                == component.determined_power
            )

        # add constraints to calculate the total inflow to the system as the sum of all flows of connected regions
        self.m.addConstr(
            gp.quicksum(
                self.MVars[component.outputs[o].name]
                for o in range(len(component.outputs))
            )
            == self.MVars[f"E_{component.name}"]
        )
        # write log
        if self.log:
            print(
                f"        - Constraint:   E_{component.name} == sum of outgoing flows"
            )

        # is the maximum output power of the source limited? If yes: Add power_max constraint
        if component.power_max_limited:
            self.m.addConstr(
                gp.quicksum(
                    component.outputs[o].weight_source
                    * self.MVars[component.outputs[o].name]
                    for o in range(len(component.outputs))
                )
                / self.interval_length
                <= component.power_max * component.availability
            )
            if self.log:
                print(
                    f"        - Constraint:   P_{component.name} <= P_{component.name}_max"
                )
        else:
            # TODO: Abhängig machen von slacks
            self.m.addConstr(
                gp.quicksum(
                    component.outputs[o].weight_source
                    * self.MVars[component.outputs[o].name]
                    for o in range(len(component.outputs))
                )
                * 1000
                <= 1000000
            )
            if self.log:
                print(
                    f"        - Constraint:   P_{component.name} <= P_SECURITY                            -> Prevent Model from being unbounded"
                )

        # is the minimum output power of the source limited? If yes: Add power_min constraint
        if component.power_min_limited:
            self.m.addConstr(
                gp.quicksum(
                    component.outputs[o].weight_source
                    * self.MVars[component.outputs[o].name]
                    for o in range(len(component.outputs))
                )
                / self.interval_length
                >= component.power_min
            )
            # write log
            if self.log:
                print(
                    f"        - Constraint:   P_{component.name} >= P_{component.name}_min"
                )

        # does the utilization of the source cost something? If yes: Add the corresponding cost factors
        if component.chargeable:
            self.C_objective.append(
                self.m.addMVar(1, vtype=GRB.CONTINUOUS, name=f"C_{component.name}")
            )
            self.m.addConstr(
                self.C_objective[-1]
                == component.cost[0 : self.T] @ self.MVars[f"E_{component.name}"]
            )
            if self.log:
                print(f"        - CostFactor:   Cost for usage of {component.name}")

                # for i in range(len(component.outputs)):
                #    self.C_objective.append(self.m.addMVar(1, vtype=GRB.CONTINUOUS, name=f"C_{component.name}_{i}"))
                #    self.m.addConstr(self.C_objective[-1] == component.cost[0:self.T] @ self.MVars[component.outputs[i].name])
                # if self.log:
                #   print(
                #      f"        - CostFactor:   Cost to use {component.outputs[i].flow.name} from {component.name} for {component.outputs[i].sink.name}")
                # TODO: delete the lines above if no error occures in the next weeks (01/23)

        # is the source afflicted with a capacity charge?
        # If yes: Add an MVar for the maximum used Power and add cost factor
        if component.capacity_charge > 0:

            # create single float Mvar
            self.MVars[f"P_max_{component.name}"] = self.m.addMVar(
                1, vtype=GRB.CONTINUOUS, name=f"P_max_{component.name}"
            )

            # define the Mvar as the maximum used output power
            self.m.addConstr(
                self.MVars[f"P_max_{component.name}"][0]
                == gp.max_(
                    (self.MVars[f"E_{component.name}"][t] for t in range(self.T)),
                    constant=0,
                )
            )

            # create new cost term
            self.C_objective.append(
                self.m.addMVar(
                    1, vtype=GRB.CONTINUOUS, name=f"C_Capacity_{component.name}"
                )
            )

            # define the costs -> capacity_charge is specified on yearly basis, so only
            self.m.addConstr(
                self.C_objective[-1]
                == self.interval_length
                * self.T
                / 8760
                * component.capacity_charge
                * self.MVars[f"P_max_{component.name}"]
            )

            # write log
            if self.log:
                print(
                    f"        - CostFactor:   Cost for capacity charge of {component.name}"
                )

        # does the source cause direct or indirect emissions when used?
        if component.causes_emissions:
            # create new cost term for the emissions
            self.C_objective.append(
                self.m.addMVar(
                    1, vtype=GRB.CONTINUOUS, name=f"C_{component.name}_emissions"
                )
            )

            # calculate the costs
            self.m.addConstr(
                self.C_objective[-1]
                == component.co2_emissions_per_unit[0 : self.T]
                @ self.MVars[f"E_{component.name}"]
                * self.scenario.cost_co2_per_kg
            )
            # write log
            if self.log:
                print(
                    f"        - CostFactor:   Cost for CO2-emissions due to usage of {component.name}"
                )

    def __add_thermalsystem(self, component):
        # create a timeseries of decision variables to represent the total inflow going into the thermal demand:
        self.MVars[f"E_{component.name}_in"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"E_{component.name}_in"
        )
        self.m.addConstrs(
            (
                self.MVars[f"E_{component.name}_in"][t]
                == gp.quicksum(
                    self.MVars[component.inputs[input_id].name][t]
                    for input_id in range(len(component.inputs))
                )
            )
            for t in range(self.T)
        )
        if self.log:
            print(
                f"        - Variable:     E_{component.name}_in                                 (timeseries of incoming thermal energy at {component.name})"
            )

        # create a timeseries of decision variables to represent the total outflow going out of the thermal demand:
        self.MVars[f"E_{component.name}_out"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"E_{component.name}_out"
        )
        self.m.addConstrs(
            (
                self.MVars[f"E_{component.name}_out"][t]
                == gp.quicksum(
                    self.MVars[component.outputs[output_id].name][t]
                    for output_id in range(len(component.outputs))
                )
            )
            for t in range(self.T)
        )
        if self.log:
            print(
                f"        - Variable:     E_{component.name}_out                                  (timeseries of removed thermal energy at {component.name})"
            )

        # create a timeseries for the internal temperature:
        self.MVars[f"T_{component.name}"] = self.m.addMVar(
            self.T, vtype=GRB.CONTINUOUS, name=f"T_{component.name}"
        )
        if self.log:
            print(
                f"        - Variable:     T_{component.name}                                  (Internal Temperature of {component.name})"
            )

        # set the starting temperature:
        self.m.addConstr(
            self.MVars[f"T_{component.name}"][0] == component.temperature_start
        )
        if self.log:
            print(f"        - Constraint:   T_{component.name}[0] = Tstart")

        # add constraint for the thermal R-C-factory
        self.m.addConstrs(
            (
                self.MVars[f"T_{component.name}"][t]
                == self.MVars[f"T_{component.name}"][t - 1]
                + (  # t-1 temperature
                    component.temperature_ambient[t - 1]
                    - self.MVars[f"T_{component.name}"][t - 1]
                )
                * self.time_reference_factor
                / (component.R * component.C)
                + (  # thermal inertia
                    self.MVars[f"E_{component.name}_in"][t - 1]
                    - self.MVars[f"E_{component.name}_out"][t - 1]
                )
                * self.time_reference_factor
                / component.C
            )
            for t in range(1, self.T)
        )  # heating/cooling impact

        # keep the temperature within the allowed boundaries during simulation interval:
        self.m.addConstrs(
            (self.MVars[f"T_{component.name}"][t] >= component.temperature_min[t])
            for t in range(self.T)
        )
        self.m.addConstrs(
            (self.MVars[f"T_{component.name}"][t] <= component.temperature_max[t])
            for t in range(self.T)
        )
        if self.log:
            print(
                f"        - Constraint:   Tmin < T_{component.name} < Tmax for {component.name}"
            )

        # set the end temperature:
        if component.sustainable:
            self.m.addConstr(
                self.MVars[f"T_{component.name}"][self.T - 1]
                + (
                    component.temperature_ambient[self.T - 1]
                    - self.MVars[f"T_{component.name}"][self.T - 1]
                )
                * self.time_reference_factor
                / (component.R * component.C)
                + (
                    self.MVars[f"E_{component.name}_in"][self.T - 1]
                    - self.MVars[f"E_{component.name}_out"][self.T - 1]
                )
                * self.time_reference_factor
                / component.C
                == component.temperature_start
            )
            if self.log:
                print(f"        - Constraint:   T_{component.name}[T] = Tstart")
        else:
            # keep the temperature within allowed boundaries at timestep T+1
            self.m.addConstr(
                self.MVars[f"T_{component.name}"][self.T - 1]
                + (
                    component.temperature_ambient[self.T - 1]
                    - self.MVars[f"T_{component.name}"][self.T - 1]
                )
                * self.time_reference_factor
                / (component.R * component.C)
                + (
                    self.MVars[f"E_{component.name}_in"][self.T - 1]
                    - self.MVars[f"E_{component.name}_out"][self.T - 1]
                )
                * self.time_reference_factor
                / component.C
                >= component.temperature_min[self.T - 1]
            )

            self.m.addConstr(
                self.MVars[f"T_{component.name}"][self.T - 1]
                + (
                    component.temperature_ambient[self.T - 1]
                    - self.MVars[f"T_{component.name}"][self.T - 1]
                )
                * self.time_reference_factor
                / (component.R * component.C)
                + (
                    self.MVars[f"E_{component.name}_in"][self.T - 1]
                    - self.MVars[f"E_{component.name}_out"][self.T - 1]
                )
                * self.time_reference_factor
                / component.C
                <= component.temperature_max[self.T - 1]
            )

        # calculate the losses:
        self.m.addConstrs(
            self.MVars[component.to_losses.name][t]
            - self.MVars[component.from_gains.name][t]
            == (self.MVars[f"T_{component.name}"][t] - component.temperature_ambient[t])
            * self.time_reference_factor
            / component.R
            for t in range(self.T)
        )

        if self.log:
            print(
                f"        - Constraint:     calculation of thermal losses for {component.name}"
            )

    def __add_triggerdemand(self, component):
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
        self.MVars[f"{component.name}_executions"] = self.m.addMVar(
            possibilities, vtype=GRB.INTEGER, name=f"{component.name}_executions"
        )
        if self.log:
            print(
                f"        - Variable:     {component.name}_executions                                 (List of triggered events at triggerdemand {component.name})"
            )

        # guarantee the required amount of executions
        if component.executions > 0:
            self.m.addConstr(
                sum(self.MVars[f"{component.name}_executions"]) == component.executions
            )
            if self.log:
                print(
                    f"        - Constraint:     Guarantee the required amount of process executions at {component.name}"
                )

        # limit the number of parallel executions
        if component.max_parallel > 0:
            self.m.addConstr(
                parallelcheck.transpose() @ self.MVars[f"{component.name}_executions"]
                <= np.ones(component.Tend - component.Tstart + 1)
                * component.max_parallel
            )
            if self.log:
                print(
                    f"        - Constraint:   Limit the maximum parallel executions at {component.name}"
                )

        # calculate resulting load profile
        if component.input_energy:
            self.MVars[f"{component.name}_loadprofile_energy"] = self.m.addMVar(
                self.T,
                vtype=GRB.CONTINUOUS,
                name=f"{component.name}_loadprofile_energy",
            )
        if component.input_material:
            self.MVars[f"{component.name}_loadprofile_material"] = self.m.addMVar(
                self.T,
                vtype=GRB.CONTINUOUS,
                name=f"{component.name}_loadprofile_material",
            )
        if self.log:
            print(
                f"        - Variable:     {component.name}_loadprofile                                 (resulting load profile of triggerdemand {component.name})"
            )

        if component.Tstart > 1:
            if component.input_energy:
                self.m.addConstr(
                    self.MVars[f"{component.name}_loadprofile_energy"][
                        : component.Tstart - 1
                    ]
                    == 0
                )
            if component.input_material:
                self.m.addConstr(
                    self.MVars[f"{component.name}_loadprofile_material"][
                        : component.Tstart - 1
                    ]
                    == 0
                )

        if component.input_energy:
            self.m.addConstr(
                self.MVars[f"{component.name}_loadprofile_energy"][
                    component.Tstart - 1 : component.Tend
                ]
                == profiles_energy.transpose()
                @ self.MVars[f"{component.name}_executions"]
            )
        if component.input_material:
            self.m.addConstr(
                self.MVars[f"{component.name}_loadprofile_material"][
                    component.Tstart - 1 : component.Tend
                ]
                == profiles_material.transpose()
                @ self.MVars[f"{component.name}_executions"]
            )

        if component.Tend < self.T:
            if component.input_energy:
                self.m.addConstr(
                    self.MVars[f"{component.name}_loadprofile_energy"][
                        component.Tend + 1 :
                    ]
                    == 0
                )
            if component.input_material:
                self.m.addConstr(
                    self.MVars[f"{component.name}_loadprofile_material"][
                        component.Tend + 1 :
                    ]
                    == 0
                )
        if self.log:
            print(f"        - Constraint:   Calculate load profile at {component.name}")

        # set input and output connection to match the load profile
        if component.input_energy:
            self.m.addConstr(
                self.MVars[component.input_energy.name]
                == self.MVars[f"{component.name}_loadprofile_energy"]
                * self.interval_length
            )
            self.m.addConstr(
                self.MVars[component.output_energy.name]
                == self.MVars[f"{component.name}_loadprofile_energy"]
                * self.interval_length
            )
        if component.input_material:
            self.m.addConstr(
                self.MVars[component.input_material.name]
                == self.MVars[f"{component.name}_loadprofile_material"]
            )
            self.m.addConstr(
                self.MVars[component.output_material.name]
                == self.MVars[f"{component.name}_loadprofile_material"]
            )

    def __add_flows(self):
        """This function adds a MVar for the flow on every existing connection to te optimization problem"""

        # iterate over all existing connections
        for connection in self.factory.connections.values():

            # create a timeseries of decision variables for the flow on every connection in the graph
            self.MVars[connection.name] = self.m.addMVar(
                self.T, vtype=GRB.CONTINUOUS, name=connection.name
            )

            # write log
            if self.log:
                print(
                    f"        - Variable:     E_Flow_{connection.name}                                (timeseries of flow on connection {connection.name})"
                )

    def __collect_results(self, **kwargs):
        """
        This function collects all the simulation results of the simulation object and writes them in a
        single dictionary under simulation.results
        """

        # write log
        if self.log:
            print("COLLECTING RESULTS")

        # check, if simulation has been conducted yet
        if not self.simulated:
            # if not: raise an Exception
            raise Exception(
                f"Cannot collect results for simulation {self.name} because it has not been calculated yet"
            )

        # initialize a dict to store all the results
        self.result = {}

        # handle kwargs: initialize threshold under which numeric results are interpreted as 0
        if "threshold" in kwargs:
            threshold = kwargs["threshold"]
        else:
            threshold = 0

        # handle kwargs: initialize the number of decimals that the results are rounded to
        if "round" in kwargs:
            decimals = iv.input(kwargs["round"], "int")
        else:
            decimals = 10

        # initialize counter- and summing variables:
        total_emissions = 0
        total_emission_cost = 0

        # collect timeseries of all flows in the factory: iterate over all connections
        for connection in self.factory.connections.values():

            # get the result timeseries for the current connection
            result_i = self.MVars[connection.name].X

            # apply threshold and round
            result_i = self.__apply_threshold_and_rounding(
                result_i, threshold, decimals
            )

            # write the result into the result-dictionary
            self.result[connection.name] = result_i

        # prepare summing variables for differentiation of onsite and offsite generation/consumption
        self.result["energy_generated_onsite"] = np.zeros(self.T)
        self.result["energy_generated_offsite"] = np.zeros(self.T)
        self.result["energy_consumed_onsite"] = np.zeros(self.T)
        self.result["energy_consumed_offsite"] = np.zeros(self.T)

        # collect all component specific timeseries: iterate over all components
        for component in self.factory.components.values():

            # handle pools
            if component.type == "pool":

                # get the sum of the throughput as timeseries
                utilization = sum(
                    component.inputs[input_id].weight_sink
                    * self.MVars[component.inputs[input_id].name].X
                    for input_id in range(len(component.inputs))
                )

                # apply threshold and rounding
                utilization = self.__apply_threshold_and_rounding(
                    utilization, threshold, decimals
                )

                # write the results into the result dictionary
                self.result[component.name] = {"utilization": utilization}

            # handle converters
            if component.type == "converter":

                # get the result values, round them to the specified number of digits
                utilization = self.MVars[f"P_{component.name}"].X
                efficiency = self.MVars[f"Eta_{component.name}"].X

                # apply threshold and rounding on all values
                utilization = self.__apply_threshold_and_rounding(
                    utilization, threshold, decimals
                )
                efficiency = self.__apply_threshold_and_rounding(
                    efficiency, threshold, decimals
                )

                # write results into the result-dictionary
                self.result[component.name] = {
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
                    # if no: use the simulation result
                    utilization = self.MVars[f"E_{component.name}"].X

                # apply rounding and threshold
                utilization = self.__apply_threshold_and_rounding(
                    utilization, threshold, decimals
                )

                # calculate the emissions avoided by the sink
                if component.avoids_emissions:
                    # if the sink can avoid emissions: calculate them
                    emissions = utilization * component.co2_refund_per_unit[0 : self.T]
                    emission_cost = sum(emissions) * self.scenario.cost_co2_per_kg

                    # add avoided costs and emissions to the summing variables
                    total_emissions -= emissions
                    total_emission_cost -= emission_cost

                    # write log
                    print(
                        f"Sink {component.name} avoided total emissions of {round(sum(emissions), 2)} kgCO2, refunding {round(emission_cost, 2)}€"
                    )

                elif component.causes_emissions:
                    emissions = (
                        utilization * component.co2_emission_per_unit[0 : self.T]
                    )
                    emission_cost = sum(emissions) * self.scenario.cost_co2_per_kg

                    # add avoided costs and emissions to the summing variables
                    total_emissions += emissions
                    total_emission_cost += emission_cost
                    # write log
                    print(
                        f"Sink {component.name} caused total emissions of {round(sum(emissions), 2)} kgCO2, costing {round(emission_cost, 2)}€"
                    )

                else:
                    # otherwise set zeros:
                    emissions = 0
                    emission_cost = 0

                # write the result into the result-dictionary
                self.result[component.name] = {
                    "utilization": utilization,
                    "emissions": emissions,
                    "emission_cost": emission_cost,
                }

                # add the sinks contribution to onsite/offsite demand calculation
                if component.is_onsite:
                    self.result["energy_consumed_onsite"] += self.result[
                        component.name
                    ]["utilization"]
                else:
                    self.result["energy_consumed_offsite"] += self.result[
                        component.name
                    ]["utilization"]

            # handle sources
            elif component.type == "source":

                # is the power of the source determined by a timeseries?
                if component.determined:
                    # if yes: use the given timeseries
                    utilization = component.determined_power[0 : self.T]
                else:
                    # if no: use simulation result
                    utilization = self.MVars[f"E_{component.name}"].X

                # apply rounding and threshold
                utilization = self.__apply_threshold_and_rounding(
                    utilization, threshold, decimals
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

                    # write log
                    print(
                        f"Source {component.name} caused total emissions of {round(sum(emissions),2)} kgCO2, costing additional {round(emission_cost,2)}€"
                    )
                else:
                    emissions = 0
                    emission_cost = 0

                # write the result into the result-dictionary
                self.result[component.name] = {
                    "utilization": utilization,
                    "emissions": emissions,
                    "emission_cost": emission_cost,
                }

                # add the sources contribution to onsite/offsite generation calculation
                if component.is_onsite:
                    self.result["energy_generated_onsite"] += self.result[
                        component.name
                    ]["utilization"]
                else:
                    self.result["energy_generated_offsite"] += self.result[
                        component.name
                    ]["utilization"]

            # handle slacks
            elif component.type == "slack":
                # read the result timeseries of the simulation
                sum_energy_pos = sum(
                    self.MVars[i_input.name].X[0 : self.T]
                    for i_input in component.inputs
                )
                sum_energy_neg = sum(
                    self.MVars[i_output.name].X[0 : self.T]
                    for i_output in component.outputs
                )
                utilization = sum(
                    self.MVars[i_input.name].X[0 : self.T]
                    for i_input in component.inputs
                ) - sum(
                    self.MVars[i_output.name].X[0 : self.T]
                    for i_output in component.outputs
                )

                # apply rounding and threshold
                sum_energy_pos = self.__apply_threshold_and_rounding(
                    sum_energy_pos, threshold, decimals
                )
                sum_energy_neg = self.__apply_threshold_and_rounding(
                    sum_energy_neg, threshold, decimals
                )
                utilization = self.__apply_threshold_and_rounding(
                    utilization, threshold, decimals
                )

                # write the results to the result dictionary
                self.result[component.name] = {
                    "EPos": sum_energy_pos,
                    "ENeg": sum_energy_neg,
                    "utilization": utilization,
                }

            # handle storages
            elif component.type == "storage":
                # read the result timeseries from the simulation
                power_charge = (
                    self.MVars[f"E_{component.name}_charge"].X / self.interval_length
                )
                power_discharge = (
                    self.MVars[f"E_{component.name}_discharge"].X / self.interval_length
                )
                soc = self.MVars[f"SOC_{component.name}"].X
                soc_start = self.MVars[f"SOC_{component.name}_start"].X

                # apply rounding and threshold
                power_charge = self.__apply_threshold_and_rounding(
                    power_charge, threshold, decimals
                )
                power_discharge = self.__apply_threshold_and_rounding(
                    power_discharge, threshold, decimals
                )
                soc = self.__apply_threshold_and_rounding(soc, threshold, decimals)
                soc_start = self.__apply_threshold_and_rounding(
                    soc_start, threshold, decimals
                )

                # write the results to the result dictionary
                self.result[component.name] = {
                    "Pcharge": power_charge,
                    "Pdischarge": power_discharge,
                    "SOC": soc,
                    "utilization": power_discharge - power_charge,
                    "SOC_start": soc_start,
                }

            # handle schedulers
            elif component.type == "schedule":
                # read the result timeseries from the simulation
                utilization = self.MVars[f"E_{component.name}_in"].X
                availability = self.MVars[f"X_{component.name}_availability"]

                # apply rounding and threshold
                utilization = self.__apply_threshold_and_rounding(
                    utilization, threshold, decimals
                )
                availability = self.__apply_threshold_and_rounding(
                    availability, threshold, decimals
                )

                # write the results to the result dictionary
                self.result[component.name] = {
                    "utilization": utilization,
                    "availability": availability,
                }

            # handle thermalsystems
            elif component.type == "thermalsystem":
                # read the result timeseries from the simulation
                utilization = (
                    self.MVars[f"E_{component.name}_in"].X
                    - self.MVars[f"E_{component.name}_out"].X
                )
                temperature = self.MVars[f"T_{component.name}"].X

                # apply rounding and threshold
                utilization = self.__apply_threshold_and_rounding(
                    utilization, threshold, decimals
                )
                temperature = self.__apply_threshold_and_rounding(
                    temperature, threshold, decimals
                )

                # write the results to the result dictionary
                self.result[component.name] = {
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

        # print(f"Total emissions: {round(sum(self.result['total_emissions']),2)}, Certificate Costs: {round(self.result['total_emission_cost'],2)}€")

        # collect achieved costs/revenues (objective of target function - ambient_gain_punishment_term)
        self.result["objective"] = self.m.objVal - sum(
            self.result["ambient_gains"]["utilization"]
            * self.factory.components["ambient_gains"].cost[0 : self.T]
        )

        # validate results
        self.__validate_results()

        # set results_collected to true
        self.results_collected = True

        # write log
        if self.log:
            print(" -> Results processed")

    def create_dash(self) -> object:
        """This function calls the factory_dash.create_dash()-routine to bring the dashboard online for the just conducted simulation"""
        # write log-entry if requested
        if self.log:
            print("CREATING DASHBOARD")
        fd.create_dash(self)

    def __read_scenario_data(self):
        """This function checks the factory for "scenario_data" arguments and configures concerning
        components with the requested parameters from self.scenario"""

        # find components, that need to be fed with data from the scenario
        for i_component in self.factory.components:
            component = self.factory.components[i_component]  # cache the actual object

            # continue with next component if the current one is not scenario dependent
            if not component.scenario_dependent:
                continue

            # initialize new kwargs-dict
            kwargs = {}

            # go through list of parameters to be set by the scenario
            for parameter in component.scenario_data:
                key = component.scenario_data[parameter]

                # check, if the scenario has the requested key
                if not hasattr(self.scenario, key):
                    raise Exception(
                        f'ERROR while setting scenario data for component {component.name}: Scenario "{self.scenario.name}" does not contain the requested attribute "{key}"'
                    )

                # add the identified parameter to the kwargs-dict
                kwargs[parameter] = getattr(self.scenario, key)

            # change component configuration
            self.factory.set_configuration(component.name, **kwargs)

    def save(self, file_path, **kwargs):
        """
        This function saves a simulation-object under the specified filepath as a single file.
        :param file_path: Path to the file to be created
        :param kwargs: Set "overwrite=True" to allow the method to overwrite existing files.
        Otherwise an error will occur when trying to overwrite a file
        :return: Nothing
        """

        # determine, if an existing file will be overwritten or not
        if "overwrite" in kwargs:
            overwrite_existing_file = kwargs["overwrite"]
        else:
            overwrite_existing_file = False

        # check, if file already exists
        file = Path(file_path)
        if file.is_file():
            if overwrite_existing_file:
                warnings.warn(
                    f"WARNING: The specified file already exists and will be overwritten"
                )
            else:
                raise Exception(
                    f"ERROR: The specified file already exists! Saving Factory aborted!"
                )

        # create a copy of the simulation without the gurobi_model
        simulation_data = self
        simulation_data.m = []
        simulation_data.MVars = []
        simulation_data.C_objective = []
        simulation_data.R_objective = []

        # save the factory at the given path
        with open(file_path, "wb") as f:
            pickle.dump(simulation_data, f)

        # write log
        if self.log:
            print(f"SIMULATION SAVED under{file_path}")

    def set_factory(self, factory):
        """This function sets a factory_model.factory-object as the factory for the simulation"""
        self.factory = factory

        if factory.version == self.version:
            print("Factory for simulation set")
        else:
            warnings.warn(
                "Different skript-versions of factory_model and factory_simulation are being used! "
                "This might lead to errors due to incompatibilities"
            )

    def set_name(self, name=str):
        """This function sets the given name as a name for the simulation"""
        self.name = iv.input(name, "string")

    def set_scenario(self, scenario):
        """This function sets a factory_scenario.scenario-object as the scenario for the simulation"""
        self.scenario = scenario
        print("scenario for simulation set")

    def simulate(self, **kwargs):
        """
        This function builds an optimization problem out of the factory and scenario and calls gurobi to solve it.
        :param kwargs: enable_solver_log | enable_time_tracking | enable_simulation_log | max_solver_time | solver_method
        :return: Adds an attribute .result to the simulation object
        """

        # handle kwargs: set logging options
        self.log = False
        if (
            "enable_simulation_log" in kwargs
        ):  # set to True, if the simulation routine shall write a log in the console
            if kwargs["enable_simulation_log"] == "True":
                self.log = True

        self.log_solver = False
        if (
            "enable_solver_log" in kwargs
        ):  # set to True, if gurobi shall write a log in the console
            self.log_solver = iv.input(kwargs["enable_solver_log"], "boolean")

        self.enable_time_tracking = False
        if "enable_time_tracking" in kwargs:
            self.enable_time_tracking = iv.input(
                kwargs["enable_time_tracking"], "boolean"
            )

        # ENABLE TIMETRACKING?
        if self.enable_time_tracking:
            self.t_start = time.time()

        # PREPARATIONS
        if self.log:
            self.problem_class = {"grade": 1, "type": "float"}

        # Write timestamp
        now = datetime.now()
        self.date_simulated = now.strftime("%d/%m/%Y %H:%M:%S")  # write timestamp

        # Validate factory architecture
        self.__validate_factory_architecture()

        # check, if the factory can handle enough timesteps
        if self.scenario.number_of_timesteps > self.factory.max_timesteps:
            raise Exception(
                f"ERROR: Length of scenario {self.scenario.name} ({self.scenario.number_of_timesteps}) is longer than the factory {self.factory.name} allows {self.factory.max_timesteps}!"
            )

        # Configure the timefactor as specified in the scenario:
        self.interval_length = (
            self.scenario.timefactor
        )  # The length of one simulation timesten in hours is taken from the scenario
        self.T = (
            self.scenario.number_of_timesteps
        )  # just beeing lazy...writing "number_of_timesteps" every single time is a pain in the ass

        # calculate time_reference_factor
        self.time_reference_factor = (
            self.scenario.timefactor / self.factory.timefactor
        )  # a conversion factor that implies, how many factory related timesteps are represented by one simulation timestep

        # writelog
        if self.log:
            print(
                f"   Timefactor of the simulation set to: 1 timestep == {self.scenario.timefactor} hours ({self.scenario.timefactor*60} minutes)"
            )

        # INITIALIZE GUROBI MODEL
        # write log
        if self.log:
            print("INITIALIZING GUROBI")

        # create new gurobi factory
        self.m = gp.Model("Factory")

        # write log
        if not self.log_solver:
            self.m.Params.LogToConsole = 0

        # initialize variables for collecting parts of the optimization problem
        self.MVars = {}  # Initialize a dict to store all the factory variables
        self.C_objective = (
            list()
        )  # List of cost terms that need to be summed up for the target function
        self.R_objective = (
            list()
        )  # List of revenue terms that need to be summed up for the target function

        # ADAPTING SCENARIO DATA
        if self.log:
            print("SETTING SCENARIO_DATA")
        self.__read_scenario_data()
        if self.log:
            print(" -> Scenario data collection successful")

        # BUILDING OPTIMIZATION PROBLEM
        if self.log:
            print("BUILDING OPTIMIZATION PROBLEM")

        if self.enable_time_tracking:
            print(f"Preperations: {round(time.time()-self.t_start,2)}s")
            self.t_step = time.time()

        # CREATE MVARS FOR ALL FLOWS IN THE FACTORY
        self.__add_flows()
        if self.enable_time_tracking:
            print(f"Creating Flows: {round(time.time() - self.t_step, 2)}s")
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
                print(
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
            print(
                f"Creating objective function: {round(time.time() - self.t_step, 2)}s"
            )
            self.t_step = time.time()

        if self.log:
            print(f" -> Building optimization problem finished ")
        if self.log_solver:
            print(
                f"-> The resulting problem is of type {self.problem_class['type']} with grade {self.problem_class['grade']}!"
            )
        if self.enable_time_tracking:
            print(f"Time Required for factory setup: {time.time() - self.t_start}s")
            self.t_start = time.time()  # reset timer

        # CONFIGURE SOLVER

        # adjust gurobi configuration if the problem is non-convex / quadratic
        if self.problem_class["grade"] > 1:
            self.m.params.NonConvex = 2

        # set maximum runtime if specified
        if "max_solver_time" in kwargs:
            self.m.setParam(
                GRB.Param.TimeLimit, iv.input(kwargs["max_solver_time"], "float")
            )

        # set solver method if specified
        if "solver_method" in kwargs:
            self.m.setParam(
                gp.GRB.Param.Method, iv.input(kwargs["solver_method"], "int")
            )

        # set barrier solve tolerance if specified
        if "barrier_tolerance" in kwargs:
            self.m.setParam(
                gp.GRB.Param.BarConvTol, iv.input(kwargs["barrier_tolerance"], "0..1")
            )

        # write log
        if self.log:
            print(f"CALLING THE SOLVER")

        # CALL SOLVER
        self.m.optimize()
        if self.enable_time_tracking:
            print(f"Solver Time: {round(time.time() - self.t_step, 2)}s")
            self.t_step = time.time()

        if not self.m.Status == GRB.TIME_LIMIT:
            # mark simulation as solved
            self.simulated = True
            # write log
            if self.log:
                print(" -> Simulation solved")
            if self.enable_time_tracking:
                print(
                    f"Time Required for factory solving: {time.time() - self.t_start}s"
                )
                self.t_start = time.time()  # reset timer

            # COLLECT THE RESULTS
            self.__collect_results(**kwargs)
            if self.enable_time_tracking:
                print(
                    f"Time Required for collecting results: {time.time() - self.t_start}s"
                )

        elif self.log:
            print("Solver time exceeded. Calculation aborted")

    def __validate_component(self, component):
        """
        This function checks, if the energy/material - conservation at a component has been fulfilled during simulation
        :param component: factory_components.component-object
        :return: True/False
        """

        # check, if the simulation has been simulated already
        if not self.simulated:
            raise Exception(
                f"ERROR: Cannot validate the results of the simulation, because it has not been simualted yet!"
            )

        # skip the routine if the component is a sink, source or slack
        if (
            component.type == "sink"
            or component.type == "source"
            or component.type == "slack"
        ):
            return True  # Sinks, sources and slacks don't have to be balanced

        # calculate the sum of inputs at the component
        [input_sum_energy, input_sum_material] = self.__calculate_component_input_sum(
            component
        )

        # calculate the sum of outputs at the component
        [
            output_sum_energy,
            output_sum_material,
        ] = self.__calculate_component_output_sum(component)

        # check the energy input/output equilibrium
        if not round(input_sum_energy, 3) == round(
            output_sum_energy, 3
        ):  # round to 3 digits to avoid false positives due to solver tolerances
            warnings.warn(
                f"WARNING: Energy is not conserved at component {component.name}! Input: {round(input_sum_energy)}    Output: {round(output_sum_energy)}"
            )
            return False

        # check the material input/output equilibrium
        if not round(input_sum_material, 3) == round(
            output_sum_material, 3
        ):  # round to 3 digits to avoid false positives due to solver tolerances
            warnings.warn(
                f"WARNING: Material is not conserved at component {component.name}! Input: {round(input_sum_material)}    Output: {round(output_sum_material)}"
            )
            return False

        return True

    def __validate_factory_architecture(self):
        """
        This function calls the factory.check_validity-method for the given factory and writes the corresponding log
        """
        if self.log:
            print("VALIDATING FACTORY ARCHITECTURE")
        if self.factory.check_validity():
            if self.log:
                print(" -> FACTORY IS VALID")

    def __validate_results(self):
        """
        This function takes a look at all the results of a simulation and performs some basic checks to confirm,
        that every equilibrium is met, no slacks have been used etc...
        :return: Sets self.simulation_valid as true or false
        """

        if not self.simulated:
            raise Exception(
                f"ERROR: Cannot validate the results of the simulation, "
                f"because it has not been simualted yet!"
            )

        if self.log:
            print("CHECKING RESULT CONSISTENCY")
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
                if component.flow.is_energy():
                    values_energy_in = np.append(
                        values_energy_in,
                        sum(self.result[component.name]["utilization"]),
                    )
                    names_energy_in.append(component.name)

                if component.flow.is_material():
                    values_material_in = np.append(
                        values_material_in,
                        sum(self.result[component.name]["utilization"]),
                    )
                    names_material_in.append(component.name)

            if component.type == "sink":
                if component.flow.is_energy():
                    values_energy_out = np.append(
                        values_energy_out,
                        sum(self.result[component.name]["utilization"]),
                    )
                    names_energy_out.append(component.name)

                if component.flow.is_material():
                    values_material_out = np.append(
                        values_material_out,
                        sum(self.result[component.name]["utilization"]),
                    )
                    names_material_out.append(component.name)

            if component.type == "slack":
                slack_utilization = round(
                    sum(self.result[component.name]["utilization"]), 3
                )
                if slack_utilization > 0:
                    values_slacks = np.append(values_slacks, slack_utilization)
                    names_slacks.append(component.name)
                    slacks_used = True
                    self.simulation_valid = False

        sum_energy_in = round(sum(values_energy_in), 3)
        sum_energy_out = round(sum(values_energy_out), 3)
        sum_material_in = round(sum(values_material_in), 3)
        sum_material_out = round(sum(values_material_out), 3)

        if sum_energy_in < sum_energy_out:
            warnings.warn(
                f"WARNING: There is Energy being created within the system! Input: {round(sum_energy_in)}   Output: {round(sum_energy_out)}"
            )
            self.simulation_valid = False

        if sum_energy_in > sum_energy_out:
            warnings.warn(
                f"WARNING: There is Energy being lost within the system! Input: {round(sum_energy_in)}   Output: {round(sum_energy_out)}"
            )
            self.simulation_valid = False

        if sum_material_in < sum_material_out:
            warnings.warn(
                f"WARNING: There is Material being created within the system! Input: {round(sum_energy_in)}   Output: {round(sum_energy_out)}"
            )
            self.simulation_valid = False

        if sum_material_in > sum_material_out:
            warnings.warn(
                f"WARNING: There is Material being lost within the system! Input: {round(sum_energy_in)}   Output: {round(sum_energy_out)}"
            )
            self.simulation_valid = False

        if slacks_used:
            df_slacks = {"values": values_slacks, "names": names_slacks}
            warnings.warn(
                f"WARNING: Slacks were needed to solve the optimization: {df_slacks}"
            )

        # Check, if the punishment term for ambient gains was chosen high enough
        if max(self.result["ambient_gains"]["utilization"]) > 10000000:
            warnings.warn(
                f"Warning: There is a high utilization of ambient gains! "
                f"This could be due to a numerical issue with the punishment-"
                f"term within factory_model.create_essentials(). "
                f"You should check the results for numerical issues!"
            )
            self.simulation_valid = False

        if self.log:
            if self.simulation_valid:
                print(" -> Simulation is valid!")
            else:
                print(" -> Simulation is invalid!")

    def write_results_to_excel(self, path):

        # check, that the simulation has already been performed
        if not self.simulated:
            warnings.warn(
                "The simulation has to be solved before the results can be exported. Calling the simulation method now..."
            )
            self.simulate()

        # check, that results have been collected
        if not self.results_collected:
            warnings.warn(
                "The simulation results have not been processed yet. Calling the result processing method now..."
            )
            self.__collect_results()

        # create a result dict with reduced depth:
        result_dict = {}
        for key, value in self.result.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    result_dict[f"{key}_{subkey}"] = subvalue
            else:
                result_dict[key] = value

        # create a new excel workbook
        workbook = xlsxwriter.Workbook(
            "C:\\Users\\smsikamm\\Documents\\Daten\\output.xlsx"
        )
        worksheet = workbook.add_worksheet()

        # iterate over all parameters and write each of them in an individual column in the excel file
        col = 0
        for key in result_dict.keys():
            # insert key names
            worksheet.write(0, col, key)

            # insert data
            if (
                isinstance(result_dict[key], int)
                or isinstance(result_dict[key], float)
                or isinstance(result_dict[key], bool)
            ):
                worksheet.write(1, col, result_dict[key])
            else:
                for row in range(len(result_dict[key])):
                    worksheet.write(row + 1, col, result_dict[key][row])

            # continue with next column in excel sheet
            col += 1

        workbook.close()

    def __calculate_component_input_sum(self, component):
        """
        This function calculates the sum of energy and material inputs that arrived at a component
        :param component: factory_components.component-object
        :return: input_sum_energy, input_sum_material: float
        """

        # prepare summing variables for energy and material
        input_sum_energy = 0
        input_sum_material = 0

        # iterate over all regular inputs
        for input_i in component.inputs:

            # add the total flow of the input to the sum of energy balance if it is an energy-input
            if input_i.flow.is_energy():
                input_sum_energy += sum(self.result[input_i.name])

            # add the total flow of the input to the sum of material balance if it is a material-input
            if input_i.flow.is_material():
                input_sum_material += sum(self.result[input_i.name])

        # if the components is a thermalsystem: add the thermal-gains input as well!
        if component.type == "thermalsystem":
            input_sum_energy += sum(self.result[component.from_gains.name])

        return input_sum_energy, input_sum_material

    def __calculate_component_output_sum(self, component):
        """
        This function calculates the sum of energy and material outputs that leave at a component
        :param component: factory_comonents.component-object
        :return: output_sum_energy, output_sum_material: float
        """

        # prepare summing variables for the outputs of energy and material
        output_sum_energy = 0
        output_sum_material = 0

        # iterate over all outputs
        for output_i in component.outputs:

            # add the flow of the output to the sum of energy outputs if it is an energy output
            if output_i.flow.is_energy():
                output_sum_energy += sum(self.result[output_i.name])

            # add the flow of the output to the sum of material outputs if it is a material output
            if output_i.flow.is_material():
                output_sum_material += sum(self.result[output_i.name])

        # if the component is a converter: add the energy and material losses as well
        if component.type == "converter":
            if not component.to_Elosses == []:
                output_sum_energy += sum(self.result[component.to_Elosses.name])
            if not component.to_Mlosses == []:
                output_sum_material += sum(self.result[component.to_Mlosses.name])

        # if the component is a storage or a thermalsystem: ad the energy or material losses as well
        if component.type == "storage" or component.type == "thermalsystem":

            # check, if the flow is energy or material and add the losses to the correct bilance
            if component.flow.is_energy():
                output_sum_energy += sum(self.result[component.to_losses.name])
            if component.flow.is_material():
                output_sum_material += sum(self.result[component.to_losses.name])

        # return calculated outputs
        return output_sum_energy, output_sum_material

    def __apply_threshold_and_rounding(self, data, threshold=float, decimals=int):
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
        data = data.round(decimals)

        # set all values < threshold to 0
        data[data < threshold] = 0

        # return results
        return data
