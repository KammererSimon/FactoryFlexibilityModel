def define_component_parameters():
    # define list of attributes to be considered for the different component types
    converter_parameters = {
        "ratios": {"text": "Inputs/Outputs", "description": "", "unit_type": ""},
        "power_max": {
            "text": "Maximum Operating Point",
            "description": "Maximum Conversion Rate per Timestep",
            "unit_type": "flowrate_primary",
        },
        "power_min": {
            "text": "Minimum Operating Point",
            "description": "Minimum Conversion Rate per Timestep",
            "unit_type": "flowrate_primary",
        },
        "availabiity": {
            "text": "Availability",
            "description": "Availability of Pmax",
            "unit_type": "%",
        },
        "max_pos_ramp_power": {
            "text": "Positive Ramping",
            "description": "Maximum Ramp Up",
            "unit_type": "ramping",
        },
        "max_neg_ramp_power": {
            "text": "Negative Ramping",
            "description": "Maximum Ramp Down",
            "unit_type": "ramping",
        },
        "eta_max": {
            "text": "Best Efficiency",
            "description": "Maximum Efficiency at nominal operating Point",
            "unit_type": "%",
        },
        "power_nominal": {
            "text": "Nominal Operating Point",
            "description": "Operating Point of Max Efficiency",
            "unit_type": "flowrate_primary",
        },
        "delta_eta_high": {
            "text": "Upper Efficiency Drop",
            "description": "Rate of efficiency drop when exceeding nominal operating point",
            "unit_type": "efficiency_drop",
        },
        "delta_eta_low": {
            "text": "Lower Efficiency Drop",
            "description": "Rate of efficiency drop when operating below nominal operating point",
            "unit_type": "efficiency_drop",
        },
    }
    deadtime_parameters = {
        "delay": {
            "text": "Delay",
            "description": "Delay Number of Timesteps",
            "unit_type": "timesteps",
        }
    }
    schedule_parameters = {
        "power_max": {
            "text": "Max Throughput",
            "description": "Maximum Total Flowrate",
            "unit_type": "flowrate",
        },
        "demands": {
            "text": "Demands",
            "description": "List of individual Demands",
            "unit_type": "integer",
        },
    }
    sink_parameters = {
        "cost": {
            "text": "Cost",
            "description": "Cost per Unit of Utilization",
            "unit_type": "currency",
        },
        "power_max": {
            "text": "Maximum Input",
            "description": "Maximum Input Flowrate",
            "unit_type": "flowrate",
        },
        "power_min": {
            "text": "Minimum Input",
            "description": "Minimum Input Flowrate",
            "unit_type": "flowrate",
        },
        "demand": {
            "text": "Demand",
            "description": "Endogenous given Demand",
            "unit_type": "flowrate",
        },
        "max_total_input": {
            "text": "Maximum Cumulative Input",
            "description": "Maximum cumulative input over all timesteps",
            "unit_type": "flow",
        },
        "revenue": {
            "text": "Revenue",
            "description": "Revenue per Unit of Utilization",
            "unit_type": "currency",
        },
        "co2_emissions_per_unit": {
            "text": "Emissions Caused",
            "description": "Caused Emissions",
            "unit_type": "emissions",
        },
    }
    source_parameters = {
        "power_max": {
            "text": "Maximum Output",
            "description": "Maximum Output Flowrate",
            "unit_type": "flowrate",
        },
        "power_min": {
            "text": "Minimum Output",
            "description": "Minimum Output Flowrate",
            "unit_type": "flowrate",
        },
        "determined_power": {
            "text": "Fixed Output",
            "description": "Endogenous given Input Volume",
            "unit_type": "flowrate",
        },
        "availability": {
            "text": "Availability",
            "description": "Ratio of Maximum Output that is available at any time",
            "unit_type": "%",
        },
        "cost": {
            "text": "Cost",
            "description": "Cost per Unit of Utilization",
            "unit_type": "currency",
        },
        "capacity_charge": {
            "text": "Capacity Charge",
            "description": "Fixed price charged per maximum utilized flowrate",
            "unit_type": "capacity_charge",
        },
        "co2_emissions_per_unit": {
            "text": "Emissions Caused",
            "description": "Caused Emissions",
            "unit_type": "emissions",
        },
    }
    storage_parameters = {
        "efficiency": {
            "text": "Base Efficiency",
            "description": "Efficiency at nominal operation point",
            "unit_type": "%",
        },
        "capacity": {
            "text": "Capacity",
            "description": "Storage Capacity",
            "unit_type": "flow",
        },
        "power_max_charge": {
            "text": "Max Charging Power",
            "description": "Max Charging Power",
            "unit_type": "flowrate",
        },
        "power_max_discharge": {
            "text": "Max Discharging Power",
            "description": "Max Discharging Power",
            "unit_type": "flowrate",
        },
        "soc_start": {
            "text": "SOC Start",
            "description": "Initial state of Charge",
            "unit_type": "%",
        },
        "leakage_time": {
            "text": "Absolute Leakage",
            "description": "Absolute Leakage over Time",
            "unit_type": "leakage_time",
        },
        "leakage_soc": {
            "text": "Relative Leakage",
            "description": "Relative Leakage over Time",
            "unit_type": "leakage_soc",
        },
    }
    thermalsystem_parameters = {
        "temperature_ambient": {
            "text": "Ambient Temperature",
            "description": "Temperature Outside of the System",
            "unit_type": "temperature",
        },
        "temperature_max": {
            "text": "Maximum Temperature",
            "description": "Upper Boundary for Valid Internal Temperature",
            "unit_type": "temperature",
        },
        "temperature_min": {
            "text": "Minimum Temperature",
            "description": "Lower Boundary for Valid Internal Temperature",
            "unit_type": "temperature",
        },
        "R": {
            "text": "Thermal Resistance",
            "description": "Energy Loss Factor",
            "unit_type": "float",
        },
        "C": {
            "text": "thermal Capacity",
            "description": "Heat Capacity",
            "unit_type": "float",
        },
    }
    triggerdemand_parameters = {
        "load_profile_energy": {
            "text": "Energy Profile",
            "description": "Energy throughput timeseries",
            "unit_type": "float",
        },
        "load_profile_mass": {
            "text": "Mass Profile",
            "description": "Mass throughput timeseries",
            "unit_type": "float",
        },
        "max_parallel": {
            "text": "Max Parallel Executions",
            "description": "Max number of parallel executions",
            "unit_type": "integer",
        },
    }

    component_parameter_list = {
        "converter": converter_parameters,
        "deadtime": deadtime_parameters,
        "schedule": schedule_parameters,
        "sink": sink_parameters,
        "source": source_parameters,
        "storage": storage_parameters,
        "thermalsystem": thermalsystem_parameters,
        "triggerdemand": triggerdemand_parameters,
    }

    return component_parameter_list