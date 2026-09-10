% === PARAMETER 2: ELECTRICAL POWER SYSTEM (EPS) ===
function eps = EPS_sim(correction)


% Author: David Ntwali, Elise Katsube
% Date: 07-Sep-2026


persistent sim_time current_charge_wh

if nargin < 1
    correction = [];
end

if isempty(current_charge_wh)
    current_charge_wh = 0.06;    
    sim_time = 0;
end

% --- TIMING CONTROLS ---
telemetry_dt = 5;       
physics_dt = 1;         

% Base Systems 
power_base_draw = 1.5;          
power_thermal = 0.5;            
power_payload = 0.8;            
power_attitude = 0.6;           
power_comms_draw = 3.0;         

solar_generation = 7;           
battery_capacity_wh = 0.06;     

% --- APPLY CORRECTIONS ---
if ~isempty(correction)
    if isfield(correction, 'disable_payload') && correction.disable_payload
        power_payload = 0;
    end
    if isfield(correction, 'disable_attitude_control') && correction.disable_attitude_control
        power_attitude = 0;
    end
    if isfield(correction, 'safe_mode') && correction.safe_mode
        power_base_draw = 0.2;
        power_payload = 0;
        power_thermal = 0.2;
        power_attitude = 0;
    end
    if isfield(correction, 'emergency_power') && correction.emergency_power
        power_payload = 0;
        power_attitude = 0;
        power_base_draw = power_base_draw * 0.3;
    end
end

total_draw = power_base_draw + power_payload + power_attitude + power_thermal;

% --- PHYSICS SUB-STEPPING LOOP ---
for step = 1:telemetry_dt
    sim_time = sim_time + physics_dt; % Advance clock by 1s per loop

    % Sunlight Check
    if mod(sim_time, 90) < 60
        in_sunlight = true;
        net_power = solar_generation - total_draw;
    else
        in_sunlight = false;
        net_power = -total_draw; 
    end

    % Simulate a data transmission spike every 10 seconds exactly
    if mod(sim_time, 10) == 0
        net_power = net_power - power_comms_draw;
    end

    % Convert Watts to Watt-hours for the 1-second time step
    charge_change = net_power * (physics_dt / 3600); 
    current_charge_wh = current_charge_wh + charge_change;

    % Battery Limits
    if current_charge_wh > battery_capacity_wh
        current_charge_wh = battery_capacity_wh;
    elseif current_charge_wh < 0
        current_charge_wh = 0;
    end
end

eps.time = sim_time;
eps.battery_percent = (current_charge_wh / battery_capacity_wh) * 100;
eps.power_consumption_w = net_power;
eps.in_sunlight = in_sunlight;

end
