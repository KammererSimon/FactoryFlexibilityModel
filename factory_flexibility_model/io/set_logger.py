# IMPORTS
import logging


# FUNCTIONS
def set_logging_level(logging_level: str = "warning"):
    """
    This is a helper function, that configures the python internal logger to report only messages of a certain urgance, which can be specified by the user via logging_level.
    The detail of logging can be adjusted in the five thresholds "debug", "info", "warning", "error" and "critical".

    If the keyword "true" is provided, the level gets set so "info".
    If no input is provided, the level gets set to "warning".
    If the keyword "false" is provided, the level gets set so "error".

    Details on the logging package can be found here: https://docs.python.org/3/howto/logging.html

    :param logging_level: [str] ["debug", "info", "warning", "error", "critical", "true", "false"]
    :return: None -> Function just changes the configuration of the active logger
    """

    # get the reference to the logger
    logger = logging.getLogger()

    if type(logging_level) is bool:
        if logging_level:
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.ERROR)
    else:
        if logging_level.lower() == "debug":
            logger.setLevel(logging.DEBUG)
        elif logging_level.lower() in ["info", "true"]:
            logger.setLevel(logging.INFO)
        elif logging_level.lower() == "warning":
            logger.setLevel(logging.WARNING)
        elif logging_level.lower() in ["error", "false"]:
            logger.setLevel(logging.ERROR)
        elif logging_level.lower() == "critical":
            logger.setLevel(logging.CRITICAL)
