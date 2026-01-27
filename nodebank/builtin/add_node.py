# add_node.py
def add_node(inputs=None,variables=None):
    """
    inputs: list of numbers from connected nodes or field
    """
    if inputs is None:
        inputs = [0]  # default if nothing connected

    result = sum(inputs)
    return result
