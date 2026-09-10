% === PARAMETER 3: THERMAL CONTROL SYSTEM (TCS) ===
function thermal = thermal_sim(correction)


% Author: David Ntwali, Elise Katsube
% Date: 07-Sep-2026


persistent T_kelvin sim_time

if nargin < 1
    correction = [];
end

if isempty(T_kelvin)
    T_kelvin = 293.15;
    sim_time = 0;
end

% --- TIMING CONTROLS ---
telemetry_dt = 5;       % How often data goes to the GUI
physics_dt = 1;         % How often physics updates

% CubeSat Thermal Properties (1U Aluminum Frame)
mass = 1.33;            % kg (Standard 1U mass)
Cp = 900;               % Specific heat capacity of Aluminum (J/kg*K)
thermal_mass = mass * Cp; 
A_sun = 0.01;           % Cross-sectional area facing the sun (m^2)
A_total = 0.06;         % Total surface area radiating heat out (m^2)
alpha = 0.8;            % Solar absorptivity
epsilon = 0.8;          % IR emissivity
sigma = 5.67e-8;        % Stefan-Boltzmann constant

solar_flux = 1361;      % Sun's energy at Earth's orbit (W/m^2)
T_space = 3;            % Deep space background temperature (Kelvin)
Q_internal = 1.5;       % Internal electronics heating

% --- APPLY CORRECTIONS ---
Q_control = 0;
if ~isempty(correction)
    if isfield(correction, 'heater') && correction.heater
        Q_control = Q_control + 20.0; %Watts
    end
    if isfield(correction, 'cooler') && correction.cooler 
        Q_control = Q_control - 20.0; %Watts
    end
end    

% --- PHYSICS SUB-STEPPING LOOP ---
for step = 1:telemetry_dt
    sim_time = sim_time + physics_dt; % Advance clock by 1s per loop

    % Check if in sunlight for this specific second
    if mod(sim_time, 90) < 60
        Q_sun = solar_flux * A_sun * alpha;
    else
        Q_sun = 0;
    end

    % Heat radiating out
    Q_out = epsilon * sigma * A_total * (T_kelvin^4 - T_space^4);

    % Net heat and temperature change over 1 second
    Q_net = Q_sun + Q_internal + Q_control - Q_out; 
    delta_T = (Q_net / thermal_mass) * physics_dt; 

    T_kelvin = T_kelvin + delta_T;
end

thermal.temperature_c = T_kelvin - 273.15;

end

