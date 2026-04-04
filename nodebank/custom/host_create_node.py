# inputs:  1  (host: str)
# outputs: 1  (host: str)

def host_create_node(host: str = "0.0.0.0") -> str:
    return str(host).strip()