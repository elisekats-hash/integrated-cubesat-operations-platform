from __future__ import annotations

__author__ = "Elise Katsube"
__version__ = "22/06/26"

MAX_WHEEL_SPEED = 100

KP = 2.0
KD = 0.5

def control_attitude(roll_error, pitch_error, yaw_error,
                     wx, wy, wz):

    wheel_x = KP * roll_error - KD * wx
    wheel_y = KP * pitch_error - KD * wy
    wheel_z = KP * yaw_error - KD * wz

    wheel_x = max(min(wheel_x, MAX_WHEEL_SPEED), -MAX_WHEEL_SPEED)
    wheel_y = max(min(wheel_y, MAX_WHEEL_SPEED), -MAX_WHEEL_SPEED)
    wheel_z = max(min(wheel_z, MAX_WHEEL_SPEED), -MAX_WHEEL_SPEED)

    return {
        "wheel_x": float(wheel_x),
        "wheel_y": float(wheel_y),
        "wheel_z": float(wheel_z)
    }