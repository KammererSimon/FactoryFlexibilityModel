# CONNECTION
# This script contains the connection class, which specifies a connection between two components

# IMPORT ENDOGENOUS COMPONENTS
import factory_flexibility_model.input_validations as iv


class connection:
    def __init__(
        self,
        source,
        sink,
        connection_id,
        *,
        to_losses=None,
        from_gains=None,
        flowtype=None,
        name=None,
        weight=None,
        weight_source=None,
        weight_sink=None,
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
            # If just one "weight" is specified: use it for validate and output
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
                raise Exception(
                    f"incompatible flowtypes between connection {self.name} and component {source.name}: {self.flowtype.name} vs {source.flowtype.name}"
                )

            # check if it is compatible with the flowtype of the sink
            if not (sink.flowtype.is_unknown()) and not (
                sink.flowtype.is_losses()
                or sink.flowtype == self.flowtype
                or self.flowtype.is_unknown()
            ):
                raise Exception(
                    f"incompatible flowtypes between connection {self.name} and component {sink.name}: {self.flowtype.name} vs {sink.flowtype.name}"
                )

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
                raise Exception(
                    f"Flowtypes of origin and destination do not match: {source.flowtype.name} vs {sink.flowtype.name}"
                )

    def update_flowtype(self, flowtype):
        """This function takes a name of a flowtype. If the flowtype of the connection is not yet defined it will be set to the given flowtype.
        In this case the update-cascade will be continued at the other sides component of the connection.
        If the flowtype of the connection is already assigned, it is checked, whether the given flowtype matches with the defined flowtype.
        An Error is thrown if the flows are incompatible."""

        # do nothing if the flowtype already matches
        if self.flowtype == flowtype:
            return

        # ...otherwise set the flowtype of the connection
        self.flowtype = flowtype

        # check, if the flowtype of the source component is already known
        if self.source.flowtype.is_unknown():
            # if no: update it as well
            self.source.update_flow(flowtype)

        # if yes: is it compatible with the flowtype that has just been set for the connection?
        elif not self.source.flowtype == flowtype:
            # throw error if the flows are not the same
            raise Exception(
                f"Error while assigning flowtype types: interface between {self.source.name} and {self.sink.name} does not match"
            )

        # do the same for the sink side: Check, if the flowtype of the sink component is already known
        if self.sink.flowtype.is_unknown():
            # if no: update it as well
            self.sink.update_flow(flowtype)

        # if yes: is it compatible with the flowtype that has just been set for the connection?
        elif not self.sink.flowtype == flowtype:
            # throw error if the flows are not the same
            raise Exception(
                f"Error while assigning flowtype types: interface between {self.source.name} and {self.sink.name} does not match"
            )

        # everything succesful? -> Write log_simulation
        if self.source.factory.log_simulation:
            print(
                f"            (UPDATE) The flowtype of connection {self.name} is now defined as {flowtype.name}"
            )
