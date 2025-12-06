# main_engine.py
import sys
import json
from pathlib import Path
from datetime import datetime


def main():
    if len(sys.argv) < 2:
        print("Usage: python main_engine.py <input_file.json>")
        return

    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Input file not found: {input_file}")
        return

    with open(input_file) as f:
        payload = json.load(f)

    action = payload.get("action", "run")

    print("Engine done!")

if __name__ == "__main__":
    main()
