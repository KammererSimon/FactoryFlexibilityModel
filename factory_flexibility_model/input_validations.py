### INPUT VALIDATIONS
# Contained functions:
# - validate() -> Validates a single user validate and returns it as a guaranteed compatible value
# - check_version_compatibility -> Compares the versions of two scripts and warns when incompatibilities might occur

# TODO: Refactor this to get rid of the excessive if/elif-nesting!

import logging

import numpy as np

# IMPORT 3RD PARTY PACKAGES
import pandas as pd


# CODE START
def validate(input, type, *, min=None, max=None, positive=False, timesteps=1):
    """This function represents the FORMAL validate validation takes any validate and transforms it into the desired format
    or throws an error, if the datatypes are not compatible.
    :param input: [int, float, string, boolean, np-array, list, pandas-series] User given Input data
    :param type: [String] {"str", "string", "int", "integer", "float", "bool", "boolean", "%", "0..1"}
    :param min: [Float] Optional Lower boundary for numeric values
    :param max: [Float] Optional upper boundary for numeric values
    :param timesteps: [Int] Optional number of timesteps required for timeseries data
    :param positive: [Boolean] Optional constraint to positive numerical values
    :return: User data in the specfied format"""

    logging.basicConfig(level=logging.WARNING)

    # handle config and prepare the limits for numeric inputs
    if max is not None:
        upperlimit = True
    else:
        upperlimit = False

    if min is not None:
        lowerlimit = True
    else:
        lowerlimit = False

    if positive:
        if not lowerlimit or min < 0:
            min = 0
            lowerlimit = True

    # Determine, if a timeseries is requested
    if timesteps > 1:
        timeseries = True
    else:
        timeseries = False

    # Handle strings
    if type == "str" or type == "string":
        if timeseries:
            logging.critical(f"Creating a string - timeseries is not possible!")
            raise Exception
        if isinstance(input, str):
            return input
        else:
            print(input)
            logging.critical(
                f"Given value is {type(input)}, not a string as requested!"
            )
            raise Exception

    # Handle booleans
    if type == "boolean" or type == "bool":
        if isinstance(input, bool):
            if timeseries:
                logging.critical(
                    f"handling of boolean arrays as validate is not implemented yet"
                )
                raise Exception
                # TODO: implement boolean array generation
            else:
                return input
        elif isinstance(input, str):
            if input == "TRUE" or input == "true" or input == "True":
                return True
            if input == "FALSE" or input == "false" or input == "False":
                return False
            else:
                logging.critical(
                    f"The given value string '{input}' cannot be identified as 'True' or 'False'!"
                )
                raise Exception
        else:
            logging.critical(
                f"Given value is of type {type(input)} and incompatible with requested type (boolean)!"
            )
            raise Exception

    # Handle ratios
    if type == "0..1" or type == "%":
        if timeseries:
            if isinstance(input, float) or isinstance(input, int):
                if input > 1:
                    logging.critical(f"ERROR: given value {input} is greater than 1")
                    raise Exception
                if input < 0:
                    logging.critical(f"ERROR: given value {input} is below 0")
                    raise Exception
                return np.ones(timesteps) * input

            elif isinstance(input, list):
                if len(input) >= timesteps:
                    data = np.array(input[0:timesteps])
                    if data.max() > 1:
                        logging.critical(f"ERROR: given value {input} is above 1")
                        raise Exception
                    if data.min() < 0:
                        logging.critical(f"ERROR: given value {input} is below 0")
                        raise Exception
                    return data
                else:
                    logging.critical(
                        f"the given timeseries does not have enough timesteps! Minimum requirement is {timesteps} values"
                    )
                    raise Exception

                # is validate data type a numpy array?
            elif isinstance(input, np.ndarray):
                if len(input) >= timesteps:
                    data = input[0:timesteps]
                    if data.max() > 1:
                        logging.critical(f"ERROR: given value {input} is above 1")
                        raise Exception
                    if data.min() < 0:
                        logging.critical(f"ERROR: given value {input} is below 0")
                        raise Exception
                    return data
                else:
                    logging.critical(
                        f"the given timeseries does not have enough timesteps! Minimum requirement is {timesteps} values"
                    )
                    raise Exception

                # is validate data type a pandas array?
            elif isinstance(input, pd.core.series.Series):
                data = input.astype("float64").to_numpy()
                if len(input) >= timesteps:
                    data = data[0:timesteps]
                    if data.max() > 1:
                        logging.critical(f"ERROR: given value {input} is above 1")
                        raise Exception
                    if data.min() < 0:
                        logging.critical(f"ERROR: given value {input} is below 0")
                        raise Exception
                    return data
                else:
                    logging.critical(
                        f"the given timeseries does not have enough timesteps! Minimum requirement is {timesteps} values"
                    )
                    raise Exception
            else:
                logging.critical(
                    f"data type {type(input)} is invalid as validate for a timeseries!"
                )
                raise Exception
            # TODO: implement ratio array generation
        else:
            if isinstance(input, int):
                if input == 0 or input == 1:
                    return input
                else:
                    logging.critical(f"Given value is not a value between 0 and 1")
                    raise Exception

            elif isinstance(input, float):
                if 0 <= input <= 1:
                    return input
                else:
                    logging.critical(f"Given value is not a value between 0 and 1")
                    raise Exception

            elif isinstance(input, bool):
                if input:
                    return 1
                else:
                    logging.info(
                        "Given value was a boolean and not a value between 0 and 1. It has been translated to True=1, False=0"
                    )
                    return 0

            else:
                logging.critical(
                    f"Given value is of type {type(input)} and not a value between 0 and 1"
                )
                raise Exception

    # INTEGERS
    if type == "int" or type == "integer":
        # INT, TIMESERIES
        if timeseries:
            if isinstance(input, float) or isinstance(input, int):
                if upperlimit and input > max:
                    logging.critical(
                        f"ERROR: given value {input} is above the given upper limit ({max})"
                    )
                    raise Exception
                if lowerlimit and input < min:
                    logging.critical(
                        f"ERROR: given value {input} is below the given lower limit ({min})"
                    )
                    raise Exception
                return np.ones(timesteps) * input

            elif isinstance(input, list):
                if len(input) >= timesteps:
                    data = np.array(input[0:timesteps])
                    if upperlimit and data.max() > max:
                        logging.critical(
                            f"ERROR: given value {input} is above the given upper limit ({max})"
                        )
                        raise Exception
                    if lowerlimit and data.min() < min:
                        logging.critical(
                            f"ERROR: given value {input} is below the given lower limit ({min})"
                        )
                        raise Exception
                    return round(data)
                else:
                    logging.critical(
                        f"the given timeseries does not have enough timesteps! Minimum requirement is {timesteps} values"
                    )
                    raise Exception

                # is validate data type a numpy array?
            elif isinstance(input, np.ndarray):
                if len(input) >= timesteps:
                    data = input[0:timesteps]
                    if upperlimit and data.max() > max:
                        logging.critical(
                            f"ERROR: given value {input} is above the given upper limit ({max})"
                        )
                        raise Exception
                    if lowerlimit and data.min() < min:
                        logging.critical(
                            f"ERROR: given value {input} is below the given lower limit ({min})"
                        )
                        raise Exception
                    return round(data)
                else:
                    logging.critical(
                        f"the given timeseries does not have enough timesteps! Minimum requirement is {timesteps} values"
                    )
                    raise Exception

                # is validate data type a pandas array?
            elif isinstance(input, pd.core.series.Series):
                data = input.astype("float64").to_numpy()
                if len(input) >= timesteps:
                    data = data[0:timesteps]
                    if upperlimit and data.max() > max:
                        logging.critical(
                            f"ERROR: given value {input} is above the given upper limit ({max})"
                        )
                        raise Exception
                    if lowerlimit and data.min() < min:
                        logging.critical(
                            f"ERROR: given value {input} is below the given lower limit ({min})"
                        )
                        raise Exception
                    return round(data)
                else:
                    logging.critical(
                        f"the given timeseries does not have enough timesteps! Minimum requirement is {timesteps} values"
                    )
                    raise Exception
            else:
                logging.critical(
                    f"data type {type(input)} is invalid as validate for a timeseries!"
                )
                raise Exception
        # INT, NO TIMESERIES
        else:
            if isinstance(input, int):
                return input
            elif isinstance(input, float):
                logging.info(
                    "Given value was a float and has been rounded to next int!"
                )
                return round(input)
            else:
                logging.critical(
                    f"Given value is of type {type(input)} and incompatible with requested type (int)!"
                )
                raise Exception

            # TODO: Check, what happened here ;)
            if upperlimit and max(data) > max:
                logging.critical(
                    f"ERROR: given value {data} is above the given upper limit ({max})"
                )
                raise Exception
            if lowerlimit and min(data) < min:
                logging.critical(
                    f"ERROR: given value {data} is below the given lower limit ({min})"
                )
                raise Exception

    if type == "float":
        if not isinstance(input, float):
            if input == "" or input is None:
                return None
            try:
                input = float(input)
                logging.info("Given value has been converted to float")
            except:
                logging.critical(
                    f"Given value of type {type(input)} and incompatible with requested type (float)!"
                )
                raise Exception

        if timeseries:
            if isinstance(input, float) or isinstance(input, int):
                if upperlimit and input > max:
                    logging.critical(
                        f"ERROR: given value {input} is above the given upper limit ({max})"
                    )
                    raise Exception
                if lowerlimit and input < min:
                    logging.critical(
                        f"ERROR: given value {input} is below the given lower limit ({min})"
                    )
                    raise Exception
                return np.ones(timesteps) * input

            elif isinstance(input, list):
                if len(input) >= timesteps:
                    data = np.array(input[0:timesteps])
                    if upperlimit and max(data) > max:
                        logging.critical(
                            f"ERROR: given value {input} is above the given upper limit ({max})"
                        )
                        raise Exception
                    if lowerlimit and min(data) < min:
                        logging.critical(
                            f"ERROR: given value {input} is below the given lower limit ({min})"
                        )
                        raise Exception
                    return data
                else:
                    logging.critical(
                        f"the given timeseries does not have enough timesteps! Minimum requirement is {timesteps} values"
                    )
                    raise Exception

                # is validate data type a numpy array?
            elif isinstance(input, np.ndarray):
                if len(input) >= timesteps:
                    data = input[0:timesteps]
                    if upperlimit and max(data) > max:
                        logging.critical(
                            f"ERROR: given value {input} is above the given upper limit ({max})"
                        )
                        raise Exception
                    if lowerlimit and min(data) < min:
                        logging.critical(
                            f"ERROR: given value {input} is below the given lower limit ({min})"
                        )
                        raise Exception
                    return data
                else:
                    logging.critical(
                        f"the given timeseries does not have enough timesteps! Minimum requirement is {timesteps} values"
                    )
                    raise Exception

                # is validate data type a pandas array?
            elif isinstance(input, pd.core.series.Series):
                data = input.astype("float64").to_numpy()
                if len(input) >= timesteps:
                    data = data[0:timesteps]
                    if upperlimit and max(data) > max:
                        logging.critical(
                            f"ERROR: given value {input} is above the given upper limit ({max})"
                        )
                        raise Exception
                    if lowerlimit and min(data) < min:
                        logging.critical(
                            f"ERROR: given value {input} is below the given lower limit ({min})"
                        )
                        raise Exception
                    return data
                else:
                    logging.critical(
                        f"the given timeseries does not have enough timesteps! Minimum requirement is {timesteps} values"
                    )
                    raise Exception
            else:
                logging.critical(
                    f"data type ({input}) is invalid as validate for a timeseries!"
                )
                raise Exception

        else:
            if positive and input < 0:
                logging.critical(
                    "The given value is negative but a positive float is requested! "
                )
                raise Exception
            return input

    if type == "timeseries":
        logging.critical("This function call is no longer supported")
        raise Exception
