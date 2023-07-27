#!/usr/bin/env python3

"""Describes a device connected to WSG gripper"""

from enum import Enum, unique
import socket
import numpy as np

from .event import Event
from .touch_detect_device import TouchDetectDevice, TouchDetectType

# Default port for WSG connection.
TCP_PORT = 1000


@unique
class WsgEventType(Enum):
    """Represents different type of events triggered by WSG touch detect.
    """
    ERROR_CLOSING_PORT = 1
    ERROR_OPENING_PORT = 2
    CONNECTED = 3
    DISCONNECTED = 4
    NEW_DATA = 5


class WsgEventData():
    """Encapsulates event data for CAN events.
    """

    def __init__(self, event: WsgEventType, data: list = None):
        """Initialize class

        :param event: type of event triggered
        :type event: CanEventType
        :param data: relevant data for the event, defaults to None
        :type data: list, optional
        """
        self.type = event
        self.data = data


class WsgDevice(TouchDetectDevice):
    """Represents a WSG device.
    """
    # Event object
    events = Event('')

    def __init__(self, address: str, name: str = None,
                 taxels_array_size: tuple = (6, 6)):
        """Initialize WSG object.

        :param address: Address of the device
        :type address: str
        :param name: Name of serial port
        :type name: str
        :param taxels_array_size: size of the array, defaults to (6, 6)
        :type taxels_array_size: tuple, optional
        """

        super().__init__(address, name, TouchDetectType.TCP, taxels_array_size)

        self._port_handler = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._taxels_array_left = np.zeros(shape=self._taxels_array_size)
        self._taxels_array_right = np.zeros(shape=self._taxels_array_size)

        # Public variables
        self.tcp_port = TCP_PORT

    @property
    def port_handler(self) -> socket.socket:
        """port_handler getter.
        """
        with self._lock:
            return self._port_handler

    @property
    def taxels_array_left(self) -> socket.socket:
        """taxel_array_left getter.
        """
        with self._lock:
            return self._taxels_array_left

    @taxels_array_left.setter
    def taxels_array_left(self, data: list) -> None:
        """set taxel_array_left.

        :param data: new data array.
        :type data: np.array
        """
        with self._lock:
            self._taxels_array_left = data

    @property
    def taxels_array_right(self) -> socket.socket:
        """taxel_array_right getter.
        """
        with self._lock:
            return self._taxels_array_right

    @taxels_array_right.setter
    def taxels_array_right(self, data: list) -> None:
        """set taxel_array_right.

        :param data: new data array.
        :type data: np.array
        """
        with self._lock:
            self._taxels_array_right = data

    def fire_event(self, event_type: WsgEventType, event_data: list = None):
        """Fires the event of the class.

        :param event_type: reason why the event was triggered.
        :type event_type: WsgEventType
        :param event_data: useful data linked to the event, defaults to None
        :type event_data: list, optional
        """
        event_data = WsgEventData(event_type, event_data)
        self.events(event_data)
