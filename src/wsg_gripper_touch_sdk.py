#!/usr/bin/env python3

"""SDK for gathering data from WSG gripper. In order
   to access TouchDetect information it is required to run
   a LUA script inside WSG gripper.
"""
import logging
import time

from threading import Event, Lock, Thread

import numpy as np

from .wsg_device import WsgDevice, WsgEventType
from .touch_detect_device import ConnectionStatus

# Value that represents the start of the frame.
TRANSACTION_ID = bytearray(b'\xaa\xaa')
# Value that represents the end of the frame.
PROTOCOL_ID = bytearray(b'\xaa\xbb')
# Command for reading left touch_detect
READ_LEFT_SENSOR_COMMAND = bytearray(b'\x01')
# Command for reading right touch_detect
READ_RIGHT_SENSOR_COMMAND = bytearray(b'\x02')
# Minimum size of a reponse from WSG gripper
RESPONSE_MIN_LENGTH = 9
# Update rate of the data of all the sensors in seconds.
UPDATE_RATE = 0.01
# Polynomial table for CRC16 calculation.
CRC_TABLE_CCITT16 = [
    0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
    0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
    0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
    0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
    0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
    0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
    0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
    0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
    0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
    0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
    0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
    0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
    0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
    0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
    0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
    0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
    0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
    0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
    0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
    0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
    0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
    0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
    0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
    0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
    0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
    0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
    0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
    0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
    0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
    0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
    0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
    0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0
]


class Crc16Generator():
    """This library generates CRC16 checksum calculation.
    """

    @classmethod
    def checksum_update_crc16(cls, data: bytearray, init_value: int = 0xFFFF) -> int:
        """Calculates CRC16 with 0x1021 polynomial representation.

        :param data: data being used to calculate CRC.
        :type data: bytearray
        :param init_value: initial value for CRC. Defaults to 0xFFFF.
        :type init_value: int
        :return: CRC16 generated.
        :rtype: int
        """
        crc = init_value
        data_size = len(data)
        for index in range(data_size):
            idx = (crc ^ data[index]) & 0x00FF
            crc = CRC_TABLE_CCITT16[idx] ^ (crc >> 8)
            crc &= 0xFFFF
        return crc


