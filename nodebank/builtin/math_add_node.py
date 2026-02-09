# math_add_node.py
from executor.utils.node_logger import log_print

def math_add_node(Inputs1, Inputs2):
    # Convert to float to handle both int and float strings
    if Inputs1 is None:
        Inputs1 = 0
    else:
        Inputs1 = float(Inputs1)
    
    if Inputs2 is None:
        Inputs2 = 0
    else:
        Inputs2 = float(Inputs2)
    
    log_print(f"Adding {Inputs1} + {Inputs2}")
    Math = Inputs1 + Inputs2
    log_print(f"Result: {Math}")
    
    return Math