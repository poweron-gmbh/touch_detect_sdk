#!/usr/bin/env python3

""" Tests for Serial Device """

from threading import Event, Thread
import time
import sys

import pytest
from pytest_mock import MockerFixture
import serial  # pyserial
# pylint: disable=no-name-in-module
from yahdlc import (
    FRAME_ACK,
    FRAME_DATA,
    frame_data,
    get_data,
)
# pylint: enable=no-name-in-module

from touch_detect_sdk.event import EventSuscriberInterface
from touch_detect_sdk.serial_device import SerialDevice, SerialEventType
from .test_data.sensor_data import TEST_RAW_SENSOR_DATA, \
    TEST_CONVERTED_TAXEL_DATA

SERIAL_COMMAND_GET_DATA = bytes(b'\x01')

TEST_PORT_1 = '/dev/pts/1'
TEST_PORT_2 = '/dev/pts/2'

# Default values for serial port.
DEFAULT_BAUDRATE = 115200
PARITY = serial.PARITY_NONE
STOP_BITS = serial.STOPBITS_ONE
BYTE_SIZE = 8
DEFAULT_TIMEOUT_SEC = 0.05

MIN_PACKAGE_SIZE = 6


class SerialDeviceEmulator():
    """Opens a serial port and emulates a SerialDevice.
    """

    def __init__(self, port):
        # Event for stopping data_task.
        self._stop_wsg_data_loop = Event()
        # Thread for processing incomming data.
        self._serial_thread = Thread(
            target=self.data_task)
        self._serial_port = serial.Serial(TEST_PORT_2)
        # Private variables
        self._port_handler = serial.Serial()
        self._port_handler.port = port
        self._port_handler.baudrate = DEFAULT_BAUDRATE
        self._port_handler.parity = PARITY
        self._port_handler.stopbits = STOP_BITS
        self._port_handler.bytesize = BYTE_SIZE
        self._port_handler.timeout = DEFAULT_TIMEOUT_SEC
        self._communication_started = False

        self.communication_in_progress = False

    def __del__(self):
        self.stop()

    def start(self):
        """Start emulator.
        """
        self._serial_thread.start()

    def stop(self):
        """Stop emulator.
        """
        if self._communication_started:
            self._stop_wsg_data_loop.set()
            self._serial_thread.join()
            self._communication_started = False

    def data_task(self):
        """Task for handling packages from the SDK.
        """
        self._communication_started = True
        while not self._stop_wsg_data_loop.is_set():
            # Read data when there is a package available
            if self._serial_port.in_waiting < MIN_PACKAGE_SIZE:
                continue

            # Read all the data available from serial port
            serial_data = self._serial_port.read_all()
            data, frame_type, _ = get_data(serial_data)

            # Reply ACK with another ACK
            if frame_type == FRAME_DATA:
                if data == SERIAL_COMMAND_GET_DATA:
                    hdlc_data_frame = frame_data(
                        bytes(TEST_RAW_SENSOR_DATA), FRAME_DATA, 0)
                    hdlc_ack_frame = frame_data('', FRAME_ACK, 2)
                    final_frame = hdlc_data_frame + hdlc_ack_frame
                    self._serial_port.write(final_frame)
                    self.communication_in_progress = True
            elif frame_type == FRAME_ACK:
                self.communication_in_progress = False
            time.sleep(DEFAULT_TIMEOUT_SEC)


class Suscriber(EventSuscriberInterface):
    """Suscriber for events.
    """

    def __init__(self):
        super().__init__()
        self.connected = False
        self.connect_and_then_data = False
        self.disconnected = False
        self.new_data_event = False
        self.error_opening_port = False
        self.data = None

    def touch_detect_event(self, sender: object, earg: object):
        """Implement function function called on event
        """
        if earg.type == SerialEventType.CONNECTED:
            self.connected = True
            if not self.new_data_event:
                self.connect_and_then_data = True
        elif earg.type == SerialEventType.NEW_DATA:
            self.new_data_event = True
            self.data = earg.data
        elif earg.type == SerialEventType.DISCONNECTED:
            self.disconnected = True
        elif earg.type == SerialEventType.ERROR_OPENING_PORT:
            self.error_opening_port = True


class TestSerialDevice:
    """Test SerialDevice
    """

# pylint: disable=redefined-outer-name
    def test_create_default_device(self):
        """Create a default object.
        """

        # Arrange
        uut = SerialDevice()

        # Assert
        assert uut

    def test_connect(self, mocker: MockerFixture):
        """Test connect function calling to connect thread.
        """
        # Arrange
        start_mock = mocker.patch(
            "touch_detect_sdk.serial_device.Thread.start")
        uut = SerialDevice(TEST_PORT_1)

        # Act
        thread = uut.connect()

        # Assert
        assert thread
        start_mock.assert_called_once()

    def test_disconnect(self, mocker: MockerFixture):
        """Test disconnect function calling to disconnect thread.
        """
        # Arrange
        start_mock = mocker.patch(
            "touch_detect_sdk.serial_device.Thread.start")
        uut = SerialDevice(TEST_PORT_1)

        # Act
        thread = uut.disconnect()

        # Assert
        assert thread
        start_mock.assert_called_once()

    @pytest.mark.skipif(sys.platform != "linux", reason="requires linux")
    def test_connect_wrong_port(self):
        """Attempt to connect to wrong port.
        """
        # Arrange
        fake_suscriber = Suscriber()
        uut = SerialDevice('COM100')
        uut.events += fake_suscriber

        # Act
        uut.connect()
        time.sleep(1.0)

        # Assert
        assert not fake_suscriber.connected
        assert fake_suscriber.error_opening_port

    @pytest.mark.skipif(sys.platform != "linux", reason="requires linux")
    def test_connect_2(self):
        """Connect to SerialDeviceEmulator.
        """
        # Arrange
        fake_suscriber = Suscriber()
        uut = SerialDevice(TEST_PORT_1)
        uut.events += fake_suscriber
        emulator = SerialDeviceEmulator(TEST_PORT_2)

        # Act
        emulator.start()
        uut.connect()
        time.sleep(1.0)
        uut.disconnect()
        emulator.stop()

        # Assert
        assert fake_suscriber.connected

    @pytest.mark.skipif(sys.platform != "linux", reason="requires linux")
    def test_get_data(self):
        """Connect and try to get data.
        """
        # Arrange
        fake_suscriber = Suscriber()
        uut = SerialDevice(TEST_PORT_1)
        uut.events += fake_suscriber
        emulator = SerialDeviceEmulator(TEST_PORT_2)

        # Act
        emulator.start()
        uut.connect()
        time.sleep(1.0)
        uut.disconnect()
        emulator.stop()

        # Assert
        assert fake_suscriber.new_data_event
        assert fake_suscriber.connect_and_then_data
        assert (fake_suscriber.data == TEST_CONVERTED_TAXEL_DATA).all()

    @pytest.mark.skipif(sys.platform != "linux", reason="requires linux")
    def test_disconnect_2(self):
        """Connect, get data and disconnect from device.
        """
        # Arrange
        fake_suscriber = Suscriber()
        uut = SerialDevice(TEST_PORT_1)
        uut.events += fake_suscriber
        emulator = SerialDeviceEmulator(TEST_PORT_2)

        # Act
        emulator.start()
        uut.connect()
        time.sleep(1.0)
        uut.disconnect()
        emulator.stop()

        # Assert
        assert fake_suscriber.connected
        assert fake_suscriber.new_data_event
        assert fake_suscriber.disconnected


# pylint: enable=redefined-outer-name
