#!/usr/bin/env python3

"""SDK for gathering data from BLE TouchDetect.
"""
import asyncio

from threading import Thread
from typing import Callable

from bleak import BleakScanner

from .ble_device import BleDevice
from .event import Event
from .touch_detect_device import ConnectionStatus

# Search time in Seconds
BLE_DISCOVERY_TIME = 2.0


class BleTouchSdk:
    """This Class manages the communication with BLE devices.
    """

    # Event for searching devices.
    search_devices_event = Event('')

    @classmethod
    def __init__(cls):
        # List of threads currently running.
        cls._thread_list = []

    @classmethod
    def __del__(cls):
        """Ensure that threads stopped and connection closed
        """
        # Finish all running threads
        for thread in cls._thread_list:
            if thread.is_alive():
                thread.join()

    @classmethod
    def search_devices(cls, callback: Callable[[list], None]) -> Thread:
        """Runs the thread for looking for new devices.

        :return: Reference to the thread running.
        :rtype: Thread
        """
        thread = Thread(target=cls._discover, args=(callback,))
        thread.start()
        cls._thread_list.append(thread)
        return thread

    @classmethod
    def connect(cls, ble_device: BleDevice) -> Thread:
        """connects to specific BLE device.

        :param ble_device: device to connect
        :type ble_device: CanDevice
        :return: Reference to the thread running.
        :rtype: Thread
        """
        # Check if device was already connected.
        if ble_device.connection_status == ConnectionStatus.CONNECTED:
            return None

        thread = Thread(target=ble_device.connection_thread)
        thread.start()
        cls._thread_list.append(thread)
        return thread

    @classmethod
    def disconnect(cls, ble_device: BleDevice):
        """Disconnects BLE device.

        :param ble_device: device to disconnect
        :type ble_device: BLEDevice
        :return: Reference to the thread running.
        :rtype: Thread
        """
        # Check if device was already disconnected.
        if ble_device.connection_status == ConnectionStatus.DISCONNECTED:
            return

        # Disconnect port.
        ble_device.stop_notify_loop_event.set()

    @classmethod
    def _discover(cls, callback: Callable[[list], None]):
        """Search BLE devices.
        """
        ble_devices = []

        # Set new event loop for this thread.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Search devices and populate list.
        devices_info = loop.run_until_complete(
            BleakScanner.discover(BLE_DISCOVERY_TIME))
        for device_info in devices_info:
            if device_info.name:
                ble_device = BleDevice(device_info.address, device_info.name)
                ble_devices.append(ble_device)
        callback(ble_devices)
