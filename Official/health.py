"""Health supervisor module."""

from __future__ import annotations

__author__ = "Elise Katsube"
__version__ = "11/06/26"

import thermal_control #type: ignore
import power_control #type: ignore

def process_telemetry(data:float) -> dict:

    if (data.get("temperature_c") is None or data.get("battery_percent") is None):
        print("ERROR: Incomplete health telemetry")
        return {}

    thermal_command = thermal_control.check_temperature(data.get("temperature_c"))

    power_command = power_control.check_battery(data.get("battery_percent"))

    return {"thermal":thermal_command, "power":power_command}