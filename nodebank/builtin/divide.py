def divide(inputs, variables):
    """
    inputs: [a, b]
    returns: a / b
    """
    a = inputs[0] if len(inputs) > 0 else 0
    b = inputs[1] if len(inputs) > 1 else 1
    if float(b) == 0:
        raise ValueError("Division by zero")
    return float(a) / float(b)
