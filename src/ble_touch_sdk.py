#!/usr/bin/env python3

import asyncio
import logging
import os
import time
import sys

from bleak import BleakClient, BleakScanner, BleakError
from threading import Thread, Event, Lock

from .ble_device import BleDevice  # noqa

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
BLE_UPDATE_LOOP_TIME_LONG = 1
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
        self._logger = None
        # self._logger = logging.getLogger(__name__)
        # @todo actual logging implementation
        if logfile:
            logging.basicConfig(
                filename=logfile, encoding='utf-8', level=logging.INFO)

        # List of devices found
        self._devices_found = []
        # Event loop for running incomming data callback.
        self._loop_ble_data = None
        # Queue for sharing data.
        self._incomming_data_queue = None
        # Timestamp for calculating time between readings.
        self._timestamp_start = time.time()
        # Thread for processing incomming data.
        self._incomming_data_thread = None
        # Lock for protecting _ble_client
        self._data_thread_lock = Lock()
        # Events for controlling
        self._stop_notify_loop_event = Event()
        self._stop_acquisition_event = Event()
        self._exit_ready_event = Event()
        # MAC of the device that is going to be connected.
        self._device_mac = None
        # General TD Device which is connected
        self._target_device: BleDevice = None
        self._stop_acquisition_event.set()

    def __del__(self):
        """Deconstrutor to ensure threads stopped and connection closed
        """
        if self._incomming_data_thread and self._incomming_data_thread.is_alive():
            self._stop_notify_loop_event.set()
            while self._incomming_data_thread.is_alive():
                if self._exit_ready_event.wait(timeout=2.0):
                    break

    def search_devices(self):
        """Search BLE devices nearby

        :return: list of BLE devices
        :rtype: list
        """
        self._devices_found.clear()
        asyncio.run(self._discover())
        return self._devices_found

    def connect_by_dev(self, device: BleDevice):
        """Connect to BLE device"""
        self._target_device = device
        result = self.connect(self._target_device.name)
        with self._data_thread_lock:
            self._target_device.connected = result
        return result

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
            self._stop_notify_loop_event.clear()
            self._incomming_data_thread = Thread(
                target=self._ble_data_thread)
            self._incomming_data_thread.start()

            # Wait for BLE connection.
            con_feedback = asyncio.run(self._wait_for_connection())
            self._target_device.connection_lost = False
            return con_feedback
        except Exception as e:
            logging.error(e)
            logging.error('Error connecting from BLE device')
            return False

    def disconnect(self):
        """Disconnects BLE TouchDetect

        :return: true if disconnection was successful, False otherwise
        :rtype: boolean
        """
        if not self._target_device.connected:
            return False

        try:
            # Send the signal to stop the thread.
            self._stop_notify_loop_event.set()
            # Wait until connection thread finishes.
            while self._target_device.acquisition_running:
                time.sleep(BLE_UPDATE_LOOP_TIME)
            self._stop_notify_loop_event.set()
            while self._incomming_data_thread.is_alive():
                time.sleep(BLE_UPDATE_LOOP_TIME)
            self._target_device.connected = False
        except Exception as e:
            logging.error(e)
            logging.error('Error disconnecting from BLE device')
            return False
        logging.info('Disconnected from BLE device')
        return True

    def start_acquisition(self):
        if self._target_device.acquisition_running:
            logging.error('Acquisition already running on BLE Device')
            return
        self._stop_acquisition_event.clear()

    def stop_acquisition(self):
        if not self._target_device.acquisition_running:
            return
        self._stop_acquisition_event.set()

    def single_acquisition(self):
        if self._target_device.connected:
            self.start_acquisition()
            time.sleep(0.5)
            d = self.get_data()
            self.stop_acquisition()
            return d

    def get_data(self):
        """Get latests data sent from BLE device

        :return: list of tuples with format: (timestamp, data)
        :rtype: list
        """
        if not self._is_connected():
            logging.info('Data thread not running. Call connect() first.')
            return None
        data = None
        with self._data_thread_lock:
            if self._incomming_data_queue.empty():
                logging.info('No data from BLE device.')
            else:
                data = self._incomming_data_queue.get_nowait()
                self._incomming_data_queue.task_done()
        return data

    def _is_connected(self):
        """Check if BLE device is connected.

        :return: True if SDK is connected to device, False otherwise.
        :rtype: boolean
        """        
        with self._data_thread_lock:
            if self._incomming_data_thread and\
                    self._incomming_data_thread.is_alive() and\
                    self._target_device.connected:
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
        await asyncio.sleep(1)
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
            name = device.name if device.name else 'Unknown'
            ble_device = BleDevice(name, device.address)
            self._devices_found.append(ble_device)

    def _ble_data_thread(self):
        """Start loop for gathering data from BLE device
        """
        self._loop_ble_data = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop_ble_data)
        self._incomming_data_queue = asyncio.Queue(DATA_QUEUE_SIZE)
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
        with self._data_thread_lock:
            if self._incomming_data_queue.full():
                while self._incomming_data_queue.full():
                    self._incomming_data_queue.get_nowait()
                    self._incomming_data_queue.task_done()
            self._incomming_data_queue.put_nowait((timestamp, data_values))

    async def _ble_loop(self):
        """Loop for getting notifications for getting data from BLE.
        """
        # Set notification callbacks for BLE data.
        ble_client = BleakClient(self._device_mac)
        try:
            await ble_client.connect()
        except BleakError as err:
            logging.info(err)
            logging.info('Connection not confirmed')
        else:
            with self._data_thread_lock:
                self._target_device.connected = True
            await ble_client.get_services()
            ble_client.set_disconnected_callback(self._disconnect_callback)

        while not self._stop_notify_loop_event.is_set():
            try:
                if self._target_device.acquisition_running and self._stop_acquisition_event.is_set():
                    # Stop BLE notifications.
                    self._target_device.acquisition_running = False
                    await ble_client.stop_notify(BLE_NOTIFY_UUID)
                    await asyncio.sleep(BLE_UPDATE_LOOP_TIME)

                if not self._target_device.acquisition_running and not self._stop_acquisition_event.is_set():
                    # Start BLE notifications
                    await ble_client.start_notify(BLE_NOTIFY_UUID, self._ble_data_callback)
                    await asyncio.sleep(BLE_UPDATE_LOOP_TIME)
                    self._target_device.acquisition_running = True
                # sleep for short period of time.
            except BleakError as err:
                self._error_handling(err)

            await asyncio.sleep(BLE_UPDATE_LOOP_TIME)

        if self._target_device.connected:  # End of Thread - when Connection ends
            try:
                await ble_client.disconnect()
            except BleakError as err:
                logging.info(err)

        logging.info('Finished Thread Loop - inactive now')

    def _disconnect_callback(self, device_client: BleakClient):
        logging.info(f'Disconnect callback at {device_client.address=}')
        self._shutdown_cleaning()
        self._target_device.connection_lost = True

    def _error_handling(self, err: BleakError):
        logging.info('BLE ERROR')
        self._shutdown_cleaning()

    def _shutdown_cleaning(self):
        logging.info(f'{self._target_device.name=}')
        logging.info('Shutting down thread and clean class runtime variables')
        self._stop_notify_loop_event.set()
        self._stop_acquisition_event.set()
        self._target_device.connected = False
        self._target_device.acquisition_running = False
