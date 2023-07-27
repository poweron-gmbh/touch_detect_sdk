#!/usr/bin/env python3

"""This demo connects to the sensor and gets data from it.
   This version uses the SDK.
"""

import os
import sys
import time

from threading import Event

import keyboard

# This allows demo.py see modules that are one level up.
sys.path.append(os.getcwd())  # noqa
from touch_detect_sdk.serial_device import SerialDevice, SerialEventType, SerialEventData
from touch_detect_sdk.serial_touch_detect_sdk import SerialTouchSdk


# Possible returning values of the script.
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

# Device port to connect.
SERIAL_PORT = 'COM26'

# Update rate of the loop for handling the communication.
LOOP_RATE_SEC = 0.010

stop_serial_data_loop = Event()

# pylint: disable=global-variable-not-assigned
def event_handler(_: object, event_info: SerialEventData):
    """This function can be suscribed to any Serial TouchDetect event

    :param sender: identifies the device who raised the event.
    :type sender: object
    :param EventInfo: event information
    :type EventInfo: SerialEventType
    """
    global stop_serial_data_loop
    if event_info.type == SerialEventType.CONNECTED:
        print('Successfully connnected to ' + SERIAL_PORT)
    elif event_info.type == SerialEventType.DISCONNECTED:
        print('Successfully disconnected to ' + SERIAL_PORT)
        stop_serial_data_loop.set()
    elif event_info.type == SerialEventType.ERROR_OPENING_PORT:
        print('Error connecting to ' + SERIAL_PORT)
        stop_serial_data_loop.set()
    elif event_info.type == SerialEventType.NEW_DATA:
        sensor_data = event_info.data[0]
        print('New data: ')
        print(sensor_data)


def main():
    """Main function of the demo.
    """
    global stop_serial_data_loop
    serial_touch_detect = SerialTouchSdk()
    td_device = SerialDevice(SERIAL_PORT)
    td_device.events += event_handler

    # Attempt to open the port.
    serial_touch_detect.connect(td_device)

    # Run the demo until the user presses q.
    print('Running demo. Press q to quit')
    while not stop_serial_data_loop.is_set():
        time.sleep(LOOP_RATE_SEC)
        if keyboard.is_pressed('q'):
            serial_touch_detect.disconnect(td_device)
            break

    # Wait for the thread to finish.
    while not stop_serial_data_loop.is_set():
        time.sleep(LOOP_RATE_SEC)
    print('Closing demo')

    return EXIT_SUCCESS
# pylint: enable=global-variable-not-assigned

if __name__ == '__main__':
    sys.exit(main())
