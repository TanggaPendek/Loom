# math_divide_node.py
import sys

def math_divide_node(Inputs1, Inputs2):
    if Inputs1 is None:
        Inputs1 = 0
    if Inputs2 in (None, 0):
         sys.exit("Cannot divide by zero!")
    Math = Inputs1 / Inputs2
    return Math