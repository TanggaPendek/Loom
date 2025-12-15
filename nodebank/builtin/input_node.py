# nodebank/builtin/input.py
def input_node(inputs, variables):
    # output var is defined in node JSON
    out_var = "out_1"

    # take literal from inputs (should already be numeric from VariableManager)
    value = inputs[0] if inputs else 10  # fallback default
    # store it in temp store
    variables[out_var] = value

    return value
