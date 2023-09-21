#!/usr/bin/env python3

"""SDK for interfacing CAN devices"""

import asyncio
import copy
import logging
import threading

from threading import Event, Thread

import numpy as np
import serial  # pyserial
from serial.tools.list_ports import comports
from serial import serialutil

from .can_device import CanDevice, CanEventType  # noqa
from .touch_detect_device import ConnectionStatus


SUPPORTED_MANUFACTURERS_LIST = ['FTDI']

# Value that represents the start of the frame.
START_OF_FRAME = 0xFF
# Value that represents the end of the frame.
END_OF_FRAME = 0xFE
# Amount of frames per package.
PACKAGE_SIZE = 12
# Amount of bytes of the frame.
FRAME_SIZE = 22
# CAN Device ID of package 0.
DEVICE_ID = 0x300


class CanFrameDecoder:
    """Set of tools for decoding CAN packages.
    """

    @staticmethod
    def decode_package(package: list[bytes]) -> np.array:
        """Decodes a complete package. This function does not check
        if the package is valid.

        :param package: package to decode.
        :type package: list
        :return: (6,6) numpy array
        :rtype: tuple
        """
        try:
            taxel_data = []
            # Iterates through all the frames of package.
            for frame in package:
                byte_data = []
                index = 0
                # Decode the encoding applied by USB CAN stick.
                for index in range(5, 15, 2):
                    byte_data.append(CanFrameDecoder.make_byte(
                        frame[index], frame[index+1]))
                # Decode the encoding applied by CAN Device.
                taxel_data.append(CanFrameDecoder.make_short(
                    byte_data[3] & 0x0F, byte_data[0]))
                taxel_data.append(CanFrameDecoder.make_short(
                    (byte_data[3] & 0xF0) >> 4, byte_data[1]))
                taxel_data.append(CanFrameDecoder.make_short(
                    byte_data[4] & 0x0F, byte_data[2]))
            # Convert the list into a byte array.
            result = np.array(taxel_data, dtype=int)
            # Reshape to the proper array shape.
            return result.reshape((6, 6))
        except serial.SerialException:
            logging.error('Error decoding package')

    @staticmethod
    def check_frame_format(frame: bytes) -> bool:
        """Checks that frame has a valid structure.

        :param frame: array to decode
        :type frame: bytes
        :return: true if format is valid, false otherwise
        :rtype: bool
        """
        # Frame has to have a fixed size
        if len(frame) != FRAME_SIZE:
            return False

        # Frame should start with START_OF_FRAME and end with END_OF_FRAME
        if frame[0] != START_OF_FRAME or frame[-1] != END_OF_FRAME:
            return False

        return True

    @staticmethod
    def get_frame_id(frame: bytearray) -> int:
        """gets the ID of a frame

        :param frame: Frame to decode
        :type frame: bytearray
        :return: ID of the frame
        :rtype: bytes
        """
        high_byte = CanFrameDecoder.make_byte(frame[1], frame[2]) & 0x0F
        low_byte = CanFrameDecoder.make_byte(frame[3], frame[4])
        return CanFrameDecoder.make_short(high_byte, low_byte)

    @staticmethod
    def is_starting_frame(frame: bytearray) -> bool:
        """Test if frame is the first frame of a package.

        :param frame: frame to test
        :type bytearray: bytes
        :return: true if it is the start frame, false otherwise.
        :rtype: bool
        """
        # The first frame should have an ID that matches DEVICE_ID
        if CanFrameDecoder.get_frame_id(frame) == DEVICE_ID:
            return True
        return False

    @staticmethod
    def make_byte(high_byte: bytes, low_byte: bytes) -> bytes:
        """ This functions masks the information of two bytes into one.
        This has to be done in order to decode the information encoded by
        USB CAN Stick.

        :param high_byte: Byte with Most significant bit
        :type high_byte: bytes
        :param low_byte: Least significant byte
        :type low_byte: bytes
        :return: decoded byte
        :rtype: bytes
        """
        return (high_byte & 0x80) | (low_byte & 0x7F)

    @staticmethod
    def make_short(high_byte: bytes, low_byte: bytes) -> int:
        """ This functions creates a 16 bit int from 2 single bytes.

        :param high_byte: Most significant byte
        :type high_byte: bytes
        :param low_byte: Least significant byte
        :type low_byte: bytes
        :return: decoded byte
        :rtype: int
        """
        return (high_byte << 8) | low_byte


