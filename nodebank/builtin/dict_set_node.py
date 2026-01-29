# dict_set_node.py
def dict_set_node(DictObj, Key, Value):
    if DictObj is None:
        DictObj = {}
    DictObj[Key] = Value
    return DictObj
