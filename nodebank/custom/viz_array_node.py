# inputs:  3  (size: int, min_val: int, max_val: int)
# outputs: 1  (array: list)

import random

def viz_array_node(size: int = 50, min_val: int = 10, max_val: int = 400) -> list:
    arr = [random.randint(int(min_val), int(max_val)) for _ in range(int(size))]
    return (arr,)  # wrap in tuple so the engine treats this as 1 output, not N outputs