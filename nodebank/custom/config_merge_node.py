# inputs:  4  (port, host, cors_config, static_config)
# outputs: 1  (server_config: dict)

def config_merge_node(port: int,
        host: str,
        cors_config: dict) -> dict:
    return {
        "port": port,
        "host": host,
        "cors": cors_config,
    }