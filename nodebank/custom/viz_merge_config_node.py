# inputs:  3  (array, viz_config, window_config)
# outputs: 1  (full_config: dict)

def viz_merge_config_node(array: list, viz_config: dict, window_config: dict) -> dict:
    return {
        "array": array,
        "viz": viz_config,
        "window": window_config,
    }