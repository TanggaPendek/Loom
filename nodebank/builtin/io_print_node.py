# print.py
from executor.utils.node_logger import log_print

def io_print_node(inputs):
    log_print(f"Printing: {inputs}")
    print(inputs)
