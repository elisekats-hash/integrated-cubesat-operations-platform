% === PARAMETER 1: KINEMATICS & ORBITAL POSITION ===
function position = position_sim(attitude_corr, orbit_corr)

persistent X Y Z vx vy vz sim_time roll pitch yaw disturbance_applied

% ============================================================
% SAFETIES
% ============================================================

if nargin < 2
    orbit_corr = [];
end

if nargin < 1
    attitude_corr = [];
end

% ============================================================
% INITIAL CONDITIONS
% ============================================================

if isempty(X)

    % Position (km)
    X = 6771.0;
    Y = 0.0;
    Z = 0.0;

    % Velocity (km/s)
    vx = 0.0;
    vy = 7.67;
    vz = 0.001;

    % Simulation time
    sim_time = 0.0;

    % Attitude (degrees)
    roll = 0.0;
    pitch = 0.0;
    yaw = 0.0;

    % Disturbance flag
    disturbance_applied = false;
end

% Make sure persistent values are doubles
X = double(X);
Y = double(Y);
Z = double(Z);

vx = double(vx);
vy = double(vy);
vz = double(vz);

sim_time = double(sim_time);

roll = double(roll);
pitch = double(pitch);
yaw = double(yaw);

% ============================================================
% TIMING
% ============================================================

telemetry_dt = 5;       % Seconds between telemetry packets
physics_dt = 0.1;       % Physics timestep
physics_steps = round(telemetry_dt / physics_dt);

sim_time = sim_time + telemetry_dt;

% ============================================================
% CONSTANTS
% ============================================================

% Earth's gravitational parameter
% km^3/s^2
G_Mu = 398600.4418;

gravity_scale = 1.0;

% ============================================================
% ATTITUDE
% ============================================================

roll_rate = 2.0;
pitch_rate = 1.5;
yaw_rate = 10.0;

% Apply reaction wheel corrections
if ~isempty(attitude_corr)

    if isfield(attitude_corr, 'wheel_x')
        roll_rate = roll_rate + double(attitude_corr.wheel_x);
    end

    if isfield(attitude_corr, 'wheel_y')
        pitch_rate = pitch_rate + double(attitude_corr.wheel_y);
    end

    if isfield(attitude_corr, 'wheel_z')
        yaw_rate = yaw_rate + double(attitude_corr.wheel_z);
    end

end

% ============================================================
% APPLY THRUSTER CORRECTION
% ============================================================
% The correction is applied ONCE per telemetry packet.
%
% This does NOT continuously force the spacecraft onto the
% desired orbit. It simply changes its velocity slightly.

if ~isempty(orbit_corr)

    if isfield(orbit_corr, 'thruster_direction') && ...
       isfield(orbit_corr, 'thruster_newtons') && ...
       isfield(orbit_corr, 'duration_ms')

        direction = char(orbit_corr.thruster_direction);

        if ~strcmp(direction, 'off')

            thrust_force = double(orbit_corr.thruster_newtons);

            % Spacecraft mass = 1.33 kg
            % N/kg = m/s^2
            % Divide by 1000 -> km/s^2
            thrust_accel = (thrust_force / 1.33) / 1000;

            % Convert milliseconds -> seconds
            thrust_duration = double(orbit_corr.duration_ms) / 1000;

            % Current velocity magnitude
            v_mag = sqrt(vx^2 + vy^2 + vz^2);

            % Prevent division by zero
            if v_mag > 0

                % Unit vector in direction of travel
                ux = vx / v_mag;
                uy = vy / v_mag;
                uz = vz / v_mag;

                % Delta-V from this burn
                delta_v = thrust_accel * thrust_duration;

                % Apply the burn ONCE
                if strcmp(direction, 'prograde')

                    vx = vx + ux * delta_v;
                    vy = vy + uy * delta_v;
                    vz = vz + uz * delta_v;

                elseif strcmp(direction, 'retrograde')

                    vx = vx - ux * delta_v;
                    vy = vy - uy * delta_v;
                    vz = vz - uz * delta_v;

                end
            end
        end
    end
