# random_int_node.py
import random
def random_int_node(Min, Max):
    if Min is None:
        Min = 0
    if Max is None:
        Max = 100
    Random = random.randint(Min, Max)
    return  Random
