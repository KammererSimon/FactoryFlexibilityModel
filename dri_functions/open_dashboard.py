
import factory_flexibility_model.io.factory_import as imp
import factory_flexibility_model.io.xlsx_io as xlsx
def dash():
    print("Opening Dashboard")
    simulation_file = f"C:\\Users\\Simon\\PycharmProjects\\WattsInsight\\simulations\\output_data\\simulations_solved\\CCS_epex_2023_NG200_EL20_VOL0_CO20_Reduction0_ElectricityEmissions_0.25.sim"
    simulation = imp.import_simulation(simulation_file)
    simulation.create_dash()
