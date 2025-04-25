
import factory_flexibility_model.io.factory_import as imp
import factory_flexibility_model.io.xlsx_io as xlsx
def dash():
    print("Opening Dashboard")
    simulation_file = f"C:\\Users\\Simon\\PycharmProjects\\WattsInsight\\simulations\\Partial_epex_2023_NG2100_EL220_VOL0.25_CO2200_Reduction0_ElectricityEmissions_0.5.sim"
    simulation = imp.import_simulation(simulation_file)
    simulation.create_dash()
