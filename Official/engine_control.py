from __future__ import annotations

__author__ = "Elise Katsube"
__version__ = "22/06/26"

def orbit_correction(error) -> dict:
    # within 1 km of desired orbit - no correction needed
    if abs(error) < 1:
        return {
            "thruster_direction": "off", 
            "thruster_newtons":0, 
            "duration_ms": 0}
    # orbit is below desired radius - accelerate prograde
    elif error > 0:
        return {
            "thruster_direction":"prograde",
            "thruster_newtons":min(error*10, 100), 
            "duration_ms":500}
    # orbit is above desired radius - slow down retrograde
    else:
        return {
            "thruster_direction":"retrograde",
            "thruster_newtons":min(abs(error)*10, 100), 
            "duration_ms":500}

    