# inputs:  1  (port: int)
# outputs: 1  (port: int)

def port_create_node(port: int = 8080) -> int:
    assert 1 <= int(port) <= 65535, f"Invalid port: {port}"
    return int(port)