# math_subtract_node.py
def math_subtract_node(Inputs1, Inputs2):
    if Inputs1 is None:
        Inputs1 = 0
    else:
        Inputs1 = float(Inputs1)
    
    if Inputs2 is None:
        Inputs2 = 0
    else:
        Inputs2 = float(Inputs2)
    
    Math = Inputs1 - Inputs2
    return Math