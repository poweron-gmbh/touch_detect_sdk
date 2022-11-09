#!/usr/bin/python

"""This demo shows how to use ble_touchdetect_sdk"""

import os
import sys
import time

# This allows demo.py see modules that are one level up.
sys.path.append(os.getcwd())  # noqa
from src.ble_touch_sdk import BleTouchSdk  # noqa

# Possible returning values of the script.
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
# Amount of samples to take from device.
N_SAMPLES = 5
# Time to wait between readings.
RATE = 0.2
# Device name to connect.
BLE_DEVICE_NAME = 'PWRON1'

def main():
    # Create BLE Touch Detect.
    ble_touch_detect = BleTouchSdk()

    # Search for BLE devices.
    devices = ble_touch_detect.search_devices()
    print('Searching BLE devices ...')

    # Print devices found.
    for d in devices:
        print('Found device: ' + d.name)
        print('with MAC: ' + d.address)
    if len(devices) == 0:
        print('Search finished. No devices found')
        return EXIT_SUCCESS
    print(f'Search finished. {len(devices)} device[s] found')

    # Connect to device.
    print('Connecting to ' + BLE_DEVICE_NAME)
    result = ble_touch_detect.connect(BLE_DEVICE_NAME)
    if result:
        print('Successfully connnected to ' + BLE_DEVICE_NAME)
    else:
        print('Problem connecting to ' + BLE_DEVICE_NAME)

    for _ in range(N_SAMPLES):
        # Wait for data
        time.sleep(RATE)

        # Read data.
        data = ble_touch_detect.get_data()
        if data:
            print('Time: ' + str(data[0]))
            print('data: ' + str(data[1]))
            print('-----------------------------')

    # After finishing, disconnect.
    ble_touch_detect.disconnect()

    return EXIT_SUCCESS


if __name__ == '__main__':
    sys.exit(main())
