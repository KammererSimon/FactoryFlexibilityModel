# -----------------------------------------------------------------------------
# This script is used to read in factory layouts and specifications from Excel files and to generate
# factory-objects out of them that can be used for the simulations
#
# Project Name: Factory_Flexibility_Model
# File Name: set_logger.py
#
# Copyright (c) [2024]
# [Institute of Energy Systems, Energy Efficiency and Energy Economics
#  TU Dortmund
#  Simon Kammerer (simon.kammerer@tu-dortmund.de)]
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----------------------------------------------------------------------------

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
