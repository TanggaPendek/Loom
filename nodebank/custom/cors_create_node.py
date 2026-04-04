# inputs:  3  (enabled: bool, origins: str, methods: str)
# outputs: 1  (cors_config: dict)

def cors_create_node(enabled: bool = False,
        origins: str = "*",
        methods: str = "GET,POST,OPTIONS") -> dict:
    return {
        "enabled": bool(enabled),
        "origins": origins,
        "methods": [m.strip() for m in methods.split(",")]
    }