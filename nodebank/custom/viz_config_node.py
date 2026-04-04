# inputs:  4  (algorithm: str, speed: int, bar_color: str, highlight_color: str)
# outputs: 1  (config: dict)

def viz_config_node(algorithm: str = "bubble",
                         speed: int = 30,
                         bar_color: str = "#4fc3f7",
                         highlight_color: str = "#ff6b6b") -> dict:
    valid = ("bubble", "merge", "quick")
    algorithm = algorithm.lower().strip()
    if algorithm not in valid:
        algorithm = "bubble"
    return {
        "algorithm": algorithm,
        "speed": int(speed),
        "bar_color": bar_color,
        "highlight_color": highlight_color,
    }