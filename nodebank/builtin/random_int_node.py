# random_int_node.py
import random
from executor.utils.node_logger import log_print

def random_int_node(Min, Max):
    if Min is None:
        Min = 0
    if Max is None:
        Max = 100
    
    log_print(f"Generating random integer between {Min} and {Max}")
    
    Random = random.randint(Min, Max)
    
    log_print(f"Generated: {Random}")
    
    return Random
