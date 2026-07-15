# Architecture

## Components

| Module | Role |
|--------|------|
| `roarm_api_server.py` | Flask entry point; serves the UI and registers API routes |
| `roarm_handler.py` | HTTP handlers for arm endpoints |
| `roarm_driver.py` | Joint state, simulation logic, optional serial I/O |
| `web_page_use_arm.html` | Control panel UI |
| `web_page.js` | Fetch calls and Three.js visualization |

## Operating modes

### Simulation (default)

- `ROBOT_SERIAL_PORT` is unset or empty.
- Joint angles and LED state live in process memory.
- `send_cmd()` does not open a serial port.
- API responses include `"mode": "simulation"`.

### Hardware

- `ROBOT_SERIAL_PORT` must be set explicitly (no auto-detect on startup).
- Commands are sent as newline-terminated JSON over serial.
- API responses include `"mode": "hardware"`.

## Serial command reference

These commands match the protocol already used by the original driver:

| Action | JSON |
|--------|------|
| Init / feedback enable | `{ "T": 210, "cmd": 1 }` |
| Joint move | `{ "T": 101, "joint": 1-4, "rad": value, "spd": 0, "acc": 10 }` |
| Reset | `{ "T": 100 }` |
| LED | `{ "T": 114, "led": 255 }` or `{ "T": 114, "led": 0 }` |

Default joint angles after reset: `[0.0, 0.0, 1.57, 3.14]`.

## Request flow (joint adjust)

1. Browser `POST /arm_control` with `{ joint, dir }`.
2. Handler validates types and calls `driver.adjust_joint`.
3. Driver updates in-memory angles (within limits).
4. In hardware mode, driver serializes and writes the `T:101` command.
5. Response returns `{ angles, mode }` for UI / 3D update.

## Intentionally omitted

This portfolio build does not include:

- Parent-robot WebSocket movement control
- Camera streams
- System reboot / shutdown endpoints
- USB copy or data-clear microservices
- Organization branding or internal deployment scripts
