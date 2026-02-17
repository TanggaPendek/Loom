# string_concat_node.py
def string_concat_node(Str1, Str2):
    if Str1 is None:
        Str1 = ""
    if Str2 is None:
        Str2 = ""
    String = str(Str1) + str(Str2)
    return String