# math_divide_node.py
import sys

def math_divide_node(Inputs1, Inputs2):
    if Inputs1 is None:
        Inputs1 = 0
    else:
        Inputs1 = float(Inputs1)
    
    if Inputs2 is None or float(Inputs2) == 0:
        sys.exit("Cannot divide by zero!")
    else:
        Inputs2 = float(Inputs2)
    
    Math = Inputs1 / Inputs2
    return Math