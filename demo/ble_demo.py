#!/usr/bin/python

"""This demo shows how to use ble_touchdetect_sdk"""

import os
import queue
import sys
import time

# This allows demo.py see modules that are one level up.
sys.path.append(os.getcwd())  # noqa
from touch_detect_sdk.ble_touch_sdk import BleTouchSdk
from touch_detect_sdk.ble_device import BleEventInfo, BleEventType

# Possible returning values of the script.
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
# Amount of samples to take from device.
N_SAMPLES = 5
# Time to wait between readings.
RATE = 8.0
# Device name to connect.
BLE_DEVICE_NAME = 'PWRON1'
# Queue for devices found.
DEVICE_QUEUE = None


def discovery_callback(devices: list):
    """Callback for discover devices.

    :param devices: List of devices found
    :type devices: list
    """
    global DEVICE_QUEUE

    # Print devices found.
    for device in devices:
        print('Found device: ' + device.device_id)
        print('with MAC: ' + device.address)
        if device.device_id == BLE_DEVICE_NAME:
            DEVICE_QUEUE.put(device)
    if len(devices) == 0:
        print('Search finished. No devices found')
        DEVICE_QUEUE.put(None)
        return


def event_handler(_: object, event_info: BleEventInfo):
    """This function can be suscribed to any BleTouchSdk event

    :param sender: identifies the device who raised the event.
    :type sender: object
    :param EventInfo: event information
    :type EventInfo: BleEventType
    """
    if event_info.type == BleEventType.CONNECTED:
        print('Successfully connnected to ' + BLE_DEVICE_NAME)
    elif event_info.type == BleEventType.DISCONNECTED:
        print('Successfully disconnected to ' + BLE_DEVICE_NAME)
    elif event_info.type == BleEventType.ERROR_OPENING_PORT:
        print('Error connecting to ' + BLE_DEVICE_NAME)
    elif event_info.type == BleEventType.ERROR_CLOSING_PORT:
        print('Error closing port of ' + BLE_DEVICE_NAME)
    elif event_info.type == BleEventType.NEW_DATA:
        sensor_data = event_info.data[0]
        print('New data: ')
        print(sensor_data)


def main():
    global DEVICE_QUEUE
    DEVICE_QUEUE = queue.Queue()

    # Create BLE Touch Detect.
    ble_touch_detect = BleTouchSdk()

    # Search for BLE devices.
    print('Searching BLE devices ...')
    ble_touch_detect.search_devices(discovery_callback)
    device = DEVICE_QUEUE.get()
    if not device:
        return EXIT_SUCCESS
    device.events += event_handler

    # Connect to device.
    print('Connecting to ' + BLE_DEVICE_NAME)
    ble_touch_detect.connect(device)

    time.sleep(RATE)

    # After finishing, disconnect.
    ble_touch_detect.disconnect(device)

    return EXIT_SUCCESS


if __name__ == '__main__':
    sys.exit(main())
