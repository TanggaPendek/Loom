# math_add_node.py
from executor.utils.node_logger import log_print

def math_add_node(Inputs1, Inputs2):
    # Log the operation
    log_print(f"Adding {Inputs1} + {Inputs2}")
    
    if Inputs1 is None:
        Inputs1 = 0
    if Inputs2 is None:
        Inputs2 = 0
    
    Math = Inputs1 + Inputs2
    
    # Log the result
    log_print(f"Result: {Math}")
    
    return Math
