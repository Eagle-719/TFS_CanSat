import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# ---------------------------
# Simulation parameters
# ---------------------------
m = 0.3  # mass (kg)
F_thrust_max = 20e-3  # maximum thrust 👎
rho = 1.225  # air density (kg/m^3)
A = 0.05  # effective horizontal area (m^2)
Cd = 1  # drag coefficient (horizontal)
descent_speed = 5.5  # vertical descent speed (m/s)
initial_altitude = 1000.0  # starting altitude (m)
T_total = initial_altitude / descent_speed  # total descent time (s) ~250 s
target = np.array([0.0, 0.0])  # landing target at origin

dt = 0.1  # simulation timestep (10 ms)


def drag_force(v, wind):
    v_rel = v - wind
    speed_rel = np.linalg.norm(v_rel)
    if speed_rel == 0:
        return np.array([0.0, 0.0])
    Fd = 0.5 * rho * A * Cd * speed_rel ** 2
    return -Fd * (v_rel / speed_rel)


def generate_wind_series(T_total, dt, tau=1.0, sigma=0.0):
    N = int(T_total / dt) + 1
    t_arr = np.linspace(0, T_total, N)
    wind_series = np.zeros((N, 2))
    angle = np.random.uniform(0, 2 * np.pi)
    mag = np.random.uniform(2, 4)
    initial_wind = np.array([mag * np.cos(angle), mag * np.sin(angle)])
    wind_series[0] = initial_wind
    for i in range(N - 1):
        noise = np.random.randn(2)
        wind_series[i + 1] = wind_series[i] + dt * (-wind_series[i] / tau) + sigma * np.sqrt(dt) * noise
        wind_series[i + 1] = np.clip(wind_series[i + 1], -4, 4)
    return t_arr, wind_series


def wind_func_factory(t_arr, wind_series):
    def wind_func(t):
        wx = np.interp(t, t_arr, wind_series[:, 0])
        wy = np.interp(t, t_arr, wind_series[:, 1])
        return np.array([wx, wy])

    return wind_func


def dynamics_with_control(state, t, u, wind_func):
    pos = state[:2]
    vel = state[2:]
    wind = wind_func(t)
    F_drag = drag_force(vel, wind)
    acc = (u + F_drag) / m
    return np.array([vel[0], vel[1], acc[0], acc[1]])


def rk4_step(state, t, dt, u, wind_func):
    k1 = dynamics_with_control(state, t, u, wind_func)
    k2 = dynamics_with_control(state + 0.5 * dt * k1, t + 0.5 * dt, u, wind_func)
    k3 = dynamics_with_control(state + 0.5 * dt * k2, t + 0.5 * dt, u, wind_func)
    k4 = dynamics_with_control(state + dt * k3, t + dt, u, wind_func)
    return state + (dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)


def simulate_fall_wind_acc(initial_state, target, dt=0.01):
    t = 0.0
    t_list = [t]
    state_list = [initial_state.copy()]
    control_list = [np.array([0.0, 0.0])]
    acc_cmd_list = [np.array([0.0, 0.0])]

    wind_t, wind_series = generate_wind_series(T_total, dt, tau=50.0, sigma=0.2)
    wind_func = wind_func_factory(wind_t, wind_series)

    current_state = initial_state.copy()
    prev_velocity = initial_state[2:].copy()

    while t < T_total:
        r_curr = current_state[:2]
        v_curr = current_state[2:]

        if t == 0:
            a_meas = np.array([0.0, 0.0])
        else:
            a_meas = (v_curr - prev_velocity) / dt

        T_rem = (initial_altitude - descent_speed * t) / descent_speed
        if T_rem < 0.1:
            T_rem = 0.1
        a_des = 2 * (target - r_curr - v_curr * T_rem) / (T_rem ** 2)
        a_cmd = a_des - 0.1 * a_meas
        u = m * a_cmd
        norm_u = np.linalg.norm(u)
        u = u / norm_u * F_thrust_max
        new_state = rk4_step(current_state, t, dt, u, wind_func)
        t += dt
        t_list.append(t)
        state_list.append(new_state.copy())
        control_list.append(u.copy())
        acc_cmd_list.append(a_cmd.copy())
        prev_velocity = v_curr.copy()
        current_state = new_state.copy()

    return (np.array(t_list), np.array(state_list),
            np.array(control_list), np.array(acc_cmd_list),
            wind_t, wind_series)


num_tests = 10
trajectories = []
for i in range(num_tests):
    initial_pos = np.random.uniform(-500, 500, size=2)
    initial_vel = np.array([0.0, 0.0])
    initial_state = np.concatenate([initial_pos, initial_vel])

    t_arr, states, controls, acc_cmd, wind_t, wind_series = simulate_fall_wind_acc(initial_state, target, dt=dt)
    trajectories.append((t_arr, states, controls, acc_cmd, wind_t, wind_series, initial_pos))

fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

wind_scale = 50
u_scale = 2000
arrow_interval = 250

for t_arr, states, controls, acc_cmd, wind_t, wind_series, init in trajectories:
    x = states[:, 0]
    y = states[:, 1]

    z = initial_altitude - descent_speed * t_arr

    ax.plot(x, y, z, label=f"Start=({init[0]:.0f},{init[1]:.0f})")
    ax.scatter(init[0], init[1], initial_altitude, color='k', s=30)

    for idx in range(0, len(t_arr), arrow_interval):
        pos = np.array([x[idx], y[idx], z[idx]])
        current_time = t_arr[idx]
        wx = np.interp(current_time, wind_t, wind_series[:, 0])
        wy = np.interp(current_time, wind_t, wind_series[:, 1])
        wind_vec = np.array([wx, wy, 0])
        ax.quiver(pos[0], pos[1], pos[2],
                  wind_vec[0] * wind_scale, wind_vec[1] * wind_scale, 0,
                  arrow_length_ratio=0.2, color='c')
        u_vec = controls[idx]
        ax.quiver(pos[0], pos[1], pos[2],
                  u_vec[0] * u_scale, u_vec[1] * u_scale, 0,
                  arrow_length_ratio=0.2, color='m')

ax.scatter(target[0], target[1], 0, color='r', s=100, marker='*', label="Target")
ax.set_xlabel("x (m)")
ax.set_ylabel("y (m)")
ax.set_zlabel("Altitude (m)")
ax.set_title("3D Trajectories with Wind-Compensating Control\n(Based on Current State Acceleration)")
ax.invert_zaxis()
ax.legend(loc='upper right', fontsize='small', bbox_to_anchor=(1.2, 1))
plt.tight_layout()
plt.show()

fig2, ax2 = plt.subplots(figsize=(10, 6))
for t_arr, states, controls, acc_cmd, wind_t, wind_series, init in trajectories:
    distances = np.linalg.norm(states[:, :2], axis=1)
    ax2.plot(t_arr, distances, label=f"Start=({init[0]:.0f},{init[1]:.0f})")

ax2.set_xlabel("Time (s)")
ax2.set_ylabel("Distance from Goal (m)")
ax2.set_title("Distance from Goal vs. Time")
ax2.grid(True)
ax2.legend(fontsize='small')
plt.tight_layout()
plt.show()