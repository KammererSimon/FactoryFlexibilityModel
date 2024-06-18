"""
    .. _Simulation:

    This Script contains the Simulation class of the factory factory. It is used to store Factory-Scenario-Combinations and to perform the Simulation itself on them
    The following Methods are meant to be used by external Scripts to prepare a Simulation:
    self.__init__
    self.set_factory
    self.set_name
    self.set_scenario

    The Simulation itself is conducted by the Method:
    self.simulate
    -> This method calls all the other internal functions to build an optimization problem out of the components specified in the factory

    To get the results use:
    self.create_dash
    self.show_results
"""

# IMPORTS
import logging
import pickle
import time
from datetime import datetime
from pathlib import Path

import gurobipy as gp
import numpy as np
from gurobipy import GRB

import factory_flexibility_model.io.input_validations as iv
import factory_flexibility_model.simulation.optimization_components as oc
from factory_flexibility_model.dash import dash as fd
from factory_flexibility_model.io.set_logger import set_logging_level


class Simulation:
    def __init__(
        self,
        *,
        scenario=None,
        factory=None,
        enable_time_tracking=False,
        name="Unspecified Simulation",
        mode: str = "full",
        big_m: float = 1000000,
    ):
        """
        :param enable_time_tracking: Set to true if you want to track the time required for Simulation
        """
        # set general data for the Simulation
        self.big_m = big_m
        self.date_simulated = "NOT_SIMULATED"
        self.enable_time_tracking = enable_time_tracking
        self.factory = factory  # Variable to store the factory for the Simulation
        self.interval_length = None  # realtime length of one Simulation interval...to be taken out of the scenario
        self.info = None  # Free attribute to store additional information
        self.m = None  # Placeholder for the Gurobi-Model to be created
        self.mode = mode  # solving strategy for the simulation. {"full", "rolling"}
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
            "%d.%m.%Y %H-%M-%S"
        )  # date/time of the creation of the Simulation object

    def __collect_results(
        self, *, threshold: float = None, rounding_decimals: int = None, interval_length: int = 0, t_start: int = 0
    ):
        """
        This function collects all the Simulation results of the Simulation object and writes them in a
        single dictionary under Simulation.results.
        :param threshold: [float] Threshold under which numerical values are considered as zero
        :param rounding_decimals: [int] Number of decimals that values are rounded to
        :param interval_length: [int] length of the current simulation interval
        :return: self.results is being created
        """

        logging.info("COLLECTING RESULTS")

       #check if this is the first iteration
        if self.result is None:
            # if yes: initialize detailled result struct
            first_iteration = True
            self.result = {}
            self.result["energy_generated_onsite"] = 0
            self.result["energy_generated_offsite"] = 0
            self.result["energy_consumed_onsite"] = 0
            self.result["energy_consumed_offsite"] = 0
            self.result["costs"] = {
                "inputs": {},
                "outputs": {},
                "converter_ramping": {},
                "capacity_provision": {},
                "emission_allowances": {},
                "slacks": {},
            }
        else:
            # if no: set indicator
            first_iteration = False

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
            if first_iteration:
                self.result[connection.key] = result_i
            else:
                self.result[connection.key] = np.hstack((self.result[connection.key], result_i))


        # collect all Component specific timeseries: iterate over all components
        for component in self.factory.components.values():

            # handle pools
            if component.type == "pool":

                # get the sum of the throughput as timeseries
                utilization = sum(
                    component.inputs[input_id].weight
                    * self.MVars[component.inputs[input_id].key].X
                    for input_id in range(len(component.inputs))
                )

                # apply threshold and rounding
                utilization = self.__apply_threshold_and_rounding(
                    utilization, threshold, rounding_decimals
                )

                # write the results into the result dictionary
                if first_iteration:
                    self.result[component.key] = {"utilization": utilization}
                else:
                    self.result[component.key]["utilization"] = np.hstack((self.result[component.key]["utilization"], utilization))


            # handle converters
            if component.type == "converter":

                # get the result values, round them to the specified number of digits
                utilization = self.MVars[f"P_{component.key}"].X
                efficiency = self.MVars[f"Eta_{component.key}"].X

                if component.rampup_cost > 0:
                    rampup_cost = round(
                        sum(self.MVars[f"P_rampup_{component.key}"].X)
                        * component.rampup_cost,
                        2,
                    )

                else:
                    rampup_cost = 0

                if component.capacity_charge > 0:
                    capacity_charge = (
                        self.MVars[f"P_max_{component.key}"].X
                        * component.capacity_charge
                        * self.interval_length
                        * self.T
                        / 8760
                    )
                    capacity_charge = round(capacity_charge[0], 2)
                else:
                    capacity_charge = 0

                # apply threshold and rounding on all values
                utilization = self.__apply_threshold_and_rounding(
                    utilization, threshold, rounding_decimals
                )
                efficiency = self.__apply_threshold_and_rounding(
                    efficiency, threshold, rounding_decimals
                )

                # write results into the result-dictionary
                if first_iteration:
                    self.result[component.key] = {
                        "utilization": utilization,
                        "efficiency": efficiency,
                        "capacity_charge": capacity_charge,
                        "rampup_cost": rampup_cost,
                    }
                else:
                    self.result[component.key]["utilization"] = np.hstack((self.result[component.key]["utilization"], utilization))
                    self.result[component.key]["efficiency"] = np.hstack((self.result[component.key]["efficiency"], efficiency))
                    self.result[component.key]["capacity_charge"] += capacity_charge
                    self.result[component.key]["rampup_cost"] += rampup_cost


            # handle heatpumps
            if component.type == "heatpump":
                # get the result values, round them to the specified number of digits
                utilization = self.MVars[f"P_{component.key}"].X
                input_heat = self.MVars[f"{component.input_gains.key}"].X
                output_heat = self.MVars[f"{component.outputs[0].key}"].X


                # apply threshold and rounding on all values
                utilization = self.__apply_threshold_and_rounding(
                    utilization, threshold, rounding_decimals
                )
                input_heat = self.__apply_threshold_and_rounding(
                    input_heat, threshold, rounding_decimals
                )

                output_heat = self.__apply_threshold_and_rounding(
                    output_heat, threshold, rounding_decimals
                )

                # write results into the result-dictionary
                if first_iteration:
                    self.result[component.key] = {
                        "utilization": utilization,
                        "input_electricity": utilization,
                        "input_heat": input_heat,
                        "output_heat": output_heat
                    }
                else:
                    self.result[component.key]["utilization"] = np.hstack((self.result[component.key]["utilization"], utilization))
                    self.result[component.key]["input_electricity"] = np.hstack((self.result[component.key]["input_electricity"], utilization))
                    self.result[component.key]["input_heat"] = np.hstack((self.result[component.key]["input_heat"], input_heat))
                    self.result[component.key]["output_heat"] = np.hstack((self.result[component.key]["output_heat"], output_heat))


            # handle sinks
            if component.type == "sink":

                # is the power of the sink determined?
                if component.determined:
                    # if yes: use the demand timeseries
                    utilization = component.demand[t_start:t_start+interval_length+1]

                else:
                    # if no: use the simulation result
                    utilization = self.MVars[f"E_{component.key}"].X

                # apply rounding and threshold
                utilization = self.__apply_threshold_and_rounding(
                    utilization, threshold, rounding_decimals
                )

                if self.factory.emission_cost is None:
                    self.factory.emission_cost = 0

                # calculate the emissions created by the sink
                if component.causes_emissions:
                    emissions = (
                        utilization * component.co2_emissions_per_unit[0 : self.T]
                    )
                    emission_cost = round(
                        sum(emissions) * self.factory.emission_cost, 2
                    )


                    # add avoided costs and emissions to the summing variables
                    total_emissions += emissions
                    total_emission_cost += emission_cost

                    logging.info(
                        f"Sink {component.name} caused total emissions of {round(sum(emissions), 2)} kgCO2, costing {round(emission_cost, 2)}€"
                    )

                else:
                    # otherwise set zeros:
                    emissions = 0
                    emission_cost = 0

                # calculate total costs
                if component.refundable:
                    revenue = round(sum(utilization * component.revenue[t_start:t_start+interval_length+1]), 2)
                else:
                    revenue = 0

                if component.chargeable:
                    cost = round(sum(utilization * component.cost[t_start:t_start+interval_length+1]), 2)
                else:
                    cost = 0

                # write the result into the result-dictionary
                if first_iteration:
                    self.result[component.key] = {
                        "utilization": utilization,
                        "emissions": emissions,
                        "emission_cost": emission_cost,
                        "utilization_cost": cost - revenue,
                    }
                    self.result["costs"]["emission_allowances"][component.key] = emission_cost
                    self.result["costs"]["outputs"][component.key] = cost - revenue

                else:
                    self.result[component.key]["utilization"] = np.hstack((self.result[component.key]["utilization"], utilization))
                    self.result[component.key]["emissions"] = np.hstack((self.result[component.key]["emissions"], emissions))
                    self.result[component.key]["emission_cost"] += emission_cost
                    self.result[component.key]["utilization_cost"] += (cost-revenue)
                    self.result["costs"]["emission_allowances"][component.key] += emission_cost
                    self.result["costs"]["outputs"][component.key] += (cost - revenue)


                # add the sinks contribution to onsite/offsite demand calculation
                if component.is_onsite:
                    self.result["energy_consumed_onsite"] += sum(utilization)
                else:
                    self.result["energy_consumed_offsite"] += sum(utilization)


            # handle sources
            elif component.type == "source":

                # is the power of the source determined by a timeseries?
                if component.determined:
                    # if yes: use the given timeseries
                    utilization = component.determined_power[t_start:t_start+interval_length+1]
                else:
                    # if no: use Simulation result
                    utilization = self.MVars[f"E_{component.key}"].X

                # apply rounding and threshold
                utilization = self.__apply_threshold_and_rounding(
                    utilization, threshold, rounding_decimals
                )

                # calculate the emissions caused by the source
                if component.causes_emissions:
                    if self.factory.emission_cost is None:
                        self.factory.emission_cost = 0
                    # if the source can generate emissions: calculate the emissions and the corresponding costs
                    emissions = (
                        utilization * component.co2_emissions_per_unit[t_start:t_start+interval_length+1]
                    )
                    emission_cost = round(
                        sum(emissions) * self.factory.emission_cost, 2
                    )

                    # add the emissions and cost to the summing variables:
                    total_emissions += emissions
                    total_emission_cost += emission_cost

                    logging.info(
                        f"Source {component.name} caused total emissions of {round(sum(emissions),2)} kgCO2, costing additional {round(emission_cost,2)}€"
                    )
                else:
                    emissions = 0
                    emission_cost = 0

                if component.chargeable and not component.key == "ambient_gains":
                    cost = round(sum(component.cost[t_start:t_start+interval_length+1] * utilization), 2)
                else:
                    cost = 0

                # calculate occuring capacity charge if necessary
                if component.capacity_charge > 0:
                    capacity_charge = round(
                        max(utilization)
                        * component.capacity_charge
                        * self.interval_length
                        * self.T
                        / 8760,
                        2,
                    )

                else:
                    capacity_charge = 0

                # write the result into the result-dictionary
                if first_iteration:
                    self.result[component.key] = {
                        "utilization": utilization,
                        "emissions": emissions,
                        "emission_cost": emission_cost,
                        "utilization_cost": cost,
                        "capacity_charge": capacity_charge,
                    }
                    self.result["costs"]["emission_allowances"][component.key] = emission_cost
                    self.result["costs"]["inputs"][component.key] = cost
                    self.result["costs"]["capacity_provision"][component.key] = capacity_charge
                else:
                    self.result[component.key]["utilization"] = np.hstack((self.result[component.key]["utilization"],utilization))
                    self.result[component.key]["emissions"] = np.hstack((self.result[component.key]["emissions"], emissions))
                    self.result[component.key]["emission_cost"] += emission_cost
                    self.result[component.key]["utilization_cost"] += cost
                    self.result[component.key]["capacity_charge"] += capacity_charge
                    self.result["costs"]["emission_allowances"][component.key] += emission_cost
                    self.result["costs"]["inputs"][component.key] += cost
                    self.result["costs"]["capacity_provision"][component.key] += capacity_charge

                # add the sources contribution to onsite/offsite generation calculation
                if component.is_onsite:
                    self.result["energy_generated_onsite"] += sum(utilization)
                else:
                    self.result["energy_generated_offsite"] += sum(utilization)



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
                if first_iteration:
                    self.result[component.key] = {
                        "EPos": sum_energy_pos,
                        "ENeg": sum_energy_neg,
                        "utilization": utilization,
                    }
                    self.result["costs"]["slacks"][component.key] = (sum(utilization) * 1000000000)
                else:
                    self.result[component.key]["EPos"] += sum_energy_pos
                    self.result[component.key]["ENeg"] += sum_energy_neg
                    self.result[component.key]["utilization"]+= utilization
                    self.result["costs"]["slacks"][component.key] += (sum(utilization) * 1000000000)


            # handle storages
            elif component.type == "storage":
                # read the result timeseries from the Simulation
                power_charge = (
                    self.MVars[component.inputs[0].key].X / self.interval_length
                )
                power_discharge = (
                    self.MVars[component.outputs[0].key].X / self.interval_length
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

                soc_max = max(soc)

                # calculate occuring capacity charge if necessary
                if component.capacity_charge > 0:
                    capacity_charge = round(
                        soc_max
                        * component.capacity_charge
                        * self.interval_length
                        * self.T
                        / 8760,
                        2,
                    )

                else:
                    capacity_charge = 0

                # write the results to the result dictionary
                if first_iteration:
                    self.result[component.key] = {
                        "Pcharge": power_charge,
                        "Pdischarge": power_discharge,
                        "SOC": soc,
                        "utilization": power_discharge - power_charge,
                        "SOC_start": soc_start,
                        "soc_max": soc_max,
                        "capacity_charge": capacity_charge,
                    }
                    self.result["costs"]["capacity_provision"][component.key] = capacity_charge
                else:
                    self.result[component.key]["Pcharge"] = np.hstack((self.result[component.key]["Pcharge"], power_charge))
                    self.result[component.key]["Pdischarge"] = np.hstack((self.result[component.key]["Pdischarge"], power_discharge))
                    self.result[component.key]["SOC"] = np.hstack((self.result[component.key]["SOC"], soc))
                    self.result[component.key]["utilization"] = np.hstack((self.result[component.key]["utilization"], power_discharge - power_charge))
                    self.result[component.key]["soc_max"] = max(soc_max,self.result[component.key]["soc_max"])
                    self.result[component.key]["capacity_charge"] += capacity_charge
                    self.result["costs"]["capacity_provision"][component.key] += capacity_charge


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

        if first_iteration:
            # collect achieved costs/revenues (objective of target function - ambient_gain_punishment_term)
            if "ambient_gains" in self.factory.components:
                self.result["objective"] = self.m.objVal - sum(
                    self.result["ambient_gains"]["utilization"]
                    * self.factory.components["ambient_gains"].cost[0 : self.T]
                )
            else:
                self.result["objective"] = self.m.objVal

        else:
            # collect achieved costs/revenues (objective of target function - ambient_gain_punishment_term)
            if "ambient_gains" in self.factory.components:
                self.result["objective"] += self.m.objVal - sum(
                    self.result["ambient_gains"]["utilization"]
                    * self.factory.components["ambient_gains"].cost[t_start:t_start+interval_length+1]
                )
            else:
                self.result["objective"] += self.m.objVal

            # write the total emission values to the result-dictionary
            self.result["total_emissions"] = total_emissions
            self.result["total_emission_cost"] = total_emission_cost


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
                if "weight" in config.keys():
                    self.factory.connections[key].weight = config["weight"]
                if "to_losses" in config.keys():
                    if config["to_losses"]:
                        self.factory.connections[key].type = "losses"

    def save(self, file_path: str, *, name: str = None, overwrite: bool = False):
        """
        This function saves a Simulation-object under the specified filepath as a single file.
        :param file_path: [string] Path to the file to be created
        :param name: [sring] Option to give the saved simulation a specific name
        :param override: [boolean] Set True to allow the method to overwrite existing files.
        Otherwise an error will occur when trying to overwrite a file
        :return: Nothing
        """

        # create the filename
        if name is None:
            filename = rf"{file_path}\{self.name} ({self.date_simulated}).sim"
        else:
            filename = rf"{file_path}\{name}.sim"

        # check, if file already exists
        file = Path(filename)
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
        simulation_data.emission_sources = []

        # save the factory at the given path
        with open(filename, "wb") as f:
            pickle.dump(simulation_data, f)

        logging.info(f"SIMULATION SAVED under{filename}")

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
        interval_length: int = None,
        rounding_decimals: int = None,
        solver_config: dict = {},
        threshold: float = None,
    ):
        """
        This function manages the simulation. It prepares the necessary data, splits the simulation into rolling intervals and collects the results.

        :param interval_length: [int] Length of individually solved intervals during rolling optimization. A value of None means, that the whole simulation is solved at once.
        :param rounding_decimals: [int] Number of decimals that the results are rounded to
        :param solver_config: [dict] Optional dict with configuration parameters for the solver (max_solver_time, barrier_tolerance, solver_method, logger_level)
        :param threshold: [float] Threshold under whoch results are interpreted as zero
        :return: [True] -> Adds an attribute .result to the Simulation object
        """

        # ENABLE LOGGING/TIMETRACKING?
        if self.enable_time_tracking:
            self.t_start = time.time()

        if "logger_level" in solver_config:
            set_logging_level(solver_config["logger_level"])

        # PREPARATIONS
        self.problem_class = {"grade": 1, "type": "float"}

        # Write timestamp
        now = datetime.now()
        self.date_simulated = now.strftime("%d.%m.%Y %H-%M-%S")  # write timestamp

        # Validate factory architecture
        self.__validate_factory_architecture()

        # Configure the timefactor as specified in the scenario:
        self.interval_length = (
            self.scenario.timefactor
        )  # The length of one Simulation timestep in hours is taken from the scenario
        self.T = self.factory.timesteps

        # calculate time_reference_factor
        self.time_reference_factor = (
            self.scenario.timefactor / self.factory.timefactor
        )  # a conversion factor that implies, how many factory related timesteps are represented by one Simulation timestep

        # writelog
        logging.debug(
            f"   Timefactor of the Simulation set to: 1 timestep == {self.scenario.timefactor} hours ({self.scenario.timefactor*60} minutes)"
        )

        # READ SCENARIO DATA CONFIGURATIONS INTO FACTORY
        self.__read_scenario_data()

        # INITIALIZE RESULT DICT
        self.result = None


        # ITERATE OVER SIMULATION INTERVALS
        if interval_length is None:
            logging.info(f"No interval size specified. The simulation will be solved in one run.")
            interval_length = self.T

        if interval_length > self.T:
            logging.warning(f"The given simulation interval length ({interval_length}) is greater than the total number of simulation timesteps ({self.T}). The simulation will be solved in one run.")
            interval_length = self.T

        # determine number of required simulation intervals using integer division
        num_of_intervals = int(self.T//interval_length)

        # add an additional overflow interval for the incomplete final interval if required
        if self.T % interval_length > 0:
            num_of_intervals += 1

        # start iteration
        for interval in range(num_of_intervals):
            # determine first and last timestep of the current interval
            t_start = int(interval * interval_length)
            t_end = int(t_start + interval_length - 1)
            # make sure, that t_end is no later than the last valid timestep of the simulation task
            if t_end > self.T-1:
                t_end = self.T-1

            # Call simulation routine for current interval
            logging.info(f"Simulating Interval {interval+1} [{t_start+1} : {t_end+1}]")
            self.__simulate_interval(t_start, t_end, solver_config, threshold, rounding_decimals)

        # validate results
        self.__validate_results()

        # mark Simulation as solved
        self.simulated = True
        logging.info(" -> Simulation solved")
        if self.enable_time_tracking:
            logging.info(
                f"Time Required for solving: {time.time() - self.t_start}s"
            )


    def __simulate_interval(self, t_start, t_end, solver_config, threshold, rounding_decimals):
        """
        This function builds and solves an optimization problem for a specific interval of the simulation timeframe. It is being called from the simulation.simulate() function.

        :param t_start: [int] first timestep of the simulation interval to solve
        :param t_end: [int] last timestep of the simulation interval to solve
        """

        # INITIALIZE GUROBI MODEL
        logging.info("STARTING SIMULATION")

        # create new gurobi model
        self.m = gp.Model("Factory")

        # set solver logging
        if "log_solver" in solver_config:
            if not solver_config["log_solver"]:
                self.m.Params.LogToConsole = 0
                self.m.setParam("OutputFlag", 0)

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

        # ENABLE EMISSION ACCOUNTING IF NECESSARY
        if self.factory.emission_accounting:
            logging.info("ENABLING EMISSION ACCOUNTING")
            self.emission_sources = (
                list()
            )  # list of emission terms that need to be added up to calculate the total emissions

        # BUILDING OPTIMIZATION PROBLEM
        logging.info("BUILDING OPTIMIZATION PROBLEM")

        if self.enable_time_tracking:
            logging.info(f"Preperations: {round(time.time()-self.t_start,2)}s")
            self.t_step = time.time()

        # CREATE MVARS FOR ALL FLOWS IN THE FACTORY
        oc.add_flows(self, t_end-t_start+1)

        # CREATE MVARS AND CONSTRAINTS FOR ALL COMPONENTS IN THE FACTORY
        for component in self.factory.components.values():
            if component.type == "source":
                oc.add_source(self, component, t_start, t_end)
            elif component.type == "heatpump":
                oc.add_heatpump(self, component, t_start, t_end)
            elif component.type == "pool":
                oc.add_pool(self, component)
            elif component.type == "sink":
                oc.add_sink(self, component, t_start, t_end)
            elif component.type == "slack":
                oc.add_slack(self, component, t_start, t_end)
            elif component.type == "converter":
                oc.add_converter(self, component, t_start, t_end)
            elif component.type == "deadtime":
                oc.add_deadtime(self, component, t_start, t_end)
            elif component.type == "storage":
                oc.add_storage(self, component, t_start, t_end)
            elif component.type == "thermalsystem":
                oc.add_thermalsystem(self, component, 720)
            elif component.type == "triggerdemand":
                oc.add_triggerdemand(self, component, t_start, t_end)
            elif component.type == "schedule":
                oc.add_schedule(self, component, 720)

            if self.enable_time_tracking:
                logging.info(
                    f"Adding {component.type} {component.name}: {round(time.time() - self.t_step, 2)}s"
                )
                self.t_step = time.time()

        # SET EMISSION RELATED COSTS AND CONSTRAINTS
        if self.factory.emission_accounting:
            # add MVar to keep track of total caused emissions
            self.MVars["total_emissions"] = self.m.addMVar(
                1, vtype=GRB.CONTINUOUS, name="total_emissions"
            )

            # calculate the total emissions throughout the entire factory layout
            self.m.addConstr(
                self.MVars[f"total_emissions"]
                == sum(
                    self.emission_sources[i] for i in range(len(self.emission_sources))
                )
            )

            # add cost term for emissions
            if self.factory.emission_cost is not None:
                self.C_objective.append(
                    self.m.addMVar(1, vtype=GRB.CONTINUOUS, name=f"C_emissions")
                )
                self.m.addConstr(
                    self.C_objective[-1]
                    == self.MVars["total_emissions"] * self.factory.emission_cost
                )
                logging.debug(
                    f"        - CostFactor:   Costs for CO2 emission allowances"
                )

            # set constraint for the emission limit
            if self.factory.emission_limit is not None:
                self.m.addConstr(
                    self.MVars[f"total_emissions"] <= self.factory.emission_limit
                )
                logging.debug(
                    f"        - Constraint:   Total Emissions <= Emission Limit"
                )

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
        oc.solve(self, solver_config)

        if self.m.Status == GRB.TIME_LIMIT:
            logging.error("Solver time exceeded. Calculation aborted")
            raise Exception

        # COLLECT THE RESULTS
        self.__collect_results(threshold=threshold, rounding_decimals=rounding_decimals, interval_length=t_end-t_start, t_start=t_start)


    def __validate_component(self, component):
        """
        This function checks, if the energy/material - conservation at a Component has been fulfilled during Simulation
        :param component: [factory.components.Component-object]
        :return: [Boolean] True if Component result is valid
        """

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
                continue  # todo: remove this after fixing the slack problem
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

        if "ambient_gains" in self.result:
            if sum(self.result["ambient_gains"]["utilization"]) > 10000000:
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
