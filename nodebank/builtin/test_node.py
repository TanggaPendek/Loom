# multi_io_node.py

def test_node(a, b, c):
    """
    Example node that takes 3 inputs and returns 3 outputs.
    """
    sum_val = a + b + c
    product = a * b * c
    max_val = max(a, b, c)
    return sum_val, product, max_val
