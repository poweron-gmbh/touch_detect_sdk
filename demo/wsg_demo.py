#!/usr/bin/python

"""This demo shows how to use wsg_gripper_touch_sdk"""


import socket
import os
import sys
import time

sys.path.append(os.getcwd())  # noqa
# pylint: disable=wrong-import-position
from touch_detect_sdk.wsg_gripper_touch_sdk import WsgGripperTouchSdk  # noqa
from touch_detect_sdk.wsg_device import WsgDevice, WsgEventType, WsgEventData  # noqa
# pylint: enable=wrong-import-position

# Possible returning values of the script.
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

WSG_IP = '192.168.1.20'


class EventTester:
    """Handles events from WsgGripperTouchSdk.
    """

    def event_handler(self, sender: object, event_data: WsgEventData):
        """This function can be suscribed to any WsgGripperTouchSdk event

        :param sender: identifies the device who raised the event.
        :type sender: object
        :param event_data: event information
        :type event_data: WsgEventData
        """
        # Filter events only from one sensor.
        if sender.address == socket.gethostname():
            if event_data.type == WsgEventType.CONNECTED:
                print('Device connected')
            elif event_data.type == WsgEventType.DISCONNECTED:
                print('Device disconnected')
            elif event_data.type == WsgEventType.ERROR_OPENING_PORT:
                print('Error opening port')
            elif event_data.type == WsgEventType.ERROR_CLOSING_PORT:
                print('Error closing port')
            elif event_data.type == WsgEventType.NEW_DATA:
                print('New data received')


def main():
    """Main function of the demo.
    """
    uut = WsgGripperTouchSdk()
    test_device = WsgDevice(WSG_IP, '')
    tester = EventTester()
    test_device.events += tester.event_handler

    # Act
    uut.connect(test_device)

    time.sleep(1)

    uut.disconnect(test_device)

    return EXIT_SUCCESS


if __name__ == '__main__':
    sys.exit(main())