class CanTouchSdk:
    """This Class manages the communication with CAN devices over
    RS232 USB Adapter.
    """

    @classmethod
    def __init__(cls):
        # Create a logger.
        cls._logger = logging.getLogger(__name__)
        # Set basic configurations for logging.
        logging.basicConfig(encoding='utf-8', level=logging.INFO)
        # Event for stopping incomming_data_thread.
        cls._stop_can_data_loop = Event()
        # Thread for processing incomming data.
        cls._incoming_data_thread = Thread(
            target=cls._can_data_thread)
        # list of devices that have to be polled for data.
        cls._device_list = []
        # Lock for internal variables.
        cls._lock = threading.Lock()

    @classmethod
    def __del__(cls):
        """Ensure that threads stopped and connection closed
        """
        if not cls._stop_can_data_loop.is_set():
            cls._stop_can_data_loop.set()

    @staticmethod
    def find_devices() -> list[CanDevice]:
        """Search serial ports available for connection. This function
           filters the devices which are not supported by this library.

        :return: list of strings with the names of the ports available.
        :rtype: list[CanDevice]
        """
        device_list = []
        for port in comports():
            if port.manufacturer in SUPPORTED_MANUFACTURERS_LIST:
                device = CanDevice(port.name)
                device_list.append(device)
        return device_list

    @classmethod
    def connect(cls, can_device: CanDevice) -> bool:
        """connects to specific CAN device.

        :param can_device: device to connect
        :type can_device: CanDevice
        :return: True if connected, False otherwise
        :rtype: bool
        """
        # Check if port was already opened.
        if can_device.connection_status == ConnectionStatus.CONNECTED:
            logging.info('Already connected to a device')
            return True

        # Add device if wasn't already in the list.
        with cls._lock:
            if can_device not in cls._device_list:
                cls._device_list.append(can_device)

        # Open the port.
        try:
            can_device.port_handler.open()
        except serial.SerialException as error:
            logging.error("Could not open serial port %s: %s",
                          can_device.name, error)
            can_device.fire_event(CanEventType.ERROR_OPENING_PORT, [error])
            return False

        # Notify connection.
        can_device.connection_status = ConnectionStatus.CONNECTED
        can_device.fire_event(CanEventType.CONNECTED)

        # Start the thread in case it wasn't running before.
        if not cls._incoming_data_thread.is_alive():
            cls._stop_can_data_loop.clear()
            cls._incoming_data_thread.start()

        # Prepare port for reading.
        can_device.port_handler.reset_input_buffer()
        can_device.port_handler.setDTR(False)
        can_device.port_handler.setRTS(False)
        return True

    @classmethod
    def disconnect(cls, can_device: CanDevice) -> bool:
        """Disconnects CAN device.

        :param can_device: device to disconnect
        :type can_device: CanDevice
        :return: True if disconnection was successful, False otherwise
        :rtype: boolean
        """
        # Check if port was already closed.
        if can_device.connection_status == ConnectionStatus.DISCONNECTED:
            logging.info('Already disconnected')
            return True

        # Remove device from the list.
        with cls._lock:
            if can_device in cls._device_list:
                cls._device_list.remove(can_device)

        # Disconnect port.
        try:
            can_device.port_handler.setDTR(True)
            can_device.port_handler.setRTS(True)
            can_device.port_handler.close()
        except RuntimeError as error:
            logging.error("Could not close serial port %s: %s",
                          can_device.name, error)
            can_device.fire_event(CanEventType.ERROR_CLOSING_PORT, [error])
            can_device.connection_status = ConnectionStatus.CONNECTION_LOST
            return False

        # Notify disconnection.
        can_device.connection_status = ConnectionStatus.DISCONNECTED
        can_device.fire_event(CanEventType.DISCONNECTED)

        # Stop CAN thread if no device is listed for pooling.
        with cls._lock:
            if len(cls._device_list) == 0:
                cls._stop_can_data_loop.set()

        return True

    @classmethod
    def get_data(cls, can_device: CanDevice) -> np.array:
        """Get information about sensor array.

        :param can_device: device to connect
        :type can_device: CanDevice
        :return: array with the values of each taxel.
        :rtype: np.array
        """
        if not can_device.connection_status == ConnectionStatus.CONNECTED:
            logging.warning('Data thread not running. Call connect() first.')
            return None
        return can_device.taxels_array

    @staticmethod
    def _get_frame(port: serial.Serial) -> bytes:
        """Reads a valid package from Serial port.

        :param port: Serial Port to read
        :type port: serial.Serial
        :raises serialutil.SerialTimeoutException: if failed to read data.
        :return: package in byte format or None if there was a problem.
        :rtype: bytes
        """
        # Read one frame.
        data = port.read(FRAME_SIZE)

        if not data:
            return None
        if not CanFrameDecoder.check_frame_format(data):
            logging.error('Package has not a valid format. It will be ignored')
            return None
        return data

    @classmethod
    def _can_data_thread(cls):
        """Start loop for communicating with CAN device.
        """
        # Event loop for running incomming data callback.
        loop_can_data = asyncio.new_event_loop()
        asyncio.set_event_loop(loop_can_data)
        loop_can_data.run_until_complete(cls._can_data_task())

    @classmethod
    async def _can_data_task(cls):
        """Task for handling packages from CAN device.
        """
        logging.debug('CAN data task initialized')
        # Iterate until signal is sent.
        while not cls._stop_can_data_loop.is_set():
            # Copy objects and release the lock.
            device_list = []
            with cls._lock:
                device_list = copy.copy(cls._device_list)

            # Iterate through devices.
            for device in device_list:
                # Get one Frame
                try:
                    frame = cls._get_frame(device.port_handler)
                    # Continue is no frame was decoded.
                    if not frame:
                        continue
                except serialutil.SerialTimeoutException:
                    logging.error('''Error reading data from serial
                         port. Disconnecting port''')
                    cls.disconnect(device)
                    device.connection_status = ConnectionStatus.CONNECTION_LOST
                    continue

                # Add frame to buffer. Clear buffer if it is not the first
                # frame.
                if CanFrameDecoder.is_starting_frame(frame):
                    device.data_buffer.clear()
                device.data_buffer.append(frame)

                # Decode package when there are enough frames.
                if len(device.data_buffer) == PACKAGE_SIZE:
                    taxel_array = CanFrameDecoder.decode_package(
                        device.data_buffer)
                    device.taxels_array = taxel_array
                    device.fire_event(CanEventType.NEW_DATA, taxel_array)
        logging.debug('CAN data task finished')
