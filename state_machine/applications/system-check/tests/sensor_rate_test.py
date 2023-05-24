import time
try:
    from ulab.numpy import array, median
except ImportError:
    from numpy import array, median
from lib.pycubed import cubesat

def sensor_rate_test(sensor, name):
    trials = 1000
    li = [0.0] * trials
    dt_list = array(li)
    if name == "IMU":
        for i in range(trials):
            s_time = time.monotonic_ns()
            _ = sensor.accel
            _ = sensor.accel
            _ = sensor.accel
            e_time = time.monotonic_ns()
            dt_list[i] = e_time - s_time
    else:
        for i in range(trials):
            s_time = time.monotonic_ns()
            _ = sensor.lux
            _ = sensor.lux
            _ = sensor.lux
            e_time = time.monotonic_ns()
            dt_list[i] = e_time - s_time
    worst_case = max(dt_list)
    best_case = min(dt_list)
    med_case = median(dt_list)
    return (f"worst case: {worst_case}, best case: {best_case}, median: {med_case}", True)

async def run(result_dict):
    """
    check the rates at which sensors are able to obtain their data
    """
    print("Testing sensor rates...\n")
    sensors = [
        (cubesat.sun_xn, "SUN_X-"),
        (cubesat.sun_xp, "SUN_X+"),
        (cubesat.sun_yn, "SUN_Y-"),
        (cubesat.sun_yp, "SUN_Y+"),
        # (cubesat.sun_zn, "SUN_Z-"),
        (cubesat.sun_zp, "SUN_Z+"),
        (cubesat.imu, "IMU"),
    ]
    for (sensor, name) in sensors:
        result_dict[f"{name}_rate_test"] = sensor_rate_test(sensor, name)

    print("Done testing Sensor rates\n")
