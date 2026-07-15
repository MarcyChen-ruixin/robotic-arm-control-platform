"""Low-level RoArm driver with simulation mode by default.

Physical serial I/O is used only when ROBOT_SERIAL_PORT is explicitly set.
Otherwise the driver keeps joint state in memory and never opens hardware.
"""

from __future__ import annotations

import json
import os
import time
from typing import List, Optional, Union

joint_ids = [1, 2, 3, 4]
joint_limits = [(-3.0, 3.0), (-1.57, 0.9), (-0.75, 3.0), (1.04, 3.14)]
joint_rads = [0.0, 0.0, 1.57, 3.14]
led_on = False

_ser = None


def is_simulation_mode() -> bool:
    """True unless ROBOT_SERIAL_PORT is set to a non-empty value."""
    port = os.getenv("ROBOT_SERIAL_PORT", "").strip()
    return not port


def _baudrate() -> int:
    return int(os.getenv("ROBOT_BAUDRATE", "115200"))


def _get_serial():
    """Open the configured serial port on first use. Never auto-detects."""
    global _ser
    if _ser is not None:
        return _ser

    port = os.getenv("ROBOT_SERIAL_PORT", "").strip()
    if not port:
        raise RuntimeError(
            "Simulation mode is active. Set ROBOT_SERIAL_PORT to enable hardware."
        )

    import serial

    _ser = serial.Serial(port, baudrate=_baudrate(), timeout=1)
    time.sleep(2)
    # Enable feedback / init mode used by the arm firmware protocol.
    send_cmd({"T": 210, "cmd": 1})
    return _ser


def send_cmd(cmd_dict: dict) -> List[str]:
    """Send a JSON command. In simulation mode, return an empty response list."""
    if is_simulation_mode():
        return []

    ser = _get_serial()
    ser.write((json.dumps(cmd_dict) + "\n").encode())
    time.sleep(0.1)
    responses = []
    while ser.in_waiting:
        responses.append(ser.readline().decode().strip())
    return responses


def _direction_delta(direction: Union[float, int, str]) -> float:
    if isinstance(direction, (int, float)):
        return float(direction)
    return 0.1 if direction == "plus" else -0.1


def adjust_joint(joint_index: int, direction: Union[float, int, str]) -> List[float]:
    delta = _direction_delta(direction)
    new_val = joint_rads[joint_index] + delta
    min_val, max_val = joint_limits[joint_index]
    if min_val <= new_val <= max_val:
        joint_rads[joint_index] = new_val
        send_cmd(
            {
                "T": 101,
                "joint": joint_ids[joint_index],
                "rad": new_val,
                "spd": 0,
                "acc": 10,
            }
        )
    return joint_rads.copy()


def reset_arm() -> List[float]:
    """Reset joints to the documented default angles (protocol T:100)."""
    global joint_rads
    send_cmd({"T": 100})
    joint_rads = [0.0, 0.0, 1.57, 3.14]
    return joint_rads.copy()


def toggle_led() -> bool:
    """Toggle LED via the documented protocol command T:114."""
    global led_on
    led_on = not led_on
    send_cmd({"T": 114, "led": 255 if led_on else 0})
    return led_on


def get_current_angles() -> List[float]:
    return joint_rads.copy()


def get_status() -> dict:
    return {
        "mode": "simulation" if is_simulation_mode() else "hardware",
        "serial_port": os.getenv("ROBOT_SERIAL_PORT", "").strip() or None,
        "angles": joint_rads.copy(),
        "led": led_on,
    }


def cleanup() -> None:
    global _ser
    if _ser is not None:
        _ser.close()
        _ser = None
