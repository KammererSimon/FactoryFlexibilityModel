# SCENARIO
# This script contains the scenario class wich is used to factory the outer circumstances for a simulation

# CODE START
class scenario:
    def __init__(self, name):
        self.cost_co2_per_kg = (
            0  # assumed additional external costs for emitting one kg of CO²
        )
        self.humidity = (
            []
        )  # float(array)  # 0..1          # timeseries of the outside air humidity, normalized (UNUSED)
        self.interest_rate = (
            []
        )  # float         # % p.a.        # assumed interest rate for invest calculations
        self.name = name
        self.number_of_timesteps = (
            []
        )  # int           # 1..n          # number of hours to be simulated, all timeseries to be cut to this length
        self.price_electricity = (
            []
        )  # float(array)  # €/kWh el      # timeseries of the price for one kWh of electricity
        self.price_gas = (
            []
        )  # float(array)  # €/kWh th      # timeseries of the price for one kWh of natural gas
        self.price_hydrogen = (
            []
        )  # float(array)  # €/kWh th      # timeseries of the price for one kWh of hydrogen
        self.price_district_heating = (
            []
        )  # float(array)  # €/kWh th      # timeseries of the price for one kWh of district heating
        self.revenue_electricity = (
            []
        )  # float(array)  # €/kWh el      # timeseries of the selling price of one kWh electricity
        self.solar_radiation = (
            []
        )  # float(array)  # 0..1          # timeseries of the incoming solar radiation, normalized to the utilization of the usage of installed peak power
        self.temperature = (
            []
        )  # float(array)  # °C            # timeseries of the outside temperatures
        self.timefactor = 1  # float         # Factor        # How many hours does one timestep in the scenario represent? standard-value: 1Timestep = 1Hour
        self.windspeed = (
            []
        )  # float(array)  # 0..1          # timeseries of the outside windspeeds, normalized to the utilization of the usage of installed peak power (UNUSED)
