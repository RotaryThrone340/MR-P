"""
Mouse Recorder & Player
-----------------------
Run the script and follow the interactive prompts.
"""

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
    raise SystemExit(1)

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
            return False

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        stop_event.wait()
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
        return

    with open(path) as f:
        positions = json.load(f)

    if not positions:
        print("No positions found in the file.")
        return

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
        time.sleep(0.05)
        ctrl.click(Button.left)
        print(f"  [{i:>3}/{len(positions)}] Clicked  x={x}, y={y}")
        time.sleep(delay)

    print(f"\n  Done. {len(positions)} click(s) performed.")


# ---------------------------------------------------------------------------
# INTERACTIVE MENU
# ---------------------------------------------------------------------------

def prompt_file(label: str, default: str) -> str:
    val = input(f"  {label} [{default}]: ").strip()
    return val if val else default


def prompt_float(label: str, default: float) -> float:
    while True:
        val = input(f"  {label} [{default}]: ").strip()
        if not val:
            return default
        try:
            return float(val)
        except ValueError:
            print("  Please enter a valid number.")


def main():
    while True:
        print("\n" + "=" * 50)
        print("  MOUSE RECORDER & PLAYER")
        print("=" * 50)
        print("  [1] Record mouse positions")
        print("  [2] Play back mouse positions")
        print("  [3] Quit")
        print("=" * 50)

        choice = input("  Choose an option: ").strip()

        if choice == "1":
            output_file = prompt_file("Output file", DEFAULT_FILE)
            record(output_file)

        elif choice == "2":
            input_file = prompt_file("Input file", DEFAULT_FILE)
            delay = prompt_float("Delay between clicks (seconds)", 0.5)
            play(input_file, delay)

        elif choice == "3":
            print("\n  Goodbye!")
            break

        else:
            print("\n  Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()