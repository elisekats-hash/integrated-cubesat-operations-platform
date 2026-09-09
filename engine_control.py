from __future__ import annotations

"""Engine control module."""

__author__ = "Elise Katsube"
__version__ = "07/09/26"

import math

DESIRED_RADIUS = 6771.0       # km
EARTH_MU = 398600.4418        # km^3/s^2
MASS = 1.33                   # kg

MAX_THRUST = 0.5              # N
KP = 0.5                      # velocity correction gain

MIN_VELOCITY_ERROR = 0.005    # km/s


def orbit_correction(position: dict, velocity: dict) -> dict:
    """
    Determine a small thruster correction to help maintain
    a circular orbit at DESIRED_RADIUS.
    """

    x = float(position["x"])
    y = float(position["y"])
    z = float(position["z"])

    vx = float(velocity["vx"])
    vy = float(velocity["vy"])
    vz = float(velocity["vz"])

    # Current distance from Earth's center
    radius = math.sqrt(x**2 + y**2 + z**2)

    # Current velocity magnitude
    speed = math.sqrt(vx**2 + vy**2 + vz**2)

    # Desired circular orbital velocity
    desired_speed = math.sqrt(EARTH_MU / radius)

    # Difference between desired and current velocity
    velocity_error = desired_speed - speed

    # If we're already close enough, don't fire
    if abs(velocity_error) < MIN_VELOCITY_ERROR:
        return {
            "thruster_direction": "off",
            "thruster_newtons": 0.0,
            "duration_ms": 0
        }

    # Proportional controller
    thrust = min(abs(velocity_error) * KP, MAX_THRUST)

    if velocity_error > 0:
        # Moving too slowly -> accelerate prograde
        direction = "prograde"
    else:
        # Moving too quickly -> slow down retrograde
        direction = "retrograde"

    return {
        "thruster_direction": direction,
        "thruster_newtons": float(thrust),
        "duration_ms": 100
    }
    