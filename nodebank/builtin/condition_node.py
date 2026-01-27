def condition_node(inputs, variables=None):
    """
    inputs: dict or list
        - first input = value to test
        - second input = value to compare against
    returns: dict {"true": value, "false": value} depending on equality
    """
    # normalize inputs to a list
    if isinstance(inputs, dict):
        input_list = list(inputs.values())
    elif isinstance(inputs, list):
        input_list = inputs
    else:
        input_list = [inputs]

    # ensure we have at least 2 values
    if len(input_list) < 2:
        raise ValueError("condition_node requires at least 2 inputs")

    test_value = input_list[0]
    compare_value = input_list[1]

    if test_value == compare_value:
        return {"true": test_value}
    else:
        return {"false": test_value}
