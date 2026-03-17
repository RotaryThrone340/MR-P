"""
Mouse Recorder & Player
-----------------------
Usage:
  python mouse_recorder.py record [output.json]
  python mouse_recorder.py play   [input.json]

Record mode: Move your mouse and press ENTER to log the current position.
             Press ESC or CTRL+C to stop and save.
Play mode:   Reads a JSON file and clicks each recorded position in order.
"""

import sys
import json
import time
import threading
from pathlib import Path

# ---------------------------------------------------------------------------
# Dependency check
# ---------------------------------------------------------------------------
try:
    from pynput import mouse, keyboard
    from pynput.mouse import Button, Controller as MouseController
except ImportError:
    print("Missing dependency. Install with:\n  pip install pynput")
    sys.exit(1)

DEFAULT_FILE = "mouse_positions.json"

# ---------------------------------------------------------------------------
# RECORD MODE
# ---------------------------------------------------------------------------

def record(output_file: str):
    positions = []
    mouse_ctrl = MouseController()
    stop_event = threading.Event()

    print("=" * 50)
    print("  RECORD MODE")
    print("=" * 50)
    print(f"  Output file : {output_file}")
    print("  ENTER       → log current mouse position")
    print("  ESC         → stop recording & save")
    print("=" * 50)

    def on_press(key):
        if key == keyboard.Key.enter:
            pos = mouse_ctrl.position
            positions.append({"x": pos[0], "y": pos[1]})
            print(f"  [{len(positions):>3}] Logged  x={pos[0]}, y={pos[1]}")
        elif key == keyboard.Key.esc:
            stop_event.set()
            return False  # stop listener

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        stop_event.wait()          # block until ESC
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()

    if positions:
        with open(output_file, "w") as f:
            json.dump(positions, f, indent=2)
        print(f"\n  Saved {len(positions)} position(s) → {output_file}")
    else:
        print("\n  No positions recorded. File not written.")


# ---------------------------------------------------------------------------
# PLAY MODE
# ---------------------------------------------------------------------------

def play(input_file: str, delay: float = 0.5):
    path = Path(input_file)
    if not path.exists():
        print(f"Error: file not found → {input_file}")
        sys.exit(1)

    with open(path) as f:
        positions = json.load(f)

    if not positions:
        print("No positions found in the file.")
        sys.exit(0)

    print("=" * 50)
    print("  PLAY MODE")
    print("=" * 50)
    print(f"  Input file  : {input_file}")
    print(f"  Positions   : {len(positions)}")
    print(f"  Click delay : {delay}s")
    print("  Starting in 3 seconds — switch to your target window!")
    print("=" * 50)

    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)

    ctrl = MouseController()

    for i, pos in enumerate(positions, 1):
        x, y = pos["x"], pos["y"]
        ctrl.position = (x, y)
        time.sleep(0.05)            # small settle time before click
        ctrl.click(Button.left)
        print(f"  [{i:>3}/{len(positions)}] Clicked  x={x}, y={y}")
        time.sleep(delay)

    print(f"\n  Done. {len(positions)} click(s) performed.")


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

def usage():
    print("Usage:")
    print("  python mouse_recorder.py record [output.json]")
    print("  python mouse_recorder.py play   [input.json]  [delay_seconds]")
    sys.exit(1)


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        usage()

    mode = args[0].lower()

    if mode == "record":
        out = args[1] if len(args) > 1 else DEFAULT_FILE
        record(out)

    elif mode == "play":
        inp   = args[1] if len(args) > 1 else DEFAULT_FILE
        delay = float(args[2]) if len(args) > 2 else 0.5
        play(inp, delay)

    else:
        usage()