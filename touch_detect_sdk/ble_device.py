#!/usr/bin/env python3

"""Tests for BLE touch_detect_device"""

import asyncio
import logging
import threading
import time

from enum import Enum, unique

from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.exc import BleakDeviceNotFoundError

from .event import Event
from .touch_detect_device import ConnectionStatus
from .touch_detect_device import TouchDetectDevice, TouchDetectType
from .touch_detect_utils import TouchDetectUtils


# Size of the Frame
BLE_FRAME_SIZE = 72

# UUID characteristic where TouchDetect sends the data.
BLE_NOTIFY_UUID = "0000fe42-8e22-4541-9d4c-21edae82ed19"

# Amount of time to to wait for data changes in data loop.
BLE_UPDATE_LOOP_TIME = 0.010


@unique
class BleEventType(Enum):
    """Represents different type of events triggered by BLE touch detect.
    """
    ERROR_CLOSING_PORT = 1
    ERROR_OPENING_PORT = 2
    CONNECTED = 3
    DISCONNECTED = 4
    NEW_DATA = 5


class BleEventInfo():
    """Encapsulates event data for BLE events.
    """

    def __init__(self, event: BleEventType, data: list = None):
        """Initialize class

        :param event: type of event triggered
        :type event: BleEventType
        :param data: relevant data for the event, defaults to None
        :type data: list, optional
        """
        self.type = event
        self.data = data


class BleDevice(TouchDetectDevice):
    """Encapsulates event data for BLE events.
    """
    # Event object
    events = Event('')

    def __init__(self, address: str, device_id: str,
                 name: str = '', taxels_array_size: tuple = (6, 6)):
        """Initialize BLE object.

        :param address: MAC Address of the device
        :type address: str, optional
        :param device_id: BLE name that identifies the device.
        :type device_id: str
        :param name: Name of the device
        :type name: str
        :param taxels_array_size: size of the sensor array, defaults to (6, 6)
        :type taxels_array_size: tuple, optional
        """
        super().__init__(address, name, TouchDetectType.BLE, taxels_array_size)

        self._port_handler = BleakClient(address)
        self._device_id = device_id
        self._logger = logging.getLogger(__name__)

        # Event for stopping incomming_data_thread.
        self.stop_notify_loop_event = threading.Event()

    @property
    def device_id(self) -> str:
        """device_id getter.
        """
        return self._device_id

    def fire_event(self, event_type: BleEventType, event_data: list = None):
        """fires the event for a particular reason.

        :param event_type: reason why the event was triggered.
        :type event_type: BleEventType
        :param event_data: useful data linked to the event, defaults to None
        :type event_data: list, optional
        """
        event_data = BleEventInfo(event_type, event_data)
        self.events(event_data)

    def notification_handler(self, _: BleakGATTCharacteristic,
                             data: bytearray):
        """Notification handler which updates the data received from device.
        """
        # Convert data into valid taxel data.
        array_data = TouchDetectUtils.to_taxel_array(
            self.taxels_array_size, data)
        # Fire event only if conversion was successful.
        if len(array_data) != 0:
            self.fire_event(BleEventType.NEW_DATA, [array_data])

    def connection_thread(self):
        """Thread that handles connection of devices.
        """
        # Set new event loop for this thread.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Open the port.
            loop.run_until_complete(self._port_handler.connect())

            # Fire event for connection.
            self.connection_status = ConnectionStatus.CONNECTED
            self.fire_event(BleEventType.CONNECTED)

            # Enable notifications.
            loop.run_until_complete(self._port_handler.start_notify(
                BLE_NOTIFY_UUID, self.notification_handler))
        except BleakDeviceNotFoundError as error:
            self._logger.error('Could could not connect to BLE device %s: %s',
                               self.name, error)
            self.fire_event(BleEventType.ERROR_OPENING_PORT, [error])
            return

        # loop for gathering new data.
        while not self.stop_notify_loop_event.is_set():
            # sleep for short period of time.
            time.sleep(BLE_UPDATE_LOOP_TIME)

        try:
            # Stop BLE notifications and disconnect from device.
            loop.run_until_complete(
                self._port_handler.stop_notify(BLE_NOTIFY_UUID))
            loop.run_until_complete(self._port_handler.disconnect())
        except RuntimeError as error:
            self._logger.error('Could not close serial port %s: %s',
                               self.name, error)
            self.fire_event(BleEventType.ERROR_CLOSING_PORT, [error])
            self.connection_status = ConnectionStatus.CONNECTION_LOST

        # Fire event for disconnection.
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.fire_event(BleEventType.DISCONNECTED)
