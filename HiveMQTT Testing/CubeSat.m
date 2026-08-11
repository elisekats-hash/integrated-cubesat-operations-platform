% === COMBINED DATA SIMULATION ===
function telemetry = CubeSat(correction) 

persistent packet_num

% ================= INITIALIZATION =================
if isempty(packet_num)
    packet_num = 0;
end

packet_num = packet_num + 1;

% ================= CORRECTIONS ====================
% Safely extract corrections to pass to the sub-functions
thermal_corr = [];
power_corr = [];
attitude_corr = [];
orbit_corr = [];                        % This the one I'm unsure

% 1. The Syntax Fix: Safely check if it's a correction packet
if nargin > 0 && isfield(correction, 'packet_type')
    if strcmp(correction.packet_type, 'correction') || correction.packet_type == "correction"

        % 2. Route the Python JSON fields safely
        if isfield(correction, 'thermal')
            thermal_corr = correction.thermal;
        end
        if isfield(correction, 'power')
            power_corr = correction.power;
        end
        if isfield(correction, 'reaction_wheels')
            attitude_corr = correction.reaction_wheels;
        end
        if isfield(correction, 'thrusters')
            orbit_corr = correction.thrusters;
        end
    end
end

% ================= RUN SIMULATIONS ================
% Pass the extracted corrections into our newly updated modular functions
position = position_sim(attitude_corr, orbit_corr);
thermal = thermal_sim(thermal_corr);
power = EPS_sim(power_corr);

% ================= BUILD TELEMETRY ================
telemetry.packet_type = "telemetry";
telemetry.packet_num = packet_num;

telemetry.time = position.time;

telemetry.position_km.x = position.x;
telemetry.position_km.y = position.y;
telemetry.position_km.z = position.z;

telemetry.velocity_km_s.vx = position.vx;
telemetry.velocity_km_s.vy = position.vy;
telemetry.velocity_km_s.vz = position.vz;

% Pulling actual live attitude data instead of hardcoded 0s
telemetry.orientation_deg.roll = position.roll;
telemetry.orientation_deg.pitch = position.pitch;
telemetry.orientation_deg.yaw = position.yaw;

telemetry.angular_velocity_deg_s.wx = position.wx;
telemetry.angular_velocity_deg_s.wy = position.wy;
telemetry.angular_velocity_deg_s.wz = position.wz;

telemetry.temperature_c = thermal.temperature_c;
telemetry.battery_percent = power.battery_percent;

end