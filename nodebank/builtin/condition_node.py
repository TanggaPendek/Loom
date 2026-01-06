def condition_node(inputs, variables):
    """
    Condition node: checks if first input < second input.
    
    inputs[0] = current value (from previous node)
    inputs[1] = threshold value (e.g., 1000)
    
    Returns:
        True if inputs[0] < inputs[1], False otherwise
    """
    # extract numeric inputs
    current_value = inputs[0]
    threshold = inputs[1]

    # evaluate condition
    result = current_value < threshold

    # optionally store in variables for downstream nodes
    variables["condition_result"] = result

    return result
