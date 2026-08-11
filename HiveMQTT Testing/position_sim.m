% === PARAMETER 1: KINEMATICS & ORBITAL POSITION ===
function position = position_sim(attitude_corr, orbit_corr)

persistent X Y Z vx vy vz sim_time roll pitch yaw

% Safeties to prevent MATLAB from crashing if corrections aren't sent
if nargin < 2
    orbit_corr = [];
end
if nargin < 1
    attitude_corr = [];
end

if isempty(X)
    X = 6771;
    Y = 0;
    Z = 0;

    vx = 0;
    vy = 7.67;
    vz = 0;

    sim_time = 0;

    roll = 0;
    pitch = 0;
    yaw = 0;
end

dt = 5;             % Time step size (seconds)
% ^^^ still working on an alternative variant for realistic analysis
sim_time = sim_time + dt;         % Mission clock (seconds)

G_Mu = 398600.4418;       % Earth's Gravitational acceleration (km^3/s^2)
gravity_scale = 1.0;      % At 400 KM in altitude gravity is reduced by about 11%

% --- NEW: Full 3-Axis Attitude Variables ---
roll_rate = 2; pitch_rate = 1.5; yaw_rate = 10; % Spin rates (degrees per second AKA angular velocity)

% --- APPLY CORRECTIONS ---
if ~isempty(attitude_corr)
    % Elise's Python controller sends wheel_x, wheel_y, wheel_z
    roll_rate = roll_rate + attitude_corr.wheel_x;
    pitch_rate = pitch_rate + attitude_corr.wheel_y;
    yaw_rate = yaw_rate + attitude_corr.wheel_z;
end

if ~isempty(orbit_corr)
    % Elise's code sends orbit_corr.thruster_direction ("prograde", "retrograde", "off")
    % This part is new, will have to test and see if it works
    % and orbit_corr.thruster_newtons (0 to 100)
    
    if ~strcmp(orbit_corr.thruster_direction, 'off')
        
        % 1. Find the current direction of movement (Velocity Unit Vector)
        v_mag = sqrt(vx^2 + vy^2 + vz^2); % Current total speed
        ux = vx / v_mag; % X direction
        uy = vy / v_mag; % Y direction
        uz = vz / v_mag; % Z direction
        
        % 2. Calculate Acceleration from Thruster (a = F/m)
        % CubeSat mass is lwk light (1.33 kg). 
        % Gotta scale Elise's 0-100 magnitude down so it doesn't break orbit instantly.
        thrust_force = double(orbit_corr.thruster_newtons) * 0.001; % Assuming milliNewtons for realism
        thrust_accel = thrust_force / 1.33; 
        
        % Calculate change in velocity (Delta v = a * dt)
        delta_v = thrust_accel * dt;
        
        % 3. Apply Prograde (speed up) or Retrograde (slow down)
        if strcmp(orbit_corr.thruster_direction, 'prograde')
            vx = vx + (ux * delta_v);
            vy = vy + (uy * delta_v);
            vz = vz + (uz * delta_v);
        elseif strcmp(orbit_corr.thruster_direction, 'retrograde')
            vx = vx - (ux * delta_v);
            vy = vy - (uy * delta_v);
            vz = vz - (uz * delta_v);
        end
    end
end    

% 1. Calculate Gravity's Acceleration 
r = sqrt(X^2 + Y^2 + Z^2);                   % Distance from Earth's center (km)

ax = -G_Mu * (X / r^3) * gravity_scale; % Gravitational pull on X
ay = -G_Mu * (Y / r^3) * gravity_scale; % Gravitational pull on Y
az = -G_Mu * (Z / r^3) * gravity_scale; % Gravitational pull on Z

% 2. Update Velocity (Apply the acceleration)
vx = vx + (ax * dt);
vy = vy + (ay * dt);
vz = vz + (az * dt);

% 3. Update Orbital Position (Move using the new velocity)
X = X + (vx * dt);
Y = Y + (vy * dt);
Z = Z + (vz * dt);

% 4. Update Angles
roll = roll + (roll_rate * dt);
pitch = pitch + (pitch_rate * dt);
yaw = yaw + (yaw_rate * dt);

% --- Change angles into Rad --- 
rad_roll = deg2rad(str2double(roll));
rad_pitch = deg2rad(str2double(pitch));
rad_yaw = deg2rad(str2double(yaw));

R_x = [1, 0, 0; 0, cos(rad_roll), -sin(rad_roll); 0, sin(rad_roll), cos(rad_roll)];
R_y = [cos(rad_pitch), 0, sin(rad_pitch); 0, 1, 0; -sin(rad_pitch), 0, cos(rad_pitch)];
R_z = [cos(rad_yaw), -sin(rad_yaw), 0; sin(rad_yaw), cos(rad_yaw), 0; 0, 0, 1];

% Combine them (Z * Y * X is the standard sequence)
R_full = R_z * R_y * R_x;

% --- End Result ---
position.time = sim_time;

position.x = X;
position.y = Y;
position.z = Z;

position.vx = vx;
position.vy = vy;
position.vz = vz;

position.roll = roll;
position.pitch = pitch;
position.yaw = yaw;

position.wx = roll_rate;
position.wy = pitch_rate;
position.wz = yaw_rate;

position.R_full = R_full;

end
