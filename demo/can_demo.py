#!/usr/bin/python

"""This demo shows how to use can_touchdetect_sdk"""


import os
import sys
import time

# This allows demo.py see modules that are one level up.
sys.path.append(os.getcwd())
# pylint: disable=wrong-import-position
from touch_detect_sdk.can_touch_sdk import CanTouchSdk  # noqa
from touch_detect_sdk.can_device import CanEventData, CanEventType  # noqa
# pylint: enable=wrong-import-position

# Possible returning values of the script.
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
# Amount of samples to take from device.
N_SAMPLES = 100
# Time to wait between readings.
RATE = 1
# Device name to connect.
CAN_DEVICE_NAME = 'COM18'


def event_handler(sender: object, event_data: CanEventData):
    """This function is called when a new event is raised by the device.
    """
    # Filter events only from one sensor.
    if sender.address == CAN_DEVICE_NAME:
        if event_data.type == CanEventType.CONNECTED:
            print('Device connected')
        elif event_data.type == CanEventType.DISCONNECTED:
            print('Device disconnected')
        elif event_data.type == CanEventType.ERROR_CLOSING_PORT:
            print('Error closing port')
        elif event_data.type == CanEventType.NEW_DATA:
            print('New data')
            print(event_data.data)


def main():
    """Main function of the demo.
    """
    # Create new instance of CanTouchSDK.
    can_touch_detect = CanTouchSdk()

    # Search for BLE devices.
    print('Searching Can devices ...')
    devices = can_touch_detect.find_devices()
    device_to_connect = None

    # Print devices found.
    for device in devices:
        print('found device in port ' + device.address)
        # If device matches with the device we want to connect, then
        # we store the device name
        if device.address == CAN_DEVICE_NAME:
            device_to_connect = device
    if len(devices) == 0:
        print('Search finished. No devices found')
        return EXIT_SUCCESS

    # Check if device was found.
    if not device_to_connect:
        print(f'There is no device in {CAN_DEVICE_NAME}')
        return EXIT_SUCCESS

    # Subscribe to events.
    device_to_connect.events += event_handler

    # Connect
    print('Connecting to ' + CAN_DEVICE_NAME)
    result = can_touch_detect.connect(device_to_connect)
    if result:
        print('Successfully connnected to ' + CAN_DEVICE_NAME)
    else:
        print('Problem connecting to ' + CAN_DEVICE_NAME)
        return EXIT_SUCCESS

    # Sleep and get data.
    time.sleep(5)

    # After finishing, disconnect.
    can_touch_detect.disconnect(device_to_connect)

    return EXIT_SUCCESS


if __name__ == '__main__':
    sys.exit(main())
