#!/usr/bin/env python3

"""Tests for BLE touch_detect_device"""

from bleak import BleakClient

from .touch_detect_device import TouchDetectDevice, TouchDetectType


class BleDevice(TouchDetectDevice):
    """Represents a BLE device.
    """

    def __init__(self, name: str, address: str, taxels_array_size: tuple = (6, 6)):
        """Initialize BLE object.

        :param name: Name of the device, defaults to None
        :type name: str, optional
        :param address: MAC Address of the device, defaults to None
        :type address: str, optional
        :param taxels_array_size: size of the sensor array, defaults to (6, 6)
        :type taxels_array_size: tuple, optional
        """
        super().__init__(name, address, TouchDetectType.BLE, taxels_array_size)
        self._ble_handler = BleakClient(address)

    @property
    def ble_handler(self) -> BleakClient:
        """port_handler getter.
        """
        return self._ble_handler
