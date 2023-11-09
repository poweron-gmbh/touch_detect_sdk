#!/usr/bin/env python3

"""Describes a serial touch detect Device"""

from enum import Enum, unique

import logging
from threading import Thread
import numpy as np
import serial  # pyserial

from serial.serialutil import SerialException
# pylint: disable=no-name-in-module
from yahdlc import (
    FRAME_ACK,
    FRAME_DATA,
    frame_data,
    get_data,
)
# pylint: enable=no-name-in-module

from .event import Event
from .periodic_timer import PeriodicTimer, PeriodicTimerSuscriber
from .touch_detect_device import ConnectionStatus, TouchDetectDevice, \
    TouchDetectType
from .touch_detect_utils import TouchDetectUtils

# Default values for serial port.
DEFAULT_BAUDRATE = 115200
PARITY = serial.PARITY_NONE
STOP_BITS = serial.STOPBITS_ONE
BYTE_SIZE = 8
DEFAULT_TIMEOUT_SEC = 0.05
DEFAULT_UPDATE_RATE_SEC = 0.03

# Constants for serial communication.
FRAME_START_BYTE = bytes(b'\x7e')
FRAME_END_BYTE = bytes(b'\x7e')
DEVICE_ADDRESS = bytes(b'\xff')
SERIAL_COMMAND_GET_DATA = bytes(b'\x01')
SERIAL_COMMAND_GET_DATA_SIZE = 84
DEFAULT_SENSOR_ARRAY_SIZE = 72


@unique
class SerialEventType(Enum):
    """Represents different type of events triggered by Serial touch detect.
    """
    ERROR_OPENING_PORT = 2
    CONNECTED = 3
    DISCONNECTED = 4
    NEW_DATA = 5
    CONNECTION_ERROR = 6


@unique
class SerialDeviceStatus(Enum):
    """Represents different type of events triggered by Serial touch detect.
    """
    IDLE = 0
    REQUEST_SENT = 1


class SerialEventData():
    """Encapsulates event data for serial events.
    """

    def __init__(self, event: SerialEventType, data: np.array = None):
        """Initialize class

        :param event: type of event triggered
        :type event: SerialEventType
        :param data: relevant data for the event, defaults to None
        :type data: numpy array, optional
        """
        self.type = event
        self.data = data


