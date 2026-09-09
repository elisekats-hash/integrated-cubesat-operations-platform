from __future__ import annotations

"""Thermal Control"""

__author__ = "Elise Katsube"
__version__ = "11/06/26"

TARGET_TEMP = 20.0 #in kevlin, ~20 C, 293.15
TEMP_TOLERANCE = 5.0
#assuming up to 5 k above or down to 5 k below this temp is ok
#at 5 k below and 5 k above -> adjusting need to be done


def check_temperature(curr_temp:float)-> dict:
    
    error = TARGET_TEMP - curr_temp

    if error > TEMP_TOLERANCE:
        return {"heater": True, "cooler":False}
        #curr_temp too cold, need heater
    elif error < -TEMP_TOLERANCE:
        return {"heater":False, "cooler":True}
        #curr_temp too hot, need cooler

    return {"heater":False,"cooler":False}
