# print.py
def print_node(inputs, variables):
    # just print first input
    value = inputs[0] if inputs else None
    print(f"[Node: print] Value = {value}")
