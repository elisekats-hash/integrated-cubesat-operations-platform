from __future__ import annotations

"""Power control module."""

__author__ = "Elise Katsube"
__version__ = "11/06/26"

#low battery around 30 ~ 20 should be triggered
#use 30% to be safe for now
LOW_BATTERY = 50 #start conserving power at this stage
CRITICAL_BATTERY = 20 #BAD

# include an emergency mode??? @ 15? or 10

def check_battery(battery_perc:float) -> dict:
    if battery_perc < CRITICAL_BATTERY:
        #print("Turning on safe mode...\n Disabling payload...\n")
        #print("Disabling attitude control...\nEmerengy Power: ON")
        return {"safe_mode":True,"disable_payload":True,
                "disable_attitude_control":True,
                "emergency_power": True}
    elif battery_perc < LOW_BATTERY:
        #print("Turning on safe mode...\nDisabling payload...")
        return {"safe_mode":True,"disable_payload":True,
                "disable_attitude_control":False,
                "emergency_power": False}
        #will now draw power from storage

    return {"safe_mode":False,"disable_payload":False,
            "disable_attitude_control":False,
            "emergency_power": False}