# CONNECTION
# This script contains the connection class, which specifies a connection between two components

# -----------------------------------------------------------------------------
# This script is used to read in factory layouts and specifications from Excel files and to generate
# factory-objects out of them that can be used for the simulations
#
# Project Name: Factory_Flexibility_Model
# File Name: Connection.py
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

import logging

# IMPORT ENDOGENOUS COMPONENTS
import factory_flexibility_model.io.input_validations as iv


class Connection:
    def __init__(
        self,
        origin,
        destination,
        key: str,
        *,
        flowtype: str = None,
        name: str = None,
        type: str = "default",
        weight: float = None,
    ):

        # define attributes
        self.key = (
            key  # give the connection a unique id in the list of existing connections
        )
        self.origin = origin
        self.type = (
            type  # set type of connection {"default", "losses", "gains", "slack"}
        )
        self.destination = destination

        # set a name for the connection
        if name is not None:
            # If name is specified use the string that has been handed over
            self.name = iv.validate(name, "str")
        else:
            # otherwise generate generic name
            self.name = f"{origin.name} -> {destination.name}"

        # check, if weights have been specified
        if weight is not None:
            # If just one "weight" is specified: use it for input and output
            self.weight = iv.validate(weight, "float")
        else:
            self.weight = 1

        # if a flowtype is specified: adapt it and check for compatibility
        if flowtype is not None:

            # set the flowtype of the connection as specified
            self.flowtype = flowtype

            # check, if it is compatible with the flowtype ot the origin
            if (
                not (origin.flowtype.is_unknown())
                and not (destination.flowtype.is_losses())
                and not (
                    origin.flowtype.key == self.flowtype.key
                    or self.flowtype.is_unknown()
                )
            ):
                logging.critical(
                    f"incompatible flowtypes between connection {self.name} and Component {origin.name}: {self.flowtype.name} vs {origin.flowtype.name}"
                )
                raise Exception

            # check if it is compatible with the flowtype of the destination
            if not (destination.flowtype.is_unknown()) and not (
                destination.flowtype.is_losses()
                or destination.flowtype.key == self.flowtype.key
                or self.flowtype.is_unknown()
            ):
                logging.critical(
                    f"incompatible flowtypes between connection {self.name} and Component {destination.name}: {self.flowtype.name} vs {destination.flowtype.name}"
                )
                raise Exception

        # if no flowtype is handed over: check, if it can be derived from destination or origin
        else:
            # can the flowtype be derived from the destination without causing incompatibilities?
            if (
                origin.flowtype.is_unknown() and not destination.flowtype.is_unknown()
            ) or destination.flowtype == origin.flowtype:
                # if yes: set the flowtype as the flowtype of the destination
                self.flowtype = destination.flowtype

            # if no: can the flowtype be derived from the origin without causing incompatibilities?
            elif destination.flowtype.is_unknown() or destination.flowtype.is_losses():
                # set the flowtype as the flowtype of the origin
                self.flowtype = origin.flowtype

            else:
                # if nothing of the above is the case the flows of origin and destination must be incompatible -> throw an error
                logging.critical(
                    f"Flowtypes of origin and destination do not match: {origin.flowtype.name} vs {destination.flowtype.name}"
                )
                raise Exception

    def update_flowtype(self, flowtype):
        """This function takes a name of a flowtype. If the flowtype of the connection is not yet defined it will be set to the given flowtype.
        In this case the update-cascade will be continued at the other sides Component of the connection.
        If the flowtype of the connection is already assigned, it is checked, whether the given flowtype matches with the defined flowtype.
        An Error is thrown if the flows are incompatible."""

        # do nothing if the flowtype already matches
        if self.flowtype == flowtype:
            return

        # ...otherwise set the flowtype of the connection
        self.flowtype = flowtype

        # check, if the flowtype of the origin Component is already known
        if self.origin.flowtype.is_unknown():
            # if no: update it as well
            self.origin.update_flowtype(flowtype)

        # if yes: is it compatible with the flowtype that has just been set for the connection?
        elif not self.origin.flowtype == flowtype:
            # throw error if the flows are not the same
            logging.critical(
                f"Error while assigning flowtype types: interface between {self.origin.name} and {self.destination.name} does not match"
            )
            raise Exception

        # do the same for the destination side: Check, if the flowtype of the destination Component is already known
        if self.destination.flowtype.is_unknown():
            # if no: update it as well
            self.destination.update_flowtype(flowtype)

        # if yes: is it compatible with the flowtype that has just been set for the connection?
        elif not self.destination.flowtype == flowtype:
            # throw error if the flows are not the same
            logging.critical(
                f"Error while assigning flowtype types: interface between {self.origin.name} and {self.destination.name} does not match"
            )
            raise Exception

        logging.debug(
            f"            (UPDATE) The flowtype of connection {self.name} is now defined as {flowtype.name}"
        )
