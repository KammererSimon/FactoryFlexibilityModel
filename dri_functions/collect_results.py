# this script goes through the given folder, imports all sim-files found there and creates an excel file with all data required for the study

import pandas as pd
import os
from factory_flexibility_model.io.factory_import import import_simulation

def collect_results():
    #filepath = f"{os.getcwd()}\\simulations\\output_data\\DRI_Auswertung.xlsx"
    filepath = "F:\\FactoryFlexibilityModel\\DRI Simulations\\DRI_Auswertung.xlsx"
    #filepath_simulations = f"{os.getcwd()}\\simulations\\output_data\\simulations_solved"
    filepath_simulations = "F:\\FactoryFlexibilityModel\\DRI Simulations\\simulations_solved"

    # initialize output dataframe
    data = pd.DataFrame(columns=["Layout", "cost_natural_gas", "avg_cost_electricity", "volantility_electricity", "cost_CO2", "CO2_reduction",
                     "co2_per_ton", "cost_per_ton", "hbi_storage_rate", "co2_capture_rate", "cost_electricity"])

    # add row descriptions to dataframe
    data = data._append({"file": "Name of the simulation file",
                        "Layout": "Which of the three DRI Layouts was used for this run?",
                        "cost_natural_gas": "Fixed natural Gas price in [€/t]",
                        "avg_cost_electricity": "Average cost of the electricity timeseries in [€/MWh]",
                        "volantility_electricity": "An index describing the peak-to-peak value that the underlying timeseries has been scaled to. 0=stationary, 1=original, 2=doubled, etc..",
                        "cost_CO2": "Fixed price for CO2-allowances in [€/tCO2]",
                        "co2_reduction": "Ratio of which emissions are reduced compared to blastfurnance case",
                        "co2_per_ton": "Amount of resulting CO2 emissions of the steel production [tCO2/tLS]",
                        "cost_per_ton": "OPEX of the steel production [€/tLS]",
                        "hbi_storage_rate": "Ratio of total DRI taking the storage path vs the total amount of DRI being fed into EAF [%]",
                        "co2_capture_rate": "Ratio of captured CO2 vs produced CO2 [%]",
                        "rate_h2_in_dri": "Ratio of DRI produced using Hydrogen vs total DRI production volume [%]",
                        "solver_time": "Required runtime of the simulation [s]",
                        "cost_electricity": "Average cost of purchased electricity resulting from the optimized operation profile [€/MWh]",
                        "emissions_electricity": "Are scope 2 electricity emissions considered in this run?",
                        "electricity_savings_ratio": "Average cost of purchased electricity / Average market price of electricity"}, ignore_index=True)


    file_list = []
    for root, dirs, files in os.walk(filepath_simulations):
        for file in files:
            if file.endswith(".sim"):
                file_list.append(os.path.join(root, file))

    i= 0
    for file in file_list:
        i+=1
        print(f"importing file {i}")

        try:
            simulation = import_simulation(file)
            factory = simulation.factory

            # calculate cost per ton of produced crude steel
            cost_per_ton = simulation.result["objective"] / sum(
                simulation.result[factory.get_key("Crude Steel Out")]["utilization"])
            if cost_per_ton > 2500:
                cost_per_ton = 2500 #2500 only occurs in runs with a failed co2-target -> limit doesnt matter and just makes plots easier to reád

            # calculate co2 emissions per ton of produced crude steel
            co2_per_ton = sum(simulation.result["total_emissions"]) / sum(
                simulation.result[factory.get_key("Crude Steel Out")]["utilization"])

            if simulation.info["layout"] == "CCS":
                # calculate co2 capture rate
                co2_capture_rate = sum(simulation.result[factory.get_key('CCS -> CO2 Storage')]) / sum(
                    simulation.result[factory.get_key('Natural Gas DRI -> Pool CO2')])
            else:
                co2_capture_rate = 0

            # calculate ratio of H2 and NG used for DRI
            if simulation.info["layout"] == "Partial":
                rate_h2_in_dri = sum(simulation.result[factory.get_key('Hydrogen DRI -> DRI Composition')]) / sum(
                    simulation.result[factory.get_key("DRI Composition")]["utilization"])
            elif simulation.info["layout"] == "CCS":
                rate_h2_in_dri = 0
            else:
                rate_h2_in_dri = 1


            # calculate hbi_storage_rate
            hbi_storage_rate = sum(simulation.result[factory.get_key('Pool DRI -> DRI Compactor')]) / sum(
                simulation.result[factory.get_key("Pool DRI")]["utilization"])

            # figure out if electricity emissions had been considered
            emissions_electricity = round(factory.components[factory.get_key('Electricity Grid')].co2_emissions_per_unit[0] / 0.09380399 * 0.2, 2)

            # calculate achieved electricity price
            cost_electricity = (sum(simulation.result[factory.get_key('Electricity Grid')]["utilization"] *
                                    simulation.scenario.configurations[factory.get_key("Electricity Grid")]["cost"])+
                                sum(simulation.result[factory.get_key('Electricity Slack')]["utilization"] *
                                    simulation.scenario.configurations[factory.get_key("Electricity Slack")]["cost"]))/ (
                sum(simulation.result[factory.get_key('Electricity Slack')]["utilization"])
                + sum(simulation.result[factory.get_key('Electricity Grid')]["utilization"]))

            electricity_savings_ratio = cost_electricity / simulation.info["avg_electricity_price"]

            data = data._append({"file": file,
                                "Layout": simulation.info["layout"],
                                "cost_natural_gas": simulation.info["natural_gas_cost"],
                                "avg_cost_electricity": simulation.info["avg_electricity_price"],
                                "volantility_electricity": simulation.info["volatility"],
                                "cost_CO2": simulation.info["co2_price"],
                                "co2_reduction": simulation.info["co2_reduction"],
                                "co2_per_ton": co2_per_ton,
                                "cost_per_ton": cost_per_ton,
                                "hbi_storage_rate": hbi_storage_rate,
                                "co2_capture_rate": co2_capture_rate,
                                "rate_h2_in_dri": rate_h2_in_dri,
                                "solver_time": simulation.info["solver_time"],
                                "cost_electricity": cost_electricity,
                                "emissions_electricity": emissions_electricity,
                                "electricity_savings_ratio": electricity_savings_ratio}, ignore_index=True)
        except:
            print(f"failed to import simulation '{file}'")

    data.to_excel(filepath, index=False)
