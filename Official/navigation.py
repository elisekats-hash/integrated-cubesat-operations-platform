from __future__ import annotations

__author__ = "Elise Katsube"
__version__ = "22/06/26"

import math
import engine_control
import attitude_control

DESIRED_ROLL = 0
DESIRED_PITCH = 0
DESIRED_YAW = 0

DESIRED_RADIUS = 6771 #km

def calculate_orbit_error(position) -> float:

    x = position["x"]
    y = position["y"]
    z = position["z"]

    current_radius = math.sqrt(x**2 + y**2 + z**2)

    return DESIRED_RADIUS - current_radius

def calculate_attitude_error(orientation) -> float:
    roll_error = DESIRED_ROLL - orientation["roll"]
    pitch_error = DESIRED_PITCH - orientation["pitch"]
    yaw_error = DESIRED_YAW - orientation["yaw"]

    return roll_error, pitch_error, yaw_error

def process_telemetry(data) -> dict:
    position = data["position_km"]
    orientation = data["orientation_deg"]

    angular_velocity = data["angular_velocity_deg_s"]
    wx = angular_velocity["wx"]
    wy = angular_velocity["wy"]
    wz = angular_velocity["wz"]

    orbit_error = calculate_orbit_error(position)

    orbit_command = engine_control.orbit_correction(orbit_error)

    roll_error, pitch_error, yaw_error = calculate_attitude_error(orientation)

    attitude_command = attitude_control.control_attitude(roll_error, 
            pitch_error, yaw_error,wx, wy, wz)

    return {"thrusters": orbit_command, 
            "reaction_wheels":attitude_command}