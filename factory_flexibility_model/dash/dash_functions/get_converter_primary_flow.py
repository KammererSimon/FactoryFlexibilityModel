def get_converter_primary_flow(converter):
    """
    This function takes a ffm.converter-object and determines, which flowtype is the one that the operation of the converter is being measured in.
    By now this happenes by checking, which of the in- or outputs is specified with a weight of one.
    For future releases this prinary flow should be determined directly within the converter component.
    """

    # iterate over all inputs and return the flowtype if a weight of one is found
    for input in converter.inputs:
        if input.weight == 1:
            return input.flowtype

    # iterate over all outputs and return the flowtype if a weight of one is found
    for output in converter.outputs:
        if output.weight == 1:
            return output.flowtype

    # return the flowtype of the last output if no connection with weight 1 was identified
    return output.flowtype