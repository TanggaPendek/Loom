def subtract(inputs, variables):
    """
    inputs: [a, b]
    returns: a - b
    """
    a = inputs[0] if len(inputs) > 0 else 0
    b = inputs[1] if len(inputs) > 1 else 0
    return float(a) - float(b)
