# CONNECTION
# This script contains the connection class, which specifies a connection between two components

import logging

# IMPORT ENDOGENOUS COMPONENTS
import factory_flexibility_model.input_validations as iv


class Connection:
    def __init__(
        self,
        source,
        sink,
        connection_id: str,
        *,
        to_losses: bool = None,
        from_gains: bool = None,
        flowtype: str = None,
        name: str = None,
        weight: float = None,
        weight_source: float = None,
        weight_sink: float = None,
    ):

        # define attributes
        self.connection_id = connection_id  # give the connection a unique id in the list of existing connections
        self.source = source
        self.sink = sink
        self.weight_sink = 1
        self.weight_source = 1

        # check if the connection is meant to deduct losses
        if to_losses is not None:
            self.to_losses = to_losses
        else:
            self.to_losses = False

        # check if the connection is meant to deduct losses
        if from_gains is not None:
            self.from_gains = from_gains
        else:
            self.from_gains = False

        # set a name for the connection
        if name is not None:
            # If name is specified use the string that has been handed over
            self.name = iv.validate(name, "str")
        else:
            # otherwise generate generic name
            self.name = f"{source.name}_to_{sink.name}"

        # check, if weights have been specified
        if weight is not None:
            # If just one "weight" is specified: use it for input and output
            self.weight_sink = iv.validate(weight, "float")
            self.weight_source = iv.validate(weight, "float")

        # check if weight for sink is specified
        if weight_sink is not None:
            self.weight_sink = iv.validate(weight_sink, "float")

            # check if weight for source is specified
        if weight_source is not None:
            self.weight_source = iv.validate(weight_source, "float")

        # if a flowtype is specified: adapt it and check for compatibility
        if flowtype is not None:

            # set the flowtype of the connection as specified
            self.flowtype = flowtype

            # check, if it is compatible with the flowtype ot the source
            if (
                not (source.flowtype.is_unknown())
                and not (sink.flowtype.is_losses())
                and not (source.flowtype == self.flowtype or self.flowtype.is_unknown())
            ):
                logging.critical(
                    f"incompatible flowtypes between connection {self.name} and Component {source.name}: {self.flowtype.name} vs {source.flowtype.name}"
                )
                raise Exception

            # check if it is compatible with the flowtype of the sink
            if not (sink.flowtype.is_unknown()) and not (
                sink.flowtype.is_losses()
                or sink.flowtype == self.flowtype
                or self.flowtype.is_unknown()
            ):
                logging.critical(
                    f"incompatible flowtypes between connection {self.name} and Component {sink.name}: {self.flowtype.name} vs {sink.flowtype.name}"
                )
                raise Exception

        # if no flowtype is handed over: check, if it can be derived from sink or source
        else:
            # can the flowtype be derived from the sink without causing incompatibilities?
            if (
                source.flowtype.is_unknown() and not sink.flowtype.is_unknown()
            ) or sink.flowtype == source.flowtype:
                # if yes: set the flowtype as the flowtype of the sink
                self.flowtype = sink.flowtype

            # if no: can the flowtype be derived from the source without causing incompatibilities?
            elif sink.flowtype.is_unknown() or sink.flowtype.is_losses():
                # set the flowtype as the flowtype of the source
                self.flowtype = source.flowtype

            else:
                # if nothing of the above is the case the flows of source and sink must be incompatible -> throw an error
                logging.critical(
                    f"Flowtypes of origin and destination do not match: {source.flowtype.name} vs {sink.flowtype.name}"
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

        # check, if the flowtype of the source Component is already known
        if self.source.flowtype.is_unknown():
            # if no: update it as well
            self.source.update_flow(flowtype)

        # if yes: is it compatible with the flowtype that has just been set for the connection?
        elif not self.source.flowtype == flowtype:
            # throw error if the flows are not the same
            logging.critical(
                f"Error while assigning flowtype types: interface between {self.source.name} and {self.sink.name} does not match"
            )
            raise Exception

        # do the same for the sink side: Check, if the flowtype of the sink Component is already known
        if self.sink.flowtype.is_unknown():
            # if no: update it as well
            self.sink.update_flow(flowtype)

        # if yes: is it compatible with the flowtype that has just been set for the connection?
        elif not self.sink.flowtype == flowtype:
            # throw error if the flows are not the same
            logging.critical(
                f"Error while assigning flowtype types: interface between {self.source.name} and {self.sink.name} does not match"
            )
            raise Exception

        logging.debug(
            f"            (UPDATE) The flowtype of connection {self.name} is now defined as {flowtype.name}"
        )
