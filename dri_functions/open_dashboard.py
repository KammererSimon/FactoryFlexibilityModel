
import factory_flexibility_model.io.factory_import as imp
import factory_flexibility_model.io.xlsx_io as xlsx
def dash():
    print("Opening Dashboard")
    simulation_file = f"C:\\Users\\smsikamm\\PycharmProjects\\FactoryFlexibilityModel\\simulations\\output_data\\simulations_solved\\CCS_epex_2023_NG200_EL60_VOL0_CO20_Reduction0_2_ElectricityEmissions_0.sim"
    simulation = imp.import_simulation(simulation_file)
    print(simulation.result["component_1"])
    simulation.create_dash()
