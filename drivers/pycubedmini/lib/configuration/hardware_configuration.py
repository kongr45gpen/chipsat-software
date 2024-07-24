from ulab.numpy import array

HARDWARE_VERSION = "CS/02"

SUN_TYPE_TSL2561 = 1
SUN_TYPE_OPT3001 = 2
SUN_TYPE_OPT4001 = 3

IMU_TYPE_BMX160 = 1
IMU_TYPE_BNO08X = 2

if HARDWARE_VERSION == "CS/02":
    SUN_TYPE = SUN_TYPE_OPT4001
    IMU_TYPE = 0

    # SUN_XN_I2C = 3
    # SUN_XN_ADDRESS = 0x44

    # SUN_YN_I2C = 1
    # SUN_YN_ADDRESS = 0x44

    SUN_ZN_I2C = 2
    SUN_ZN_ADDRESS = 0x44

    # SUN_XP_I2C = 3
    # SUN_XP_ADDRESS = 0x45

    # SUN_YP_I2C = 1
    # SUN_YP_ADDRESS = 0x45

    SUN_ZP_I2C = 2
    SUN_ZP_ADDRESS = 0x45

    # COIL_X_I2C = 1
    # COIL_X_ADDRESS = 0x60

    # COIL_Y_I2C = 1
    # COIL_Y_ADDRESS = 0x61

    # COIL_Z_I2C = 1
    # COIL_Z_ADDRESS = 0x64

    CURRENT_I2C = 3
    CURRENT_ADDRESS = 0x40

    # IMU_I2C = 1
    # IMU_ADDRESS = 0x4B

    R_IMU2BODY = array([[-1., 0., 0.], [0., 0., -1.], [0., -1., 0.]])

else:
    raise ValueError(f"Invalid hardware version {HARDWARE_VERSION}")
