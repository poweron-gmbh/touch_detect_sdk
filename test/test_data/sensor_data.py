#!/usr/bin/env python3

""" This file contains sensor data for
    testing the serial touch detect SDK """

import numpy as np

# array of 16bit values that represents sensor array data from ADC.
TEST_SENSOR_DATA = bytearray(
    b'\x0001\x0002\x0003\x0004\x0005\x0006'
    b'\x0101\x0102\x0103\x0104\x0105\x0106'
    b'\x0201\x0202\x0203\x0204\x0205\x0206'
    b'\x0301\x0302\x0303\x0304\x0305\x0306'
    b'\x0401\x0402\x0403\x0404\x0405\x0406'
    b'\x0501\x0502\x0503\x0504\x0505\x0506')


# sensor array data split in pairs of 8bit.
TEST_RAW_SENSOR_DATA = bytearray(
    b'\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00\x06\x00'
    b'\x01\x01\x02\x01\x03\x01\x04\x01\x05\x01\x06\x01'
    b'\x01\x02\x02\x02\x03\x02\x04\x02\x05\x02\x06\x02'
    b'\x01\x03\x02\x03\x03\x03\x04\x03\x05\x03\x06\x03'
    b'\x01\x04\x02\x04\x03\x04\x04\x04\x05\x04\x06\x04'
    b'\x01\x05\x02\x05\x03\x05\x04\x05\x05\x05\x06\x05')

# fmt: off
# Sensor array data recovered from TEST_RAW_SENSOR_DATA
TEST_CONVERTED_TAXEL_DATA = np.array([[
    0x0001, 0x0002, 0x0003, 0x0004, 0x0005, 0x0006],
    [0x0101, 0x0102, 0x0103, 0x0104, 0x0105, 0x0106],
    [0x0201, 0x0202, 0x0203, 0x0204, 0x0205, 0x0206],
    [0x0301, 0x0302, 0x0303, 0x0304, 0x0305, 0x0306],
    [0x0401, 0x0402, 0x0403, 0x0404, 0x0405, 0x0406],
    [0x0501, 0x0502, 0x0503, 0x0504, 0x0505, 0x0506]])
# fmt: on
