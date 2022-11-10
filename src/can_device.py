#!/usr/bin/env python3
import serial

from .touch_detect_device import TouchDetectDevice, TouchDetectModel


class CanDevice(TouchDetectDevice):
    """Represents a CAN UART device.
    """

    def __init__(self, name: str = None, address: str = None,
                 start_id_can: int = 0):
        super().__init__(name=name, address=address, model=TouchDetectModel.CAN)
        """Initialize CAN TouchDetect SDK instance.

        :param name: URL to the nasm installer, defaults to None
        :type name: str, optional
        :param address:  Address of the CAN device, defaults to None
        :type address: str, optional
        """
        self._name = name
        self._address = address
        self._baudrate = 1000000
        self._parity = 0
        self._stopbit = 1
        self._bytesize = 8

    @property
    def can_id(self):
        return self._can_id

    @property
    def baudrate(self):
        """Baudrate of the serial interface

        :return:  Baudrate of the CAN devices serial communication
        :default: 1000000
        :rtype: int
        """
        return self._baudrate

    @property
    def parity(self):
        """Parity of the serial interface

        :return:  Parity of the CAN devices serial communication
        :default: 0  | indicates pyserial.PARITY_NONE
        :rtype: int
        """
        return self._parity

    @property
    def stopbit(self):
        """Stopbit of the serial interface

        :return:  Stopbit of the CAN devices serial communication
        :default: 1 | indicates pyserial.STOPBITS_ONE
        :rtype: int
        """
        return self._stopbit

    @property
    def bytesize(self):
        """Bytesize of the serial interface

        :return:  Bytesize of the CAN devices serial communication
        :default: 8
        :rtype: int
        """
        return self._bytesize


