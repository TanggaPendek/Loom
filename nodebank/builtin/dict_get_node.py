# dict_get_node.py
def dict_get_node(DictObj, Key):
    if DictObj is None:
        return None
    return DictObj.get(Key)
