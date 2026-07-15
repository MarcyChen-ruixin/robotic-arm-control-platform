# RoArm Control Demo

Browser-based robotic arm control with a Flask API, serial communication abstraction, and a Three.js visualization. Built as a portfolio and research demonstration by **Ruixin Chen**.

This repository is provided as a portfolio and research demonstration.
No license for reuse or redistribution is granted.

---

## Overview

This project demonstrates a clean software stack for controlling a multi-joint robotic arm (RoArm-compatible protocol):

- REST endpoints for joint motion, reset, LED toggle, and status feedback
- A serial driver that supports **simulation by default** and optional physical hardware
- A lightweight HTML/JS control panel with live 3D visualization

By default the application runs entirely in **Simulation Mode** — no robot, serial port, or external services are required.

---

## Key Features

- Simulation mode with in-memory joint state (default)
- Optional hardware mode via explicit `ROBOT_SERIAL_PORT`
- Flask REST API for arm control
- Joint limits and incremental angle updates
- Three.js 3D arm visualization
- Environment-based configuration
- Local-only default bind address (`127.0.0.1`)

---

## Architecture

```
Browser UI  ──HTTP──►  Flask (roarm_api_server)
                              │
                              ▼
                       roarm_handler (routes)
                              │
                              ▼
                       roarm_driver
                         ├── Simulation (default): in-memory state
                         └── Hardware: JSON-over-serial protocol
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for protocol details and endpoint reference.

---

## Screenshots

Place screenshots in `docs/images/`:

| Placeholder | Suggested content |
|-------------|-------------------|
| `docs/images/ui-overview.png` | Full control panel with Simulation Mode badge |
| `docs/images/3d-arm.png` | Three.js visualization after joint motion |

*(Add your own screenshots before publishing.)*

---

## Quick Start (Simulation Mode)

```bash
# 1. Create and activate a virtual environment
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
# .venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server (simulation mode — do not set ROBOT_SERIAL_PORT)
python roarm_api_server.py
```

Open [http://127.0.0.1:5005](http://127.0.0.1:5005) in a browser.

You should see a **Simulation Mode** badge. Joint buttons update the 3D view and API responses without contacting hardware.

---

## Optional Physical Hardware Setup

1. Connect a compatible arm via USB serial.
2. Copy `.env.example` to `.env` and set:

```bash
ROBOT_SERIAL_PORT=/dev/ttyUSB0   # or COM3 on Windows
ROBOT_BAUDRATE=115200
```

3. Export those variables (or use a tool that loads `.env`), then start the server:

```bash
export ROBOT_SERIAL_PORT=/dev/ttyUSB0   # Linux/macOS
python roarm_api_server.py
```

The UI badge switches to **Hardware Mode**. Serial I/O opens only when `ROBOT_SERIAL_PORT` is set — there is no auto-detection on startup.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ROARM_API_HOST` | `127.0.0.1` | Flask bind address |
| `ROARM_API_PORT` | `5005` | Flask listen port |
| `ROBOT_SERIAL_PORT` | _(empty)_ | If unset → simulation; if set → hardware serial path |
| `ROBOT_BAUDRATE` | `115200` | Serial baud rate (hardware mode only) |

See `.env.example` for a template. Do not commit a real `.env` file.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/arm_status` | Mode, angles, LED state |
| `POST` | `/arm_control` | Adjust joint; body `{"joint": 0-3, "dir": ±0.05}` |
| `POST` | `/arm_reset` | Reset to default angles (protocol `T:100`) |
| `POST` | `/arm_led` | Toggle LED (protocol `T:114`) |
| `GET` | `/arm_feedback` | Current angles and mode |

---

## Security Limitations

- There is **no authentication** on API endpoints.
- Default binding is localhost only; do not expose this server to the public internet without a reverse proxy, TLS, and access control.
- Hardware mode can move a physical robot — verify workspace safety before enabling `ROBOT_SERIAL_PORT`.
- System reboot/shutdown and USB/data administrative features are **not included** in this portfolio build.

---

## Technology Stack

- Python 3.8+
- Flask
- pyserial (hardware mode only)
- HTML / CSS / JavaScript
- Three.js (CDN)

---

## Repository Layout

```
github_release/
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
├── roarm_api_server.py
├── roarm_driver.py
├── roarm_handler.py
├── web_page.js
├── web_page_use_arm.html
├── docs/
│   ├── ARCHITECTURE.md
│   └── images/
└── scripts/
    └── start_roarm.sh.example
```

---

## Author

**Ruixin Chen**

---

## License Notice

This repository is provided as a portfolio and research demonstration.
No license for reuse or redistribution is granted.
