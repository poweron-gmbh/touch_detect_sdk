#!/usr/bin/env python3

"""Tests for CAN touch_detect_device"""

import serial

from .touch_detect_device import TouchDetectDevice, TouchDetectType

# Default values for serial port.
BAUDRATE = 1000000
PARITY = serial.PARITY_NONE
STOP_BITS = serial.STOPBITS_ONE
BYTE_SIZE = 8


class CanDevice(TouchDetectDevice):
    """Represents a CAN device.
    """

    def __init__(self, name: str, address: str,
                 taxels_array_size: tuple = (6, 6), baudrate: int = BAUDRATE,
                 parity: str = PARITY, stop_bits: float = STOP_BITS, byte_size: int = BYTE_SIZE):
        """Initialize CAN object.

        :param name: Name of serial port
        :type name: str
        :param address: Address of the device
        :type address: str
        :param taxels_array_size: size of the array, defaults to (6, 6)
        :type taxels_array_size: tuple, optional
        :param baudrate: Baudrate of the connection, defaults to BAUDRATE
        :type baudrate: int, optional
        :param parity: Parity of the serial connection, defaults to PARITY
        :type parity: str, optional
        :param stop_bits: amount of stopbits of the connection, defaults to STOP_BITS
        :type stop_bits: float, optional
        :param byte_size: amount of bits per byte, defaults to BYTE_SIZE
        :type byte_size: int, optional
        """

        super().__init__(name, address, TouchDetectType.CAN, taxels_array_size)

        self._port_handler = serial.Serial()
        self._port_handler.port = address
        self._port_handler.baudrate = baudrate
        self._port_handler.parity = parity
        self._port_handler.stopbits = stop_bits
        self._port_handler.bytesize = byte_size

    @property
    def port_handler(self) -> serial.Serial:
        """port_handler getter.
        """
        return self._port_handler