class WsgGripperTouchSdk:
    """This Class manages the communication with the sensors installed in
       WSG gripper.
    """

    @classmethod
    def __init__(cls):
        # Create a logger.
        cls._logger = logging.getLogger(__name__)
        # Set basic configurations for logging.
        logging.basicConfig(encoding='utf-8', level=logging.INFO)
        # Event for stopping incomming_data_thread.
        cls._stop_wsg_data_loop = Event()
        # list of devices that have to be polled for data.
        cls._device_list = []
        # Lock for internal variables.
        cls._lock = Lock()
        # Checks the status of the task for gathering data from WSG.
        cls._is_data_task_running = False
        # List of threads currently running.
        cls._thread_list = []

    @classmethod
    def __del__(cls):
        """Ensure that threads stopped and connection closed
        """
        if cls._is_data_task_running:
            cls._stop_wsg_data_loop.set()
            cls._is_data_task_running = False
        # Finish all running threads
        for thread in cls._thread_list:
            if thread.is_alive():
                thread.join()

    @classmethod
    def connect(cls, wsg_device: WsgDevice) -> Thread:
        """connects to specific WSG device.

        :param wsg_device: device to connect
        :type wsg_device: CanDevice
        :return: Reference to the thread running.
        :rtype: Thread
        """
        thread = Thread(target=cls._connect, args=(wsg_device,))
        thread.start()
        cls._thread_list.append(thread)
        return thread

    @classmethod
    def disconnect(cls, wsg_device: WsgDevice) -> Thread:
        """Disconnects WSG device.

        :param wsg_device: device to disconnect
        :type wsg_device: WsgDevice
        :return: Reference to the thread running.
        :rtype: Thread
        """
        thread = Thread(target=cls._disconnect, args=(wsg_device,))
        thread.start()
        cls._thread_list.append(thread)
        return thread

    @classmethod
    def _connect(cls, wsg_device: WsgDevice):
        """Thread that handles connection of devices.

        :param wsg_device: Device to be desconnected.
        :type wsg_device: WsgDevice
        """
        # Check if port was already opened.
        if wsg_device.connection_status == ConnectionStatus.CONNECTED:
            logging.info('Already connected to a device')
            return

        # Add device if wasn't already in the list.
        with cls._lock:
            if wsg_device not in cls._device_list:
                cls._device_list.append(wsg_device)

        # Open the port.
        try:
            wsg_device.port_handler.connect((
                wsg_device.address, wsg_device.tcp_port))
        except ConnectionRefusedError as error:
            logging.error("Could could not connect to WSG %s: %s",
                          wsg_device.name, error)
            wsg_device.fire_event(WsgEventType.ERROR_OPENING_PORT, [error])
            return False

        # Notify connection.
        wsg_device.connection_status = ConnectionStatus.CONNECTED
        wsg_device.fire_event(WsgEventType.CONNECTED)

        # Start the thread in case it wasn't running before.
        if not cls._is_data_task_running:
            cls._is_data_task_running = True
            cls._stop_wsg_data_loop.clear()
            thread = Thread(target=cls._wsg_data_task)
            thread.start()
            cls._thread_list.append(thread)

    @classmethod
    def _disconnect(cls, wsg_device: WsgDevice):
        """Thread that handles disconnection of devices.

        :param wsg_device: Device to be desconnected.
        :type wsg_device: WsgDevice
        """
        # Check if port was already closed.
        if wsg_device.connection_status == ConnectionStatus.DISCONNECTED:
            logging.info('Already disconnected')
            return

        # Remove device from the list.
        with cls._lock:
            if wsg_device in cls._device_list:
                cls._device_list.remove(wsg_device)

        # Disconnect port.
        try:
            wsg_device.port_handler.close()
        except RuntimeError as error:
            logging.error("Could not close serial port %s: %s",
                          wsg_device.name, error)
            wsg_device.fire_event(WsgEventType.ERROR_CLOSING_PORT, [error])
            wsg_device.connection_status = ConnectionStatus.CONNECTION_LOST
            return

        # Notify disconnection.
        wsg_device.connection_status = ConnectionStatus.DISCONNECTED
        wsg_device.fire_event(WsgEventType.DISCONNECTED)

        # Stop WSG thread if no device is listed for pooling.
        with cls._lock:
            if len(cls._device_list) == 0:
                cls._stop_wsg_data_loop.set()
                cls._is_data_task_running = False

    @classmethod
    def make_frame(cls, payload: bytearray) -> bytearray:
        """Creates a frame to be sent to WSG gripper.

        :param payload: data to be sent
        :type payload: bytearray
        :return: frame to sent over TCP.
        :rtype: bytearray
        """
        # Prepare header.
        frame = bytearray()
        frame += TRANSACTION_ID
        frame += PROTOCOL_ID
        payload_size = len(payload)
        frame.append(payload_size & 0xFF)
        frame.append((payload_size & 0xFF00) >> 8)

        # Calculate CRC.
        crc = Crc16Generator.checksum_update_crc16(frame)
        crc = Crc16Generator.checksum_update_crc16(payload, crc)

        # Add Payload.
        frame += payload

        # Add CRC.
        frame.append(crc & 0xFF)
        frame.append((crc & 0xFF00) >> 8)
        return frame

    @staticmethod
    def decode_frame(frame: bytes) -> bytearray:
        """Decodes incoming frame from WSG gripper.

        :param frame: Frame to decode
        :type frame: bytes
        :return: payload of the frame or None
        :rtype: bytearray
        """
        if len(frame) < RESPONSE_MIN_LENGTH:
            return None

        tid = frame[:2]
        if tid != TRANSACTION_ID:
            return None

        pid = frame[2:4]
        if pid != PROTOCOL_ID:
            return None

        payload_size = frame[4] | (frame[5] << 8)
        payload = bytearray()
        for index in range(payload_size):
            payload.append(frame[index+6])
        return payload

    @staticmethod
    def to_taxel_array(payload: bytearray, taxel_array_size: tuple) -> np.array:
        """Convert payload coming from WSG gripper into valid sensor array data.

        :param payload: data to be converted
        :type payload: bytearray
        :param taxel_array_size: size of the taxel array
        :type taxel_array_size: tuple
        :return: data converted into sensor data
        :rtype: np.array
        """
        taxel_array = np.zeros(shape=taxel_array_size, dtype=int)
        max_row = taxel_array_size[0]
        max_column = taxel_array_size[1]
        for row in range(max_row):
            for column in range(max_column):
                index = (2 * row * max_column) + (2 * column)
                value = int(payload[index] | (
                    payload[index + 1] << 8))
                taxel_array[row, column] = value
        return taxel_array

    @classmethod
    def _wsg_data_task(cls):
        """Task for handling packages from WSG gripper. 
        """
        logging.debug('WSG data task initialized')

        # Iterate until signal is sent.
        while not cls._stop_wsg_data_loop.is_set():
            with cls._lock:
                # Iterate through devices.
                for device in cls._device_list:
                    try:
                        # Calculate biggest frame.
                        n_bytes = device.taxels_array_size[0] * \
                            device.taxels_array_size[1] * 2
                        n_bytes += len(TRANSACTION_ID)
                        n_bytes += len(PROTOCOL_ID)
                        n_bytes += 4

                        # Read left sensor
                        frame = cls.make_frame(READ_LEFT_SENSOR_COMMAND)
                        device.port_handler.send(frame)
                        data = device.port_handler.recv(n_bytes)
                        if not data:
                            continue
                        payload = cls.decode_frame(data)
                        if not payload:
                            continue
                        device.taxel_array_left = cls.to_taxel_array(
                            payload, device.taxels_array_size)

                        # Read right sensor
                        frame = cls.make_frame(READ_RIGHT_SENSOR_COMMAND)
                        device.port_handler.send(frame)
                        data = device.port_handler.recv(n_bytes)
                        if not data:
                            continue
                        payload = cls.decode_frame(data)
                        if not payload:
                            continue
                        device.taxel_array_right = cls.to_taxel_array(
                            payload, device.taxels_array_size)
                        device.fire_event(WsgEventType.NEW_DATA, [
                            device.taxel_array_left, device.taxel_array_right])
                    except (RuntimeError, ConnectionAbortedError):
                        logging.error(
                            'Error getting data from gripper. Disconnecting device')
                        cls.disconnect(device)
                        continue
            time.sleep(UPDATE_RATE)

        logging.debug('WSG data task finished')
