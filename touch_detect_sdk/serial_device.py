#!/usr/bin/env python3

"""Describes a serial touch detect Device"""

from enum import Enum, unique

import numpy as np
import serial  # pyserial

from .event import Event
from .touch_detect_device import TouchDetectDevice, TouchDetectType

# Default values for serial port.
DEFAULT_BAUDRATE = 115200
PARITY = serial.PARITY_NONE
STOP_BITS = serial.STOPBITS_ONE
BYTE_SIZE = 8
DEFAULT_TIMOUT_SEC = 0.5


@unique
class SerialEventType(Enum):
    """Represents different type of events triggered by Serial touch detect.
    """
    ERROR_OPENING_PORT = 2
    CONNECTED = 3
    DISCONNECTED = 4
    NEW_DATA = 5


@unique
class SerialDeviceStatus(Enum):
    """Represents different type of events triggered by Serial touch detect.
    """
    IDLE = 0
    REQUEST_SENT = 1


class SerialEventData():
    """Encapsulates event data for serial events.
    """

    def __init__(self, event: SerialEventType, data: np.array = None):
        """Initialize class

        :param event: type of event triggered
        :type event: SerialEventType
        :param data: relevant data for the event, defaults to None
        :type data: numpy array, optional
        """
        self.type = event
        self.data = data


class SerialDevice(TouchDetectDevice):
    """Represents a Serial device.
    """
    # Event object
    events = Event('')

    def __init__(self, address: str = None, name: str = None,
                 taxels_array_size: tuple = (6, 6)):
        """Initialize Serial object.

        :param address: Address of the device
        :type address: str
        :param name: Name of serial port
        :type name: str
        :param taxels_array_size: size of the array, defaults to (6, 6)
        :type taxels_array_size: tuple, optional
        """
        super().__init__(address, name, TouchDetectType.SERIAL,
                         taxels_array_size)

        # Public variables
        # Amount of connections performed that failed.
        self.timeout_count = 0
        # Status of the communication with the device.
        self.status = SerialDeviceStatus.IDLE

        # Private variables
        self._port_handler = serial.Serial()
        self._port_handler.port = address
        self._port_handler.baudrate = DEFAULT_BAUDRATE
        self._port_handler.parity = PARITY
        self._port_handler.stopbits = STOP_BITS
        self._port_handler.bytesize = BYTE_SIZE
        self._port_handler.timeout = DEFAULT_TIMOUT_SEC

    @TouchDetectDevice.address.setter
    def address(self, data: str) -> str:
        """Set address in touch detect.

        :param data: new data array.
        :type data: np.array
        """
        self._port_handler.port = data
        with self._lock:
            self._address = data

    @property
    def port_handler(self) -> serial.Serial:
        """port_handler getter.
        """
        with self._lock:
            return self._port_handler

    def fire_event(self, event_type: SerialEventType,
                   event_data: np.array = None):
        """Fires the event of the class.

        :param event_type: reason why the event was triggered.
        :type event_type: SerialEventType
        :param event_data: useful data linked to the event, defaults to None
        :type event_data: numpy array, optional
        """
        event_data = SerialEventData(event_type, event_data)
        self.events(event_data)
