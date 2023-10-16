#!/usr/bin/env python3

"""SDK for managing communication with serial touch detect.
"""
import logging
import time
from threading import Event, Lock, Thread

from serial.serialutil import SerialException

# pylint: disable=no-name-in-module
from yahdlc import (
    FRAME_ACK,
    FRAME_DATA,
    frame_data,
    get_data,
)
# pylint: enable=no-name-in-module

from .serial_device import SerialDevice, SerialEventType, SerialDeviceStatus
from .touch_detect_device import ConnectionStatus
from .touch_detect_utils import TouchDetectUtils

# Update rate of the data of all the sensors in seconds.
TIMEOUT = 0.8
MAX_TIMEOUT_COUNT = 3
UPDATE_RATE = 0.040
MIN_PACKAGE_SIZE = 6

SERIAL_DATA_FRAME_SIZE = 72

FRAME_START_BYTE = bytes(b'\x7e')
FRAME_END_BYTE = bytes(b'\x7e')
DEVICE_ADDRESS = bytes(b'\xff')
SERIAL_COMMAND_GET_DATA = bytes(b'\x01')


class SerialTouchSdk:
    """This Class manages the communication with the sensors installed in
       serial TouchDetect
    """

    @classmethod
    def __init__(cls):
        # Create a logger.
        cls._logger = logging.getLogger(__name__)
        # Set basic configurations for logging
        logging.basicConfig(encoding='utf-8', level=logging.INFO)
        # Event for stopping the data thread
        cls._stop_serial_data_loop = Event()
        # list of devices that have to be polled for data
        cls._device_list = []
        # Lock for internal variables
        cls._lock = Lock()
        # Flag for the status of the task for gathering data from sensors
        cls._is_data_task_running = False
        # List of threads currently running
        cls._thread_list = []

    @classmethod
    def __del__(cls):
        """Ensure that threads stopped and connection closed
        """
        if cls._is_data_task_running:
            cls._stop_serial_data_loop.set()
            cls._is_data_task_running = False
        # Finish all running threads
        for thread in cls._thread_list:
            if thread.is_alive():
                thread.join()

    @classmethod
    def connect(cls, serial_device: SerialDevice) -> Thread:
        """connects to specific SerialTouchDetect device.

        :param serial_device: device to connect
        :type serial_device: SerialDevice
        :return: Reference to the thread running
        :rtype: Thread
        """
        thread = Thread(target=cls._connect, args=(serial_device,))
        thread.start()
        cls._thread_list.append(thread)
        return thread

    @classmethod
    def disconnect(cls, serial_device: SerialDevice) -> Thread:
        """Disconnects SerialTouchDetect device

        :param serial_device: device to disconnect
        :type serial_device: SerialDevice
        :return: Reference to the thread running
        :rtype: Thread
        """
        thread = Thread(target=cls._disconnect, args=(serial_device,))
        thread.start()
        cls._thread_list.append(thread)
        return thread

    @classmethod
    def _connect(cls, serial_device: SerialDevice):
        """Thread that handles connection of devices.

        :param serial_device: Device to be desconnected.
        :type serial_device: SerialDevice
        """
        # Check if port was already opened.
        if serial_device.connection_status == ConnectionStatus.CONNECTED:
            logging.info('Already connected')
            return

        # Add device if wasn't already in the list.
        with cls._lock:
            if serial_device not in cls._device_list:
                cls._device_list.append(serial_device)

        # Open the port.
        try:
            serial_device.port_handler.open()
        except SerialException as error:
            logging.error("Could could not connect to Device %s: %s",
                          serial_device.name, error)
            serial_device.fire_event(
                SerialEventType.ERROR_OPENING_PORT, [error])
            return

        # Notify connection.
        serial_device.connection_status = ConnectionStatus.CONNECTED
        serial_device.fire_event(SerialEventType.CONNECTED)

        # Start the thread in case it wasn't running before.
        if not cls._is_data_task_running:
            cls._is_data_task_running = True
            cls._stop_serial_data_loop.clear()
            thread = Thread(target=cls._serial_data_task)
            thread.start()
            cls._thread_list.append(thread)

    @classmethod
    def _disconnect(cls, serial_device: SerialDevice):
        """Thread that handles disconnection of devices.

        :param serial_device: Device to be desconnected.
        :type serial_device: SerialDevice
        """
        # Check if port was already closed.
        if serial_device.connection_status == ConnectionStatus.DISCONNECTED:
            logging.info('Already disconnected')
            return

        # Remove device from the list.
        with cls._lock:
            if serial_device in cls._device_list:
                cls._device_list.remove(serial_device)

        # Disconnect port.
        serial_device.port_handler.close()

        # Notify disconnection.
        serial_device.connection_status = ConnectionStatus.DISCONNECTED
        serial_device.fire_event(SerialEventType.DISCONNECTED)

        # Stop communiation thread if no device is listed for pooling.
        with cls._lock:
            if len(cls._device_list) == 0:
                cls._stop_serial_data_loop.set()
                cls._is_data_task_running = False

    @classmethod
    def _process_frame(cls, serial_device: SerialDevice, frames: list[bytes]):
        for frame in frames:
            data, frame_type, _ = get_data(frame)

            # Reply ACK with another ACK
            if frame_type == FRAME_ACK:
                reply = frame_data('', FRAME_ACK, 5)
                serial_device.port_handler.write(reply)
                serial_device.status = SerialDeviceStatus.IDLE
                serial_device.timeout_count = 0
                return
            # Ignore non-valid packages.
            elif (frame_type == FRAME_DATA and
                    len(data) == SERIAL_DATA_FRAME_SIZE):
                serial_device.taxels_array = TouchDetectUtils.to_taxel_array(
                    serial_device.taxels_array_size, data)
            else:
                cls._logger.warning(
                    'Received payload with wrong size. Ignoring package.')

    @classmethod
    def _poll_for_incoming_data(cls,
                                serial_device: SerialDevice) -> list[bytes]:
        """Process all the data comming from serial port. Filters the
        data into HDLC frames.

        :param serial_device: Device to get the data from.
        :type serial_device: SerialDevice
        :return: Incomming HDLC frame, None otherwise.
        :rtype: bytes
        """
        # Read data when there is a package available
        if serial_device.port_handler.in_waiting < MIN_PACKAGE_SIZE:
            return None

        # Read all the data available from serial port
        serial_data = serial_device.port_handler.read_all()

        result = []
        # Find the start of the frame
        start_index = serial_data.find(FRAME_START_BYTE)
        if start_index == -1:
            # There is no starting frame, ignore package.
            return None
        elif start_index != 0:
            # Erase all the bytes that are before the start of the package
            serial_data = serial_data[start_index:]

        # If there are two consecutive start frames (end of one frame and
        # start of the next one).
        # Remove the end frame
        if len(serial_data) != 1 and serial_data[1] == FRAME_START_BYTE:
            serial_data.pop(0)

        start_frame_index = 0
        end_frame_index = 0
        while len(serial_data) != end_frame_index:
            # Find the end of the frame. Ignore the start frame
            end_frame_index = serial_data.find(
                FRAME_END_BYTE, start_frame_index + 1)
            if end_frame_index == -1:
                # There is starting frame but there is no end frame.
                # Wait for the restof the data.
                return None
            # There is a complete frame detected. create a new byte
            # array with the frame. Increment the end frame index
            # to include the end frame byte.
            end_frame_index += 1
            new_frame = bytes(serial_data[start_frame_index:end_frame_index])
            # Set the start index of the next frame.
            start_frame_index = end_frame_index
            # Check if address is correct
            if new_frame[1] == DEVICE_ADDRESS[0]:
                result.append(new_frame)
        return result

    @classmethod
    def _serial_data_task(cls):
        """Task for handling packages from Serial Touch Detect.
        """
        logging.debug('Serial data task initialized')

        # Iterate until signal is set.
        while not cls._stop_serial_data_loop.is_set():
            with cls._lock:
                # Iterate through devices.
                for device in cls._device_list:
                    try:
                        if device.status == SerialDeviceStatus.IDLE:
                            data_request_frame = frame_data(
                                SERIAL_COMMAND_GET_DATA, FRAME_DATA, 1)
                            device.port_handler.write(data_request_frame)
                            device.status = SerialDeviceStatus.REQUEST_SENT
                            device.timeout_count = 0
                        elif device.status == SerialDeviceStatus.REQUEST_SENT:
                            # get new frame
                            new_data = cls._poll_for_incoming_data(device)
                            # If no data is available,
                            # then wait another iteration.
                            if not new_data:
                                device.timeout_count += UPDATE_RATE
                                # Check if the device is in timeout.
                                if device.timeout_count >= TIMEOUT:
                                    device.timeout_count += 1
                                    # Disconnect if MAX_TIMOUT_COUNT is
                                    # reached.
                                    if (device.timeout_count >=
                                            MAX_TIMEOUT_COUNT):
                                        device.status = SerialDeviceStatus.IDLE
                                        cls.disconnect(device)
                                continue
                            cls._process_frame(device, new_data)
                            device.fire_event(SerialEventType.NEW_DATA,
                                              device.taxels_array)

                    except (RuntimeError, ConnectionAbortedError):
                        logging.error(
                            '''Error getting data from gripper.
                            Disconnecting device''')
                        cls.disconnect(device)
                        continue
            time.sleep(UPDATE_RATE)
        logging.debug('Serial data task finished')