class SerialDevice(TouchDetectDevice, PeriodicTimerSuscriber):
    """Represents a Serial device.
    """
    # Event object
    events = Event('')

    def __init__(self, address: str = None, name: str = None,
                 taxels_array_size: tuple = (6, 6)):
        """Initialize Serial object.

        :param address: Address of the device
        :type address: str
        :param name: Name of serial port
        :type name: str
        :param taxels_array_size: size of the array, defaults to (6, 6)
        :type taxels_array_size: tuple, optional
        """
        super().__init__(address, name, TouchDetectType.SERIAL,
                         taxels_array_size)

        # Create a logger.
        self._logger = logging.getLogger(__name__)
        # Set basic configurations for logging
        logging.basicConfig(encoding='utf-8', level=logging.INFO)

        # Private variables
        self._port_handler = serial.Serial()
        self._port_handler.port = address
        self._port_handler.baudrate = DEFAULT_BAUDRATE
        self._port_handler.parity = PARITY
        self._port_handler.stopbits = STOP_BITS
        self._port_handler.bytesize = BYTE_SIZE
        self._port_handler.timeout = DEFAULT_TIMEOUT_SEC
        self._connection_status = ConnectionStatus.DISCONNECTED
        self._periodic_timer = PeriodicTimer()
        # List of threads currently running
        self._thread_list = []
        self._request_sent = False

    def connect(self) -> Thread:
        """Connects to SerialTouchDetect device.

        :return: Reference to the thread running
        :rtype: Thread
        """
        thread = Thread(target=self._connect)
        thread.start()
        self._thread_list.append(thread)
        return thread

    def disconnect(self) -> Thread:
        """Disconnects SerialTouchDetect device

        :return: Reference to the thread running
        :rtype: Thread
        """
        thread = Thread(target=self._disconnect)
        thread.start()
        self._thread_list.append(thread)
        return thread

    @property
    def update_rate_ms(self) -> int:
        """return the update rate of the device in milliseconds.
        :rtype: str
        """
        return int(DEFAULT_UPDATE_RATE_SEC * 1000)

    def _connect(self):
        """Connect to Serial device.
        """
        # Check if port was already opened.
        if self._connection_status == ConnectionStatus.CONNECTED:
            logging.info('Already connected')
            return

        # Open the port.
        try:
            self._port_handler.open()
        except SerialException as error:
            logging.error("Could could not connect to Device %s: %s",
                          self.name, error)
            self._fire_event(
                SerialEventType.ERROR_OPENING_PORT, error)
            return

        # Notify connection.
        self._connection_status = ConnectionStatus.CONNECTED
        self._fire_event(SerialEventType.CONNECTED)

        # Start the thread.
        self._periodic_timer.start(self, DEFAULT_UPDATE_RATE_SEC)

    def _disconnect(self):
        """Thread that handles disconnection of devices.
        """
        # Check if port was already closed.
        if self._connection_status == ConnectionStatus.DISCONNECTED:
            logging.info('Already disconnected')
            return

        # Stop timer.
        self._periodic_timer.stop()

        # Notify disconnection.
        self._connection_status = ConnectionStatus.DISCONNECTED
        self._fire_event(SerialEventType.DISCONNECTED)

        # Disconnect port.
        self._port_handler.close()

    def _fire_event(self, event_type: SerialEventType,
                    event_data=None):
        """Fires the event of the class.

        :param event_type: reason why the event was triggered.
        :type event_type: SerialEventType
        :param event_data: useful data linked to the event, defaults to None
        :type event_data: numpy array, optional
        """
        event_data = SerialEventData(event_type, event_data)
        self.events(event_data)

    def _get_hdlc_frame(self, new_data: bytes) -> list[bytes]:
        """Process all the data comming from serial port. Filters the
        data into HDLC frames.

        :param serial_device: Device to get the data from.
        :type serial_device: SerialDevice
        :return: Incomming HDLC frame, None otherwise.
        :rtype: bytes
        """
        result = []
        serial_data = new_data
        while len(serial_data) != 0:
            # Find the start of the frame
            start_index = serial_data.find(FRAME_START_BYTE)
            if start_index == -1:
                # There is no starting frame, ignore package.
                return None

            # Find the end of frame
            stop_index = serial_data.find(FRAME_END_BYTE, start_index + 1)
            if stop_index == -1:
                # There is no end frame, ignore package.
                return None

            # There is a complete frame detected. create a new array.
            stop_index = stop_index + 1
            frame = serial_data[start_index:stop_index]
            result.append(frame)

            # Remove from the serial data the processed frame.
            serial_data = serial_data[stop_index:]
        return result

    def _process_frame(self, frames: list[bytes]):
        """Process raw data coming from serial port and updates the data
        accordingly.

        :param frames: raw data to process
        :type frames: list[bytes]
        """
        for frame in frames:
            data, frame_type, _ = get_data(frame)

            # Reply ACK with another ACK
            if frame_type == FRAME_ACK:
                reply = frame_data('', FRAME_ACK, 5)
                self._port_handler.write(reply)
            # Ignore non-valid packages.
            elif (frame_type == FRAME_DATA and
                    len(data) == DEFAULT_SENSOR_ARRAY_SIZE):
                self.taxels_array = TouchDetectUtils.to_taxel_array(
                    self.taxels_array_size, data)
                self._fire_event(SerialEventType.NEW_DATA, self.taxels_array)
            else:
                self._logger.warning(
                    'Received payload with wrong size. Ignoring package.')

    def on_timer_event(self):
        """Event called on each period of the timer.
        """
        try:
            if not self._request_sent:
                self._port_handler.reset_input_buffer()
                data_request_frame = frame_data(
                    SERIAL_COMMAND_GET_DATA, FRAME_DATA, 1)
                self._port_handler.write(data_request_frame)
                self._request_sent = True
            elif self._request_sent:
                self._request_sent = False
                new_data = \
                    self._port_handler.read_all()
                # Ignore package if the size is not correct.
                data_size = len(new_data)
                if data_size < SERIAL_COMMAND_GET_DATA_SIZE:
                    return

                # Get HDLC frame.
                hdlc_frames = self._get_hdlc_frame(new_data)
                if not hdlc_frames:
                    return

                # Process frame.
                self._process_frame(hdlc_frames)

        except (RuntimeError, SerialException, ConnectionAbortedError):
            error = '''Error getting data from sensor.
                Disconnecting device'''
            logging.error(error)
            self._fire_event(SerialEventType.CONNECTION_ERROR, error)
            self.disconnect()
