# inputs:  4  (path: str, method: str, status: int, body: str)
# outputs: 1  (route: dict)

def routes_create_node(path: str = "/",
        method: str = "GET",
        status: int = 200,
        body: str = "OK") -> dict:
    return {
        "path": path.strip(),
        "method": method.upper().strip(),
        "status": int(status),
        "body": body,
    }