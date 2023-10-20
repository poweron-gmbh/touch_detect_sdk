#!/usr/bin/env python3

"""This demo connects to the sensor and gets data from it.
   This version uses the SDK.
"""

import os
import sys
import time

from threading import Event

# This allows demo.py see modules that are one level up.
sys.path.append(os.getcwd())
# pylint: disable=wrong-import-position
from touch_detect_sdk.event import EventSuscriberInterface  # noqa
from touch_detect_sdk.serial_touch_detect_sdk import SerialTouchSdk  # noqa
from touch_detect_sdk.serial_device import SerialEventData, SerialEventType  # noqa
from touch_detect_sdk.serial_device import SerialDevice  # noqa
# pylint: enable=wrong-import-position

# Possible returning values of the script.
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

# Device port to connect.
SERIAL_PORT = 'COM38'

# Update rate of checking keyboard input.
LOOP_RATE_SEC = 0.010

# Events for handling communication with events.
stop_serial_data_loop = Event()

# pylint: disable=global-variable-not-assigned, too-few-public-methods


class EventSuscriber(EventSuscriberInterface):
    """Demo class that suscribes to the events raised by the SerialDevice.
    """

    def touch_detect_event(self, sender: object, earg: object):
        """This function gets called on every event.

        :param sender: identifies the device who raised the event.
        :type sender: object
        :param EventInfo: event information
        :type EventInfo: SerialEventType
        """
        global stop_serial_data_loop
        # Check if the event is valid.
        if not isinstance(earg, SerialEventData):
            print('Invalid data received from event')
            return

        if earg.type == SerialEventType.CONNECTED:
            print('Successfully connnected to ' + SERIAL_PORT)
        elif earg.type == SerialEventType.DISCONNECTED:
            print('Successfully disconnected to ' + SERIAL_PORT)
            stop_serial_data_loop.set()
        elif earg.type == SerialEventType.ERROR_OPENING_PORT:
            print('Error connecting to ' + SERIAL_PORT)
            stop_serial_data_loop.set()
        elif earg.type == SerialEventType.NEW_DATA:
            print('New data: ')
            print(earg.data)


def main():
    """Main function of the demo.
    """
    global stop_serial_data_loop

    serial_touch_detect = SerialTouchSdk()
    td_device = SerialDevice(SERIAL_PORT)

    # Only objects that inherit from EventSuscriberInterface
    # can be suscribed.
    event_suscriber = EventSuscriber()
    td_device.events += event_suscriber

    # Attempt to open the port.
    serial_touch_detect.connect(td_device)

    # Run the demo until the user presses q.
    input('Running demo. Press ENTER to quit')
    serial_touch_detect.disconnect(td_device)

    # Wait for the thread to finish.
    while not stop_serial_data_loop.is_set():
        time.sleep(LOOP_RATE_SEC)
    print('Closing demo')

    return EXIT_SUCCESS
# pylint: enable=global-variable-not-assigned, too-few-public-methods


if __name__ == '__main__':
    sys.exit(main())
