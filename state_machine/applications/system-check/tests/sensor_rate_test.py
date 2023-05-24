import time
import statistics
from lib.pycubed import cubesat

def rate_test(sensor):
    trials = 1000
    dt_list = [0] * trials
    if sensor[1] == "IMU":
        for i in range(trials):
            s_time = time.time()
            sensor.accel
            e_time = time.time()
            dt_list[i] = s_time - e_time
    else:
        for i in range(trials):
            s_time = time.time()
            sensor.lux
            e_time = time.time()
            dt_list[i] = s_time - e_time

    worst_case = max(dt_list)
    best_case = min(dt_list)
    med_case = statistics.median(dt_list)
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
        (cubesat.sun_zn, "SUN_Z-"),
        (cubesat.sun_zp, "SUN_Z+"),
        (cubesat.imu, "IMU"),
    ]
    for (sensor, name) in sensors:
        result_dict[f"{name}_rate_test"] = rate_test(sensor)
    
    print("Done testing Sensor rates\n")
