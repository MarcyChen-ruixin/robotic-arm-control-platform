"""Flask blueprint exposing RoArm control endpoints."""

from flask import Blueprint, jsonify, request

import roarm_driver as driver

roarm_bp = Blueprint("roarm", __name__)


@roarm_bp.route("/arm_status", methods=["GET"])
def status():
    return jsonify(driver.get_status())


@roarm_bp.route("/arm_control", methods=["POST"])
def control():
    data = request.get_json(silent=True) or {}
    joint = data.get("joint")
    direction = data.get("dir")
    if isinstance(joint, int) and isinstance(direction, (float, int, str)):
        angles = driver.adjust_joint(joint, direction)
        return jsonify(
            {
                "angles": angles,
                "mode": "simulation" if driver.is_simulation_mode() else "hardware",
            }
        )
    return jsonify({"error": "Invalid input"}), 400


@roarm_bp.route("/arm_reset", methods=["POST"])
def reset():
    angles = driver.reset_arm()
    return jsonify(
        {
            "angles": angles,
            "mode": "simulation" if driver.is_simulation_mode() else "hardware",
        }
    )


@roarm_bp.route("/arm_led", methods=["POST"])
def led():
    led_state = driver.toggle_led()
    return jsonify(
        {
            "led": led_state,
            "mode": "simulation" if driver.is_simulation_mode() else "hardware",
        }
    )


@roarm_bp.route("/arm_feedback", methods=["GET"])
def feedback():
    angles = driver.get_current_angles()
    return jsonify(
        {
            "angles": angles,
            "led": driver.led_on,
            "mode": "simulation" if driver.is_simulation_mode() else "hardware",
        }
    )
