#!/usr/bin/env python3

import asyncio
import logging
import os
import time
import sys

from bleak import BleakClient, BleakScanner
from threading import Thread, Event, Lock

sys.path.append(os.path.dirname(__file__))  # noqa
from ble_device import BleDevice  # noqa

# Amount of time to wait for connection
WAIT_CONNECTION_TIMEOUT = 5.0
# UUID characteristic where TouchDetect sends the data.
BLE_NOTIFY_UUID = "0000fe42-8e22-4541-9d4c-21edae82ed19"
# Format for logging.
LOGGING_FORMAT = '%(asctime)s %(user)-8s %(message)s'

# Amount of time to wait for discover new devices.
BLE_DISCOVER_TIMEOUT = 2.0
# Amount of time to to wait for data changes in data loop.
BLE_UPDATE_LOOP_TIME = 0.010
# Minimal amount of time to wait for connection.
BLE_CHECK_CONNECTION_SEC = 0.05
# Size of the queue for incomming data.
DATA_QUEUE_SIZE = 1

class BleTouchSdk:
    """This Class manages the communication with BLE devices.
    """

    def __init__(self, logfile: str = None):
        """Initialize BLE TouchDetect SDK instance

        :param logfile: URL to the nasm installer, defaults to None
        :type logfile: str, optional
        """
        # List of devices found
        self._devices_found = []
        # Event loop for running incomming data callback.
        self._loop_ble_data = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop_ble_data)
        # Queue for sharing data.
        self._incomming_data_queue = asyncio.Queue(DATA_QUEUE_SIZE)
        # Timestamp for calculating time between readings.
        self._timestamp_start = time.time()
        # Thread for processing incomming data.
        self._incomming_data_thread = None

        # Lock for protecting _ble_client
        self._data_thread_lock = Lock()
        # Event for stopping incomming_data_thread.
        self._stop_notify_loop_event = Event()
        # Status of the BLE connection
        self._device_connected = False
        # MAC of the device that is going to be connected.
        self._device_mac = None

        if logfile:
            logging.basicConfig(
                filename=logfile, encoding='utf-8', level=logging.INFO)
        else:
            logging.basicConfig(level=logging.INFO)

    def search_devices(self):
        """Search BLE devices nearby

        :return: list of BLE devices
        :rtype: list
        """
        self._devices_found.clear()
        asyncio.run(self._discover())
        return self._devices_found

    def connect(self, device_name: str):
        """Connect to BLE device

        :param device_name: name of the BLE device to find
        :type device_name: str
        :return: true if connection was successful, False otherwise.
        :rtype: boolean
        """
        # Run discover if didn't run before.
        if not self._devices_found:
            asyncio.run(self._discover())
        # Get the MAC of the BLE device.
        self._device_mac = self._get_mac(device_name)

        if not self._device_mac:
            logging.warning('Device was not found')
            return False

        if self._is_connected():
            logging.warning('Already connected to a device')
            return False

        try:
            # Start thread for getting data from BLE device.
            self._incomming_data_thread = Thread(
                target=self._ble_data_thread)
            self._incomming_data_thread.start()

            # Wait for BLE connection.
            return asyncio.run(self._wait_for_connection())

        except Exception as e:
            logging.error(e)
            logging.error('Error connecting from BLE device')
            return False

    def disconnect(self):
        """Disconnects BLE TouchDetect

        :return: true if disconnection was successful, False otherwise
        :rtype: boolean
        """
        if not self._is_connected():
            logging.info('Data thread not running. Call connect() first')
            return False

        try:
            # Send the signal to stop the thread.
            self._stop_notify_loop_event.set()
            # Wait until connection thread finishes.
            while self._incomming_data_thread.is_alive():
                time.sleep(BLE_UPDATE_LOOP_TIME)
        except Exception as e:
            logging.error(e)
            logging.error('Error disconnecting from BLE device')
            return False
        logging.info('Disconnected from BLE device')
        return True

    def get_data(self):
        """Get latests data sent from BLE device

        :return: list of tuples with format: (timestamp, data)
        :rtype: list
        """
        if not self._is_connected():
            logging.info('Data thread not running. Call connect() first.')
            return None
        if self._incomming_data_queue.empty():
            logging.info('No data from BLE device.')
            return None
        return self._incomming_data_queue.get_nowait()

    def _is_connected(self):
        """Check if BLE device is connected.

        :return: True if SDK is connected to device, False otherwise.
        :rtype: boolean
        """        
        with self._data_thread_lock:
            if self._incomming_data_thread and self._incomming_data_thread.is_alive() and self._device_connected:
                return True
            return False

    def _get_mac(self, device_name: str):
        """Returns the MAC address of device_name.
        For running this function you should call first
        _discover().

        :param device_name: name of the BLE device to find
        :type device_name: str
        :return: string with the MAC address of device_name, None
            otherwise
        :rtype: str
        """
        if not self._devices_found:
            logging.error('No devices found. Call search_devices() first')
            return None

        for device in self._devices_found:
            if device.name == device_name:
                return device.address

    async def _wait_for_connection(self):
        """Blocks execution of thread until connection is reached.

        :return: True if connection is successful, False otherwise.
        :rtype: boolean
        """        
        n_loops = int(WAIT_CONNECTION_TIMEOUT / BLE_CHECK_CONNECTION_SEC)
        for _ in range(n_loops):
            if self._is_connected():
                return True
            await asyncio.sleep(BLE_CHECK_CONNECTION_SEC)
        return False

    async def _discover(self):
        """Search BLE devices nearby.
        """
        async with BleakScanner() as scanner:
            await asyncio.sleep(BLE_DISCOVER_TIMEOUT)
        for device in scanner.discovered_devices:
            ble_device = BleDevice(device.name, device.address)
            self._devices_found.append(ble_device)

    def _ble_data_thread(self):
        """Start loop for gathering data from BLE device
        """
        self._loop_ble_data.run_until_complete(self._ble_loop())

    def _ble_data_callback(self, sender, data):
        """Callback for getting BLE data.
        """
        # Process incomming data and send it to queue.
        data_length = int(len(data) / 2)
        data_values = []
        for index in range(data_length):
            data_values.append(
                int(data[index * 2] * 256 + data[index * 2 + 1]))
        timestamp = time.time() - self._timestamp_start
        # Empty queue before adding new element.
        if self._incomming_data_queue.full():
            while self._incomming_data_queue.full():
                self._incomming_data_queue.get_nowait()
        self._incomming_data_queue.put_nowait((timestamp, data_values))

    async def _ble_loop(self):
        """Loop for getting notifications for getting data from BLE.
        """
        # Set notification callbacks for BLE data.
        ble_client = BleakClient(self._device_mac)
        await ble_client.connect()
        await ble_client.start_notify(BLE_NOTIFY_UUID, self._ble_data_callback)
        self._device_connected = True
        while not self._stop_notify_loop_event.is_set():
            # sleep for short period of time.
            await asyncio.sleep(BLE_UPDATE_LOOP_TIME)
        # Stop BLE notifications.
        await ble_client.stop_notify(BLE_NOTIFY_UUID)
        await ble_client.disconnect()
