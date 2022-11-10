#!/usr/bin/env python3

from .touch_detect_device import TouchDetectDevice, TouchDetectModel


class BleDevice(TouchDetectDevice):
    """Represents a BLE device. 
    """

    def __init__(self, name: str = None, address: str = None):
        super().__init__(name=name, address=address, model=TouchDetectModel.BLE)
        """Initialize BLE TouchDetect SDK instance.

        :param name: URL to the nasm installer, defaults to None
        :type name: str, optional
        :param address:  MAC address of the BLE device, defaults to None
        :type address: str, optional
        """
