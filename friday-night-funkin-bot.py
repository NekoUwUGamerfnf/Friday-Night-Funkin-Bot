import cv2
import numpy as np
import time
import keyboard
from mss import mss
import os
import platform
import sys
from dotenv import load_dotenv

def load_lanes_from_env():
    default_lanes = {
        1: {'left': 1310, 'key': 'z'},
        2: {'left': 1570, 'key': 'x'},
        3: {'left': 1850, 'key': ','},
        4: {'left': 2125, 'key': '.'}
    }
    base_path = (os.path.dirname(sys.executable)
                 if getattr(sys, 'frozen', False)
                 else os.path.dirname(__file__))
    env_path = os.path.join(base_path, '.env')
    if not os.path.exists(env_path):
        with open(env_path, 'w') as f:
            f.write(f"LANE_COUNT={len(default_lanes)}\n")
            for i, info in default_lanes.items():
                f.write(f"LANE_{i}_LEFT={info['left']}\n")
                f.write(f"LANE_{i}_KEY={info['key']}\n")
                f.write(f"LANE_{i}_COLOR=0,225,255\n")
            f.write("TOP=235\n")
    load_dotenv(env_path)
    lane_count = int(os.getenv("LANE_COUNT", len(default_lanes)))
    lanes = {}
    for i in range(1, lane_count + 1):
        left_default = default_lanes.get(i, {}).get('left', 0)
        key_default = default_lanes.get(i, {}).get('key', '')
        left = int(os.getenv(f"LANE_{i}_LEFT", left_default))
        key = os.getenv(f"LANE_{i}_KEY", key_default)
        lanes[i] = {'left': left, 'key': key}
    target_colors = {}
    for i in range(1, lane_count + 1):
        col_str = os.getenv(f"LANE_{i}_COLOR", "0,225,255")
        rgb = [int(x) for x in col_str.split(",")]
        target_colors[i] = np.array(rgb[::-1])
    top = int(os.getenv("TOP", 235))
    return lanes, lane_count, target_colors, top

lanes, lane_count, target_colors, top = load_lanes_from_env()

color_tolerance = 30

def clear_console():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def monitor_lanes():
    left0 = lanes[1]['left']
    right0 = lanes[lane_count]['left']
    region = {'top': top, 'left': left0, 'width': right0 - left0 + 1, 'height': 1}
    statuses = {i: False for i in lanes}
    updated = False
    firsttime = True
    with mss() as sct:
        while True:
            frame = np.array(sct.grab(region))[:, :, :3]
            for i, info in lanes.items():
                x = info['left'] - left0
                px = frame[0, x]
                color = target_colors[i]
                hit = bool(np.all(np.abs(px - color) <= color_tolerance))
                if hit and not statuses[i]:
                    keyboard.press(info['key'])
                    statuses[i] = True
                    updated = True
                    firsttime = False
                elif firsttime or not hit and statuses[i]:
                    keyboard.release(info['key'])
                    statuses[i] = False
                    updated = True
                    firsttime = False
            if updated:
                clear_console()
                for i, info in lanes.items():
                    state = "Being Pressed" if statuses[i] else "Not Being Pressed"
                    print(f"Key {info['key']} Is {state}")
                updated = False
            time.sleep(0.016) # Don't Disable Or Change This

if __name__ == '__main__':
    monitor_lanes()
