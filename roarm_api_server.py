"""Flask API server for RoArm robotic arm control (portfolio demo).

By default the server binds to 127.0.0.1 and runs in simulation mode
(no serial hardware connection) unless ROBOT_SERIAL_PORT is set.
"""

import os
from pathlib import Path

from flask import Flask, send_from_directory

from roarm_handler import roarm_bp

ROOT = Path(__file__).resolve().parent

app = Flask(__name__, static_folder=None)
app.register_blueprint(roarm_bp)


@app.route("/")
def index():
    return send_from_directory(ROOT, "web_page_use_arm.html")


@app.route("/web_page.js")
def frontend_js():
    return send_from_directory(ROOT, "web_page.js")


@app.route("/web_page_use_arm.html")
def frontend_html():
    return send_from_directory(ROOT, "web_page_use_arm.html")


if __name__ == "__main__":
    host = os.getenv("ROARM_API_HOST", "127.0.0.1")
    port = int(os.getenv("ROARM_API_PORT", "5005"))
    print(f"Starting RoArm demo on http://{host}:{port}")
    print("Mode: simulation" if not os.getenv("ROBOT_SERIAL_PORT", "").strip() else "Mode: hardware")
    app.run(host=host, port=port, debug=False)
