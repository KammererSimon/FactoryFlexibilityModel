### INPUT VALIDATIONS
# Contained functions:
# - input() -> Validates a single user input and returns it as a guaranteed compatible value
# - check_version_compatibility -> Compares the versions of two scripts and warns when incompatibilities might occur

# TODO: Refactor this to get rid of the excessive if/elif-nesting!

import warnings

import numpy as np

# IMPORT 3RD PARTY PACKAGES
import pandas as pd


# CODE START
def input(input, type, **kwargs):
    """This function represents the FORMAL input validation takes any input and transforms it into the desired format
    or throws an error, if the datatypes are not compatible.

    :param input: User given Input data, valid types = {int, float, string, boolean, np-array, list, pandas-series}
    :param type: {"str", "string", "int", "integer", "float", "bool", "boolean", "%", "0..1"}
    :param kwargs: {min, max, timesteps, positive}
    :return: User data in the specfied format"""

    # handle kwargs and prepare the limits for numeric inputs
    if "max" in kwargs:
        max = kwargs["max"]
        upperlimit = True
    else:
        max = 1  # dummy value, doesn't do anything
        upperlimit = False

    if "min" in kwargs:
        min = kwargs["min"]
        lowerlimit = True
    else:
        min = 0  # dummy value, doesn't do anything
        lowerlimit = False

    if "positive" in kwargs:
        if lowerlimit:
            if min < 0:
                warnings.warn(
                    "Warning: 'Positive'-constraint overrides lower variable limit!"
                )
        min = 0
        lowerlimit = True

    # Determine, if a timeseries is requested
    timeseries = False
    if "timesteps" in kwargs:
        if kwargs["timesteps"] > 1:
            timeseries = True
            timesteps = kwargs["timesteps"]

    # Handle strings
    if type == "str" or type == "string":
        if timeseries:
            raise Exception(f"Creating a string - timeseries is not possible!")
        if isinstance(input, str):
            return input
        else:
            raise Exception(f"Given input is {type(input)}, not a string as requested!")

    # Handle booleans
    if type == "boolean" or type == "bool":
        if isinstance(input, bool):
            if timeseries:
                raise Exception(
                    f"handling of boolean arrays as input is not implemented yet"
                )
                # TODO: implement boolean array generation
            else:
                return input
        elif isinstance(input, str):
            if input == "TRUE" or input == "true" or input == "True":
                return True
            if input == "FALSE" or input == "false" or input == "False":
                return False
            else:
                raise Exception(
                    f"The given input string '{input}' cannot be identified as 'True' or 'False'!"
                )
        else:
            raise Exception(
                f"Given input is of type {type(input)} and incompatible with requested type (boolean)!"
            )

    # Handle ratios
    if type == "0..1" or type == "%":
        if timeseries:
            if isinstance(input, float) or isinstance(input, int):
                if input > 1:
                    raise Exception(f"ERROR: given value {input} is greater than 1")
                if input < 0:
                    raise Exception(f"ERROR: given value {input} is below 0")
                return np.ones(timesteps) * input

            elif isinstance(input, list):
                if len(input) >= timesteps:
                    data = np.array(input[0:timesteps])
                    if data.max() > 1:
                        raise Exception(f"ERROR: given value {input} is above 1")
                    if data.min() < 0:
                        raise Exception(f"ERROR: given value {input} is below 0")
                    return data
                else:
                    raise Exception(
                        f"the given timeseries does not have enough timesteps! Minimum requirement is {timesteps} values"
                    )

                # is input data type a numpy array?
            elif isinstance(input, np.ndarray):
                if len(input) >= timesteps:
                    data = input[0:timesteps]
                    if data.max() > 1:
                        raise Exception(f"ERROR: given value {input} is above 1")
                    if data.min() < 0:
                        raise Exception(f"ERROR: given value {input} is below 0")
                    return data
                else:
                    raise Exception(
                        f"the given timeseries does not have enough timesteps! Minimum requirement is {timesteps} values"
                    )

                # is input data type a pandas array?
            elif isinstance(input, pd.core.series.Series):
                data = input.astype("float64").to_numpy()
                if len(input) >= timesteps:
                    data = data[0:timesteps]
                    if data.max() > 1:
                        raise Exception(f"ERROR: given value {input} is above 1")
                    if data.min() < 0:
                        raise Exception(f"ERROR: given value {input} is below 0")
                    return data
                else:
                    raise Exception(
                        f"the given timeseries does not have enough timesteps! Minimum requirement is {timesteps} values"
                    )
            else:
                raise Exception(
                    f"data type {type(input)} is invalid as input for a timeseries!"
                )
            # TODO: implement ratio array generation
        else:
            if isinstance(input, int):
                if input == 0 or input == 1:
                    return input
                else:
                    raise Exception(f"Given input is not a value between 0 and 1")

            elif isinstance(input, float):
                if 0 <= input <= 1:
                    return input
                else:
                    raise Exception(f"Given input is not a value between 0 and 1")

            elif isinstance(input, bool):
                if input:
                    return 1
                else:
                    warnings.warn(
                        "Given input was a boolean and not a value between 0 and 1. It has been translated to True=1, False=0"
                    )
                    return 0

            else:
                raise Exception(
                    f"Given input is of type {type(input)} and not a value between 0 and 1"
                )

    # INTEGERS
    if type == "int" or type == "integer":
        # INT, TIMESERIES
        if timeseries:
            if isinstance(input, float) or isinstance(input, int):
                if upperlimit and input > max:
                    raise Exception(
                        f"ERROR: given value {input} is above the given upper limit ({max})"
                    )
                if lowerlimit and input < min:
                    raise Exception(
                        f"ERROR: given value {input} is below the given lower limit ({min})"
                    )
                return np.ones(timesteps) * input

            elif isinstance(input, list):
                if len(input) >= timesteps:
                    data = np.array(input[0:timesteps])
                    if upperlimit and data.max() > max:
                        raise Exception(
                            f"ERROR: given value {input} is above the given upper limit ({max})"
                        )
                    if lowerlimit and data.min() < min:
                        raise Exception(
                            f"ERROR: given value {input} is below the given lower limit ({min})"
                        )
                    return round(data)
                else:
                    raise Exception(
                        f"the given timeseries does not have enough timesteps! Minimum requirement is {timesteps} values"
                    )

                # is input data type a numpy array?
            elif isinstance(input, np.ndarray):
                if len(input) >= timesteps:
                    data = input[0:timesteps]
                    if upperlimit and data.max() > max:
                        raise Exception(
                            f"ERROR: given value {input} is above the given upper limit ({max})"
                        )
                    if lowerlimit and data.min() < min:
                        raise Exception(
                            f"ERROR: given value {input} is below the given lower limit ({min})"
                        )
                    return round(data)
                else:
                    raise Exception(
                        f"the given timeseries does not have enough timesteps! Minimum requirement is {timesteps} values"
                    )

                # is input data type a pandas array?
            elif isinstance(input, pd.core.series.Series):
                data = input.astype("float64").to_numpy()
                if len(input) >= timesteps:
                    data = data[0:timesteps]
                    if upperlimit and data.max() > max:
                        raise Exception(
                            f"ERROR: given value {input} is above the given upper limit ({max})"
                        )
                    if lowerlimit and data.min() < min:
                        raise Exception(
                            f"ERROR: given value {input} is below the given lower limit ({min})"
                        )
                    return round(data)
                else:
                    raise Exception(
                        f"the given timeseries does not have enough timesteps! Minimum requirement is {timesteps} values"
                    )
            else:
                raise Exception(
                    f"data type {type(input)} is invalid as input for a timeseries!"
                )
        # INT, NO TIMESERIES
        else:
            if isinstance(input, int):
                return input
            elif isinstance(input, float):
                warnings.warn(
                    "Given input was a float and has been rounded to next int!"
                )
                return round(input)
            else:
                raise Exception(
                    f"Given input is of type {type(input)} and incompatible with requested type (int)!"
                )

            # TODO: Check, what happened here ;)
            if upperlimit and max(data) > max:
                raise Exception(
                    f"ERROR: given value {data} is above the given upper limit ({max})"
                )
            if lowerlimit and min(data) < min:
                raise Exception(
                    f"ERROR: given value {data} is below the given lower limit ({min})"
                )

    if type == "float":
        if timeseries:
            if isinstance(input, float) or isinstance(input, int):
                if upperlimit and input > max:
                    raise Exception(
                        f"ERROR: given value {input} is above the given upper limit ({max})"
                    )
                if lowerlimit and input < min:
                    raise Exception(
                        f"ERROR: given value {input} is below the given lower limit ({min})"
                    )
                return np.ones(timesteps) * input

            elif isinstance(input, list):
                if len(input) >= timesteps:
                    data = np.array(input[0:timesteps])
                    if upperlimit and max(data) > max:
                        raise Exception(
                            f"ERROR: given value {input} is above the given upper limit ({max})"
                        )
                    if lowerlimit and min(data) < min:
                        raise Exception(
                            f"ERROR: given value {input} is below the given lower limit ({min})"
                        )
                    return data
                else:
                    raise Exception(
                        f"the given timeseries does not have enough timesteps! Minimum requirement is {timesteps} values"
                    )

                # is input data type a numpy array?
            elif isinstance(input, np.ndarray):
                if len(input) >= timesteps:
                    data = input[0:timesteps]
                    if upperlimit and max(data) > max:
                        raise Exception(
                            f"ERROR: given value {input} is above the given upper limit ({max})"
                        )
                    if lowerlimit and min(data) < min:
                        raise Exception(
                            f"ERROR: given value {input} is below the given lower limit ({min})"
                        )
                    return data
                else:
                    raise Exception(
                        f"the given timeseries does not have enough timesteps! Minimum requirement is {timesteps} values"
                    )

                # is input data type a pandas array?
            elif isinstance(input, pd.core.series.Series):
                data = input.astype("float64").to_numpy()
                if len(input) >= timesteps:
                    data = data[0:timesteps]
                    if upperlimit and max(data) > max:
                        raise Exception(
                            f"ERROR: given value {input} is above the given upper limit ({max})"
                        )
                    if lowerlimit and min(data) < min:
                        raise Exception(
                            f"ERROR: given value {input} is below the given lower limit ({min})"
                        )
                    return data
                else:
                    raise Exception(
                        f"the given timeseries does not have enough timesteps! Minimum requirement is {timesteps} values"
                    )
            else:
                raise Exception(
                    f"data type {type(input)} is invalid as input for a timeseries!"
                )
        else:
            if not isinstance(input, float):
                if input == "" or input == None:
                    return input
                try:
                    input = float(input)
                    warnings.warn("Given input has been converted to float")
                except:
                    raise Exception(
                        f"Given input is of type {type(input)} and incompatible with requested type (float)!"
                    )

            if "positive" in kwargs:
                if kwargs["positive"]:
                    if input < 0:
                        raise Exception(
                            "The given value is negative but a positive float is requested! "
                        )
            return input

    if type == "timeseries":
        raise Exception("This function call is no longer supported")


def check_version_compatibility(
    name_one, version_number_one, name_two, version_number_two
):
    """This script takes two version numbers and throws a descriptive warning if they are not compatible

    :param name_one: Name of the program component that belongs to the first given version number
    :param version_number_one: version number of the first program component
    :param name_two: Name of the program component that belongs to the second given version number
    :param version_number_two: Version number of the second program component
    :return: True/False
    """
    # CHECK VERSION COMPATIBILITY
    if version_number_one > version_number_two:
        warnings.warn(
            f"The version of used {name_two} is older than the version of used {name_one}! ({version_number_two} vs {version_number_one}) Compatibility cannot be guaranteed!"
        )
        return False
    elif version_number_two < version_number_one:
        warnings.warn(
            f"The version of used {name_one} is older than the version of used {name_two}! ({version_number_one} vs {version_number_two}) Compatibility cannot be guaranteed!"
        )
        return False
    return True
