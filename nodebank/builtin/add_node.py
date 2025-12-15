def add_node(inputs, variables):
    # if inputs are guaranteed numeric, parsing not needed
    result = sum(inputs)
    variables["out_2"] = result
    return result
