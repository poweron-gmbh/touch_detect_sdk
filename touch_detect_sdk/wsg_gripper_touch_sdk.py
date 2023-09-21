#!/usr/bin/env python3

"""SDK for gathering data from WSG gripper. In order
   to access TouchDetect information it is required to run
   a LUA script inside WSG gripper.
"""
import logging
import time

from threading import Event, Lock, Thread

from .wsg_device import WsgDevice, WsgEventType
from .touch_detect_device import ConnectionStatus
from .touch_detect_utils import TouchDetectUtils

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
        :type wsg_device: WsgDevice
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
            logging.error("Could could not connect to WSG at %s: %s",
                          wsg_device.address, error)
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
            logging.error("Could not close port %s: %s",
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
        crc = TouchDetectUtils.checksum_update_crc16(frame)
        crc = TouchDetectUtils.checksum_update_crc16(payload, crc)

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

    @classmethod
    def _wsg_data_task(cls):
        """Task for handling packages from WSG gripper.
        """
        logging.debug('WSG data task initialized')

        # Iterate until signal is set.
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
                        device.taxel_array_left = \
                            TouchDetectUtils.to_taxel_array(
                                device.taxels_array_size, payload)

                        # Read right sensor
                        frame = cls.make_frame(READ_RIGHT_SENSOR_COMMAND)
                        device.port_handler.send(frame)
                        data = device.port_handler.recv(n_bytes)
                        if not data:
                            continue
                        payload = cls.decode_frame(data)
                        if not payload:
                            continue
                        device.taxel_array_right = \
                            TouchDetectUtils.to_taxel_array(
                                device.taxels_array_size, payload)
                        device.fire_event(WsgEventType.NEW_DATA, [
                            device.taxel_array_left, device.taxel_array_right])
                    except (RuntimeError, ConnectionAbortedError):
                        logging.error(
                            '''Error getting data from gripper.
                            Disconnecting device''')
                        cls.disconnect(device)
                        continue
            time.sleep(UPDATE_RATE)

        logging.debug('WSG data task finished')
