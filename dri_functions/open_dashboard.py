
import factory_flexibility_model.io.factory_import as imp

def dash():
    simulation_file = f"C:\\Users\\smsikamm\\PycharmProjects\\DRI_Study\\simulations\\output_data\\simulations_solved\\Partial_NG1310_EL289_VOL0.5_CO286_Reduction80_1.sim"
    simulation = imp.import_simulation(simulation_file)
    simulation.create_dash()
