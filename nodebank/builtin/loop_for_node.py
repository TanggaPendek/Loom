# loop_for_node.py
def loop_for_node(Start, End, Step):
    if Start is None:
        Start = 0
    if End is None:
        End = 1
    if Step is None or Step == 0:
        Step = 1
    Loop = list(range(Start, End, Step))
    return Loop