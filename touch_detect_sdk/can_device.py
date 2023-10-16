#!/usr/bin/env python3

"""Describes a CAN Device"""

from enum import Enum, unique
import serial

from .event import Event
from .touch_detect_device import TouchDetectDevice, TouchDetectType

# Default values for serial port.
BAUDRATE = 1000000
PARITY = 'N'
STOP_BITS = 1
BYTE_SIZE = 8
DEFAULT_TIMOUT_SEC = 0.5


@unique
class CanEventType(Enum):
    """Represents different type of events triggered by CAN touch detect.
    """
    ERROR_CLOSING_PORT = 1
    ERROR_OPENING_PORT = 2
    CONNECTED = 3
    DISCONNECTED = 4
    NEW_DATA = 5


class CanEventData():
    """Encapsulates event data for CAN events.
    """

    def __init__(self, event: CanEventType, data: list = None):
        """Initialize class

        :param event: type of event triggered
        :type event: CanEventType
        :param data: relevant data for the event, defaults to None
        :type data: list, optional
        """
        self.type = event
        self.data = data


class CanDevice(TouchDetectDevice):
    """Represents a CAN device.
    """
    # Event object
    events = Event('')

    def __init__(self, address: str, name: str = '',
                 taxels_array_size: tuple = (6, 6), baudrate: int = BAUDRATE,
                 parity: str = PARITY, stop_bits: float = STOP_BITS,
                 byte_size: int = BYTE_SIZE):
        """Initialize CAN object.

        :param address: Address of the device
        :type address: str
        :param name: Name of serial port
        :type name: str
        :param taxels_array_size: size of the array, defaults to (6, 6)
        :type taxels_array_size: tuple, optional
        :param baudrate: Baudrate of the connection, defaults to BAUDRATE
        :type baudrate: int, optional
        :param parity: Parity of the serial connection, defaults to PARITY
        :type parity: str, optional
        :param stop_bits: stopbits of the connection, defaults to STOP_BITS
        :type stop_bits: float, optional
        :param byte_size: amount of bits per byte, defaults to BYTE_SIZE
        :type byte_size: int, optional
        """

        super().__init__(address, name, TouchDetectType.CAN, taxels_array_size)

        self._port_handler = serial.Serial()
        self._port_handler.port = address
        self._port_handler.baudrate = baudrate
        self._port_handler.parity = parity
        self._port_handler.stopbits = stop_bits
        self._port_handler.bytesize = byte_size
        self._port_handler.timeout = DEFAULT_TIMOUT_SEC

        self._data_buffer = []

    @property
    def port_handler(self) -> serial.Serial:
        """port_handler getter.
        """
        with self._lock:
            return self._port_handler

    @property
    def data_buffer(self) -> list:
        """data_buffer getter.
        """
        with self._lock:
            return self._data_buffer

    @data_buffer.setter
    def data_buffer(self, data: list) -> None:
        """set data buffer.

        :param data: new data array.
        :type data: np.array
        """
        with self._lock:
            self._data_buffer = data

    def fire_event(self, event_type: CanEventType, event_data: list = None):
        """Fires the event of the class.

        :param earg: parameters to send through the event, defaults to None
        :event_type earg: object, optional
        """
        event_data = CanEventData(event_type, event_data)
        self.events(event_data)
