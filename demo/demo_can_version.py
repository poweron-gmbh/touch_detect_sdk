#!/usr/bin/python

"""This demo shows how to use can_touchdetect_sdk"""

import os
import sys
import time

# This allows demo.py see modules that are one level up.
sys.path.append(os.getcwd())  # noqa
from can_touchdetect_sdk import CanTouchSdk
from can_touchdetect_sdk import CanDevice

# Possible returning values of the script.
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
# Amount of samples to take from device.
N_SAMPLES = 100
# Time to wait between readings.
RATE = 1
# Device name to connect.
CAN_DEVICE_NAME = 'COM3'

def main():
    # Create BLE Touch Detect.
    can_touch_detect = CanTouchSdk()
    can_device = CanDevice()

    # Search for BLE devices.
    devices = can_touch_detect.search_devices()
    print('Searching Can devices ...')

    # Print devices found.
    for d in devices:
        print('Found device: ' + d.name)
        print('with Adress: ' + d.address)
    if len(devices) == 0:
        print('Search finished. No devices found')
        return EXIT_SUCCESS
    print(f'Search finished. {len(devices)} device[s] found')

    # Connect to device.
    print('Connecting to ' + CAN_DEVICE_NAME)
    result = can_touch_detect.connect(CAN_DEVICE_NAME)
    if result:
        print('Successfully connnected to ' + CAN_DEVICE_NAME)
    else:
        print('Problem connecting to ' + CAN_DEVICE_NAME)

    pre_wait_cycle = 0
    # Wait for data acquisition started and synced
    while not can_touch_detect.acquisition_running():
        pre_wait_cycle += 1
        time.sleep(RATE)
        print('wait for sync | cycle {0} of 10'.format(pre_wait_cycle))
        if pre_wait_cycle == 10:
            break
    if can_touch_detect.acquisition_running():
        print('synced')
        # time.sleep(RATE)
        for _ in range(N_SAMPLES):
            if can_touch_detect.data_available():
                # Read data.
                data = can_touch_detect.get_data()
                if data:
                    print('Time: ' + str(data[0]))
                    #data_h = ''.join('\\x{:02x}'.format(byte) for byte in data[1])
                    print(data[1])
                    #print('data: ' + str(data_h))
                    print('-----------------------------')
            else:
                _ -= 1
    else:
        print('Sync Error')

    # After finishing, disconnect.
    can_touch_detect.disconnect()

    return EXIT_SUCCESS


if __name__ == '__main__':
    sys.exit(main())
