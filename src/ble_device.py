#!/usr/bin/env python3
class BleDevice:
    """Represents a BLE device. 
    """

    def __init__(self, name: str = None, address: str = None):
        """Initialize BLE TouchDetect SDK instance.

        :param name: URL to the nasm installer, defaults to None
        :type name: str, optional
        :param address:  MAC address of the BLE device, defaults to None
        :type address: str, optional
        """
        self._name = name
        self._address = address

    @property
    def name(self):
        """Name of the BLE device

        :return: name of the device
        :rtype: str
        """
        return self._name

    @property
    def address(self):
        """Address of the BLE device

        :return:  MAC address of the BLE device
        :rtype: str
        """
        return self._address
