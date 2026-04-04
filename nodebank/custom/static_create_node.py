# inputs:  2  (serve_static: bool, directory: str)
# outputs: 1  (static_config: dict)

import os

def static_create_node(serve_static: bool = False,
        directory: str = "./public") -> dict:
    return {
        "enabled": bool(serve_static),
        "directory": os.path.abspath(directory)
    }