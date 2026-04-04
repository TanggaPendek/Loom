# inputs:  2  (route_a: dict, route_b: dict)
# outputs: 1  (routes: list)

def routes_merge_node(route_a: dict, route_b: dict) -> list:
    result = []
    for r in (route_a, route_b):
        if isinstance(r, dict) and "path" in r:
            result.append(r)
        elif isinstance(r, list):
            result.extend(r)
    return result