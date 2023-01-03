import struct
import os
try:
    from ulab.numpy import array, nan
except ImportError:
    from numpy import array, nan
from pycubed import cubesat
from state_machine import state_machine

# 3 uint8 + 1 uint16 + 11 float32
# = 49 bytes of data
# = 52 byte c struct (1 extra to align chars, 2 extra to align short)
beacon_format = 3 * 'B' + 'H' + 'f' * 11

# 6 float32
# = 24 bytes of data
system_format = 6 * 'f'

# 2 unint8
# = 4 bytes
time_format = 2 * 'H'

def beacon_packet():
    """Creates a beacon packet containing the: state index byte, f_contact and f_burn flags,
    state_error_count, boot count, battery voltage,
    CPU temperature, IMU temperature, gyro reading, mag reading,
    radio signal strength (RSSI), radio frequency error (FEI).

    This data is packed into a c struct using `struct.pack`.
    """
    state_byte = state_machine.states.index(state_machine.state)
    flags = ((cubesat.f_contact << 1) | (cubesat.f_burn)) & 0xFF
    software_error = cubesat.c_software_error
    boot_count = cubesat.c_boot
    vbatt = cubesat.battery_voltage
    cpu_temp = cubesat.temperature_cpu if cubesat.micro else nan
    imu_temp = cubesat.temperature_imu if cubesat.imu else nan
    gyro = cubesat.gyro if cubesat.imu else array([nan, nan, nan])
    mag = cubesat.magnetic if cubesat.imu else array([nan, nan, nan])
    rssi = cubesat.radio.last_rssi if cubesat.radio else nan
    fei = cubesat.radio.frequency_error if cubesat.radio else nan
    return struct.pack(beacon_format,
                       state_byte, flags, software_error, boot_count,
                       vbatt, cpu_temp, imu_temp,
                       gyro[0], gyro[1], gyro[2],
                       mag[0], mag[1], mag[2],
                       rssi, fei)

def system_packet():
    """Function for logging system data, packs this data into a
    c struct.

    includes the: lux values from each sun sensor
    """
    lux_xp = cubesat.sun_xp.lux if cubesat.sun_xp else nan
    lux_yp = cubesat.sun_yp.lux if cubesat.sun_yp else nan
    lux_zp = cubesat.sun_zp.lux if cubesat.sun_zp else nan
    lux_xn = cubesat.sun_xn.lux if cubesat.sun_xn else nan
    lux_yn = cubesat.sun_yn.lux if cubesat.sun_yn else nan
    lux_zn = cubesat.sun_zn.lux if cubesat.sun_zn else nan
    return struct.pack(system_format,
                       lux_xp, lux_yp, lux_zp,
                       lux_xn, lux_yn, lux_zn)

def time_packet(t):
    """returns a struct containing only the minutes and seconds, which are
    all that is necessary given the file name will contain the year, month
    day, hour"""

    (tm_year, tm_month, tm_day,
     tm_hour, tm_min, tm_sec,
     tm_wday, tm_yday, tm_isdst) = t
    return struct.pack(time_format,
                       tm_min, tm_sec,)

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

def unpack_beacon(bytes):
    """Unpacks the fields from the beacon packet packed by `beacon_packet`
    """

    (state_byte, flags, software_error, boot_count,
     vbatt, cpu_temp, imu_temp,
     gyro0, gyro1, gyro2,
     mag0, mag1, mag2,
     rssi, fei,) = struct.unpack(beacon_format, bytes)

    gyro = array([gyro0, gyro1, gyro2])
    mag = array([mag0, mag1, mag2])

    return {"state_index": state_byte,
            "contact_flag": bool(flags & (0b1 << 1)),
            "burn_flag": bool(flags & (0b1 << 0)),
            "software_error_count": software_error,
            "boot_count": boot_count,
            "battery_voltage": vbatt,
            "cpu_temperature_C": cpu_temp,
            "imu_temperature_C": imu_temp,
            "gyro": gyro,
            "mag": mag,
            "RSSI_dB": rssi,
            "FEI_Hz": fei,
            }


def unpack_system(bytes):
    (lux_xp, lux_yp, lux_zp,
     lux_xn, lux_yn, lux_zn) = struct.unpack(system_format, bytes)
    return {"lux_xp": lux_xp,
            "lux_yp": lux_yp,
            "lux_zp": lux_zp,
            "lux_xn": lux_xn,
            "lux_yn": lux_yn,
            "lux_zn": lux_zn,
            }

def unpack_time(bytes):
    (tm_min, tm_sec) = struct.unpack(time_format, bytes)
    return {"minutes": tm_min,
            "seconds": tm_sec
            }

def unpack_telemetry(bytes):
    t = unpack_time(bytes[:4])
    beacon = unpack_beacon(bytes[4:56])
    system = unpack_system(bytes[56:80])
    return {"datetime": t,
            "beacon": beacon,
            "system": system,
            }
