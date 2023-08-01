# CONNECTION
# This script contains the connection class, which specifies a connection between two components

# IMPORT ENDOGENOUS COMPONENTS
import factory_flexibility_model.input_validations as iv


class connection:
    def __init__(self, source, sink, connection_id, **kwargs):

        # define attributes
        self.connection_id = connection_id  # give the connection a unique id in the list of existing connections
        self.source = source
        self.sink = sink
        self.weight_sink = 1
        self.weight_source = 1

        # set a name for the connection
        if "name" in kwargs:
            self.name = iv.input(
                kwargs["name"], "str"
            )  # If name is specified use the string that has been handed over
        else:
            self.name = (
                f"{source.name}_to_{sink.name}"  # otherwise generate generic name
            )

        # check, if weights have been specified in kwargs
        if "weight" in kwargs:
            # If just one "weight" is specified: use it for input and output
            self.weight_sink = iv.input(kwargs["weight"], "float")
            self.weight_source = iv.input(kwargs["weight"], "float")

        # check if weight for sink is specified
        if "weight_sink" in kwargs:
            self.weight_sink = iv.input(kwargs["weight_sink"], "float")

            # check if weight for source is specified
        if "weight_source" in kwargs:
            self.weight_source = iv.input(kwargs["weight_source"], "float")

        # if a flow is specified: adapt it and check for compatibility
        if "flow" in kwargs:

            # set the flow of the connection as specified
            self.flow = kwargs["flow"]

            # check, if it is compatible with the flowtype ot the source
            if (
                not (source.flow.is_unknown())
                and not (sink.flow.is_losses())
                and not (source.flow == self.flow or self.flow.is_unknown())
            ):
                raise Exception(
                    f"incompatible flowtypes between connection {self.name} and component {source.name}: {self.flow.name} vs {source.flow.name}"
                )

            # check if it is compatible with the flowtype of the sink
            if not (sink.flow.is_unknown()) and not (
                sink.flow.is_losses()
                or sink.flow == self.flow
                or self.flow.is_unknown()
            ):
                raise Exception(
                    f"incompatible flowtypes between connection {self.name} and component {sink.name}: {self.flow.name} vs {sink.flow.name}"
                )

        # if no flow is handed over: check, if it can be derived from sink or source
        else:
            # can the flow be derived from the sink without causing incompatibilities?
            if (
                source.flow.is_unknown() and not sink.flow.is_unknown()
            ) or sink.flow == source.flow:
                # if yes: set the flow as the flow of the sink
                self.flow = sink.flow

            # if no: can the flow be derived from the source without causing incompatibilities?
            elif sink.flow.is_unknown() or sink.flow.is_losses():
                # set the flow as the flow of the source
                self.flow = source.flow

            else:
                # if nothing of the above is the case the flows of source and sink must be incompatible -> throw an error
                raise Exception(
                    f"Flowtypes of origin and destination do not match: {source.flow.name} vs {sink.flow.name}"
                )

    def update_flow(self, flow):
        """This function takes a name of a flow. If the flow of the connection is not yet defined it will be set to the given flow.
        In this case the update-cascade will be continued at the other sides component of the connection.
        If the flow of the connection is already assigned, it is checked, whether the given flow matches with the defined flow.
        An Error is thrown if the flows are incompatible."""

        # do nothing if the flow already matches
        if self.flow == flow:
            return

        # ...otherwise set the flow of the connection
        self.flow = flow

        # check, if the flow of the source component is already known
        if self.source.flow.is_unknown():
            # if no: update it as well
            self.source.update_flow(flow)

        # if yes: is it compatible with the flow that has just been set for the connection?
        elif not self.source.flow == flow:
            # throw error if the flows are not the same
            raise Exception(
                f"Error while assigning flow types: interface between {self.source.name} and {self.sink.name} does not match"
            )

        # do the same for the sink side: Check, if the flow of the sink component is already known
        if self.sink.flow.is_unknown():
            # if no: update it as well
            self.sink.update_flow(flow)

        # if yes: is it compatible with the flow that has just been set for the connection?
        elif not self.sink.flow == flow:
            # throw error if the flows are not the same
            raise Exception(
                f"Error while assigning flow types: interface between {self.source.name} and {self.sink.name} does not match"
            )

        # everything succesful? -> Write log
        if self.source.factory.log:
            print(
                f"            (UPDATE) The flow of connection {self.name} is now defined as {flow.name}"
            )