end

% ============================================================
% SIMULATED ENVIRONMENTAL DISTURBANCE
% ============================================================
%
% The satellite normally follows its orbit naturally.
%
% After 30 seconds, introduce a small velocity disturbance
% ONCE. This simulates something like a small environmental
% disturbance.
%
% Navigation should detect the resulting orbital error and
% command a correction.
%
% ============================================================

if sim_time >= 30 && ~disturbance_applied

    % Small disturbance to orbital velocity
    vx = vx + 0.005;

    % Small out-of-plane disturbance
    vz = vz + 0.001;

    disturbance_applied = true;

end

% ============================================================
% PHYSICS SIMULATION
% ============================================================
%
% Gravity naturally produces the orbit.
% We use many small physics steps instead of one large step
% so the orbital trajectory remains stable.
%
% ============================================================

for step = 1:physics_steps

    % --------------------------------------------------------
    % Current radius
    % --------------------------------------------------------

    r = sqrt(X^2 + Y^2 + Z^2);

    % Prevent invalid calculations
    if r <= 0
        r = 6771.0;
    end

    % --------------------------------------------------------
    % Gravity
    % --------------------------------------------------------

    ax = -G_Mu * (X / r^3) * gravity_scale;
    ay = -G_Mu * (Y / r^3) * gravity_scale;
    az = -G_Mu * (Z / r^3) * gravity_scale;

    % Small restoring force toward orbital plane
    z_restoring_accel =  -0.000001 * Z;

    % --------------------------------------------------------
    % Atmospheric drag
    % --------------------------------------------------------
    %
    % Very small drag so the orbit slowly changes.
    %
    % This is intentionally tiny because the main purpose
    % of this simulation is to demonstrate navigation and
    % correction.
    %
    % --------------------------------------------------------

    drag_deceleration = 0.00001;

    v_mag = sqrt(vx^2 + vy^2 + vz^2);

    if v_mag > 0

        vx = vx - (vx / v_mag) * drag_deceleration * physics_dt;
        vy = vy - (vy / v_mag) * drag_deceleration * physics_dt;
        vz = vz - (vz / v_mag) * drag_deceleration * physics_dt;

    end

    % --------------------------------------------------------
    % Update velocity
    % --------------------------------------------------------

    vx = vx + ax * physics_dt;
    vy = vy + ay * physics_dt;
    vz = vz + (az + z_restoring_accel) * physics_dt;

    % --------------------------------------------------------
    % Update position
    % --------------------------------------------------------

    X = X + vx * physics_dt;
    Y = Y + vy * physics_dt;
    Z = Z + vz * physics_dt;

    % --------------------------------------------------------
    % Update attitude
    % --------------------------------------------------------

    roll = roll + roll_rate * physics_dt;
    pitch = pitch + pitch_rate * physics_dt;
    yaw = yaw + yaw_rate * physics_dt;

end

% ============================================================
% ROTATION MATRIX
% ============================================================

roll = double(roll);
pitch = double(pitch);
yaw = double(yaw);

rad_roll = deg2rad(roll);
rad_pitch = deg2rad(pitch);
rad_yaw = deg2rad(yaw);

R_x = [1, 0, 0;
       0, cos(rad_roll), -sin(rad_roll);
       0, sin(rad_roll), cos(rad_roll)];

R_y = [cos(rad_pitch), 0, sin(rad_pitch);
       0, 1, 0;
       -sin(rad_pitch), 0, cos(rad_pitch)];

R_z = [cos(rad_yaw), -sin(rad_yaw), 0;
       sin(rad_yaw), cos(rad_yaw), 0;
       0, 0, 1];

R_full = R_z * R_y * R_x;

% ============================================================
% RETURN TELEMETRY
% ============================================================

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
