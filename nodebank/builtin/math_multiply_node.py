# math_multiply_node.py
def math_multiply_node(Inputs1, Inputs2):
    if Inputs1 is None:
        Inputs1 = 1
    else:
        Inputs1 = float(Inputs1)
    
    if Inputs2 is None:
        Inputs2 = 1
    else:
        Inputs2 = float(Inputs2)
    
    Math = Inputs1 * Inputs2
    return Math
