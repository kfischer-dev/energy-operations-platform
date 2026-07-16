from time_grid import generate_time_grid
from datetime import datetime, time
from profiles import calculate_solar_power_kw, time_to_minutes


def simulate_solar_power_grid():

    # Simulation time
    start_time = datetime(2026, 7, 15, 10, 0, 0)
    end_time =  datetime(2026, 7, 15, 14, 0, 0)
    interval_minutes = 15

    simulation_time_grid  = generate_time_grid(start_time, end_time, interval_minutes)

    # Preliminary Asset and Profile Parameter
    rated_power_kw = 80000
    sunrise_time = time(6, 30, 0)
    sunrise_minutes = time_to_minutes(sunrise_time)
    sunset_time = time(18, 30, 0)
    sunset_minutes = time_to_minutes(sunset_time)
    peak_time = time(12, 30, 0)
    peak_minutes = time_to_minutes(peak_time)

    power_list = []

    for timestamp in simulation_time_grid:
        time_minutes = time_to_minutes(timestamp.time())

        active_power_kw = calculate_solar_power_kw(
            rated_power_kw=rated_power_kw,
            time_minutes=time_minutes,
            sunrise_minutes=sunrise_minutes,
            peak_minutes=peak_minutes,
            sunset_minutes=sunset_minutes,
        )
        power_list.append(round(active_power_kw, 2))
        print(f"{timestamp}: {active_power_kw:.2f} kW")
    
    print(power_list)