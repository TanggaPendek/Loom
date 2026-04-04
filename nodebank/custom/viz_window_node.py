# inputs:  3  (width: int, height: int, title: str)
# outputs: 1  (window_config: dict)

def viz_window_node(width: int = 800,
                     height: int = 500,
                     title: str = "Sorting Visualizer") -> dict:
    return {
        "width": int(width),
        "height": int(height),
        "title": str(title),
    }