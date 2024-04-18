
import factory_flexibility_model.io.factory_import as imp

def dash():
    simulation_file = f"C:\\Users\\smsikamm\\PycharmProjects\\DRI_Study\\simulations\\output_data\\simulations_solved\\CCS_epex_2023_NG2200_EL40_VOL0.5_CO20_Reduction50_1.sim"
    simulation = imp.import_simulation(simulation_file)
    simulation.create_dash()
