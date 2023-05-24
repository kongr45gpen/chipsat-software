from lib.pycubed import cubesat
import time

def current_test():
    measurements = 100
    vals = [0] * measurements
    outlier_count = 0
    for i in range(measurements):
        vals[i] = cubesat.battery_current
        time.sleep(0.05)
    sum = 0
    for val in vals:
        sum += val
    avg = sum / 100
    for val in vals:
        if not ((avg - 2) <= val <= (avg + 2)):
            outlier_count += 1

    # if greater than 10% of the data points are far away from the average
    # the sensor is giving strange and possibly inaccurate readings.
    if (outlier_count >= measurements / 10):
        return (f"current was inconsistent: {outlier_count} outliers", False)

    # if you want to test on average current value that can be done here
    # if not (-0.5 <= avg <= 0.5):
    #     return (f"current did not return expected value: measurement {avg} mA", False)

    return ("passed current test", True)


def manual_test():
    for _ in range(10000):
        print(cubesat.battery_current)
        time.sleep(0.01)
    return ("test complete", True)


async def run(result_dict):
    """
    basic current sensor test to verify that the hardware is connected
    and returning reasonable values
    """
    if cubesat.current_sensor:
        print("running current tests, will take ~5 seconds ...")
        result_dict["Basic_Current_test"] = current_test()
        print("done running current test!")
    else:
        result_dict["Basic_Current_test"] = (
            "cannot test current sensor; no current sensor detected", None)
