from pycubed import cubesat
from state_machine import state_machine
import struct
import os

def beacon_packet(task):
    """Creates a beacon packet containing the: CPU temp, IMU temp, gyro, acceleration, magnetic, and state byte.
    The state byte is the index of the current state in the alphabetically ordered state list.
    This data is packed into a c struct using `struct.pack`.

    If no IMU is attached it returns a packet of 0s.
    """
    if not cubesat.imu:
        task.debug('IMU not initialized')
        return bytes([0, 0, 0, 0, 0])

    cpu_temp = cubesat.temperature_cpu
    imu_temp = cubesat.temperature_imu
    gyro = cubesat.gyro
    acc = cubesat.acceleration
    mag = cubesat.magnetic
    state_byte = state_machine.states.index(state_machine.state)
    format = 'b' + 'f' * 11  # 1 char + 11 floats
    return struct.pack(format,
                       state_byte, cpu_temp, imu_temp,
                       gyro[0], gyro[1], gyro[2],
                       acc[0], acc[1], acc[2],
                       mag[0], mag[1], mag[2])


def human_time_stamp():
    """Returns a human readable time stamp in the format: 'year.month.day hour:min'
    Gets the time from the RTC."""
    t = cubesat.rtc.datetime
    return f'{t.tm_year}.{t.tm_mon}.{t.tm_mday}.{t.tm_hour}:{t.tm_min}:{t.tm_sec}'

def try_mkdir(path):
    """Tries to make a directory at the given path.
    If the directory already exists it does nothing."""
    try:
        os.mkdir(path)
    except Exception:
        pass
