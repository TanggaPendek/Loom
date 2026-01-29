# random_float_node.py
import random
def random_float_node(Min, Max):
    if Min is None:
        Min = 0.0
    if Max is None:
        Max = 1.0
    Random = random.uniform(Min, Max)
    return  Random