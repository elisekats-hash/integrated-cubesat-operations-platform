import random
import numpy as np

#for some reason these vaiables are not accessible in the function below

#for testing purposes (this is David's part)==================================================
temperature = 293.15
battery = 100.0 #battery starts at 100%

G_Mu = 398600.4418 # Earth's Gravitational acceleration (km^3/s^2)
gravity_scale = 1.0 #at 400km in altitude gravity is reduced by about 11%
dt1 = 5 #time step size for position
dt2 = 1.0 #time step size for thermals and power
roll_rate = 2.0
pitch_rate = 1.5
yaw_rate = 10.0 # spin rates

battery_capacitor_Wh = 0.05
current_charge_wh = 10.0
battery_pct = 100.0

power_base_draw = 1.5
power_comms_draw = 3.0
solar_generation = 4.0

mass = 1.33
Cp = 900
thermal_mass = mass*Cp
A_sun = 0.01
A_total = 0.06
alpha = 0.8
epsilon = 0.8
sigma = 5.67e-8

solar_flux = 1361
T_space = 3

x = 6771.0
y = 0.0
z = 0.0 #starting position
vx = 0.0
vy = 7.67
vz = 0.0 #orbital velocity
roll = 0
pitch = 0
yaw = 0 #current angles (degrees)
count = 0

def tel_data(data:dict)-> dict:
    #do your calculations here or route to diff packets etc.
    #this is just for testing

    #currently not using any of the correction data received
    #IMPORTANT ^^^^^^^^
    
    global temperature
    global battery

    global G_Mu
    global gravity_scale
    global dt1 
    global dt2 
    global roll_rate
    global pitch_rate
    global yaw_rate

    global battery_capacitor_Wh
    global current_charge_wh
    global battery_pct 

    global power_base_draw 
    global power_comms_draw 
    global solar_generation 

    global mass 
    global Cp 
    global thermal_mass 
    global A_sun
    global A_total 
    global alpha 
    global epsilon
    global sigma 

    global solar_flux 
    global T_space

    global x 
    global y 
    global z 
    global vx 
    global vy
    global vz 
    global roll 
    global pitch 
    global yaw 
    global count 


    packet = {
        "timestamp": count,

        "packet_type": "telemetry",

        "position_km": {
        "x": x,
        "y": y,
        "z": z
        },

        "velocity_km_s": {
        "vx": vx,
        "vy": vy,
        "vz": vz
        },

        "orientation_deg": {
        "roll": roll,
        "pitch": pitch,
        "yaw": yaw
        },

        "angular_velocity_deg_s": { 
        "wx": 0, 
        "wy": 0, 
        "wz": 0 
        },

        "temperature_c": temperature,

        "battery_percent": battery
    }
    
    if battery > 10:
        battery -= 10
    else:
        battery = 100 # resets back to 100 once battery drops to 10%
    
    temperature = random.randint(10,40) #generates random number between 14 and 26 inclusive
    
    r = np.sqrt(x**2 + y**2 + z**2)
    accel_x = -G_Mu * (x/r**3)*gravity_scale
    accel_y = -G_Mu * (y/r**3)*gravity_scale
    accel_z = -G_Mu * (z/r**3)*gravity_scale

    vx = vx + (accel_x * dt1);
    vy = vy + (accel_y * dt1);
    vz = vz + (accel_z * dt1);

    x = x + (vx * dt1);
    y = y + (vy * dt1);
    z = z + (vz * dt1);

    roll = roll + (roll_rate * dt1);
    pitch = pitch + (pitch_rate * dt1);
    yaw = yaw + (yaw_rate * dt1);


    return packet