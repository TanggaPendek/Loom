import threading
import webview
import uvicorn
import os
import sys
from backend.src.main_backend import app

def start_backend():
    uvicorn.run(app, host="127.0.0.1", port=8000)

def on_close():
    os._exit(0)  # force exit safely

if __name__ == "__main__":
    # Start backend thread
    t = threading.Thread(target=start_backend, daemon=True)
    t.start()

    # Create window
    window = webview.create_window("Loom", "http://127.0.0.1:8000", width=1200, height=800)

    # 1. You already have this right! This is the modern way to handle closures.
    window.events.closed += on_close

    # 2. Fix: Remove any hidden 'on_closed' arguments. 
    # Just call start() with the GUI renderer and debug mode.
    webview.start(gui='edgechromium', debug=True)