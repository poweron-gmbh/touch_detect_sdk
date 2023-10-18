#!/usr/bin/env python3

""" Tests for WsgGripperTouchSdk class. """

import socket
import time

from threading import Event, Thread

import pytest

from pytest_mock import MockerFixture

import numpy as np

from touch_detect_sdk.event import EventSuscriberInterface
from touch_detect_sdk.wsg_gripper_touch_sdk import WsgGripperTouchSdk
from touch_detect_sdk.wsg_device import WsgDevice, WsgEventData, WsgEventType

# array of 16bit values that represents sensor array data from ADC.
TEST_SENSOR_DATA = bytearray(
    b'\x0001\x0002\x0003\x0004\x0005\x0006'
    b'\x0101\x0102\x0103\x0104\x0105\x0106'
    b'\x0201\x0202\x0203\x0204\x0205\x0206'
    b'\x0301\x0302\x0303\x0304\x0305\x0306'
    b'\x0401\x0402\x0403\x0404\x0405\x0406'
    b'\x0501\x0502\x0503\x0504\x0505\x0506')

# sensor array data split in pairs of 8bit.
TEST_RAW_SENSOR_DATA = bytearray(
    b'\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00\x06\x00'
    b'\x01\x01\x02\x01\x03\x01\x04\x01\x05\x01\x06\x01'
    b'\x01\x02\x02\x02\x03\x02\x04\x02\x05\x02\x06\x02'
    b'\x01\x03\x02\x03\x03\x03\x04\x03\x05\x03\x06\x03'
    b'\x01\x04\x02\x04\x03\x04\x04\x04\x05\x04\x06\x04'
    b'\x01\x05\x02\x05\x03\x05\x04\x05\x05\x05\x06\x05')

# fmt: off
# Sensor array data recovered from TEST_RAW_SENSOR_DATA
TEST_CONVERTED_TAXEL_DATA = np.array([[
    0x0001, 0x0002, 0x0003, 0x0004, 0x0005, 0x0006],
    [0x0101, 0x0102, 0x0103, 0x0104, 0x0105, 0x0106],
    [0x0201, 0x0202, 0x0203, 0x0204, 0x0205, 0x0206],
    [0x0301, 0x0302, 0x0303, 0x0304, 0x0305, 0x0306],
    [0x0401, 0x0402, 0x0403, 0x0404, 0x0405, 0x0406],
    [0x0501, 0x0502, 0x0503, 0x0504, 0x0505, 0x0506]])
# fmt: on

# Too short WSG frame
TEST_SHORT_FRAME = bytes(b'\xaa\xaa')
# Frame with wrong TID
TEST_WRONG_TRANSACTION_ID = bytes(
    b'\xaa\xba\xaa\xbb\x04\x00\x74\x65\x73\x74\x2e\xdd')
# Frame with wrong PID
TEST_WRONG_PROTOCOL_ID = bytes(
    b'\xaa\xaa\xaa\xaa\x04\x00\x74\x65\x73\x74\x2e\xdd')

# Test payload to encode.
TEST_PAYLOAD_1 = bytearray(b'\x74\x65\x73\x74')
# Encoded payload.
TEST_ENCODED_FRAME_1 = bytearray(
    b'\xaa\xaa\xaa\xbb\x04\x00\x74\x65\x73\x74\x2e\xdd')

# Test payload to encode.
TEST_PAYLOAD_2 = bytearray(b'\x47\x6f\x6e\x7a\x61\x6c\x6f\x21')
# Encoded payload.
TEST_ENCODED_FRAME_2 = bytearray(
    b'\xaa\xaa\xaa\xbb\x08\x00\x47\x6f\x6e\x7a\x61\x6c\x6f\x21\x6a\x74')

# TCP port for connecting to WSG gripper.
TEST_TCP_PORT = 1000

# Command for reading left touch_detect
READ_LEFT_SENSOR_COMMAND = bytearray(b'\x01')
# Command for reading right touch_detect
READ_RIGHT_SENSOR_COMMAND = bytearray(b'\x02')


class WsgEmulator():
    """Opens a TCP port and emulates a WSG device.
    """

    def __init__(self):
        # Event for stopping data_task.
        self._stop_wsg_data_loop = Event()
        # Thread for processing incomming data.
        self._socket_thread = Thread(
            target=self.data_task)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._conn = None

    def __del__(self):
        self.stop()

    def start(self):
        """Start WSG emulator.
        """
        self.tcp_socket.bind((socket.gethostname(), TEST_TCP_PORT))
        self.tcp_socket.listen(10)

    def accept(self):
        """Accept connection from client.
        """
        self._conn, _ = self.tcp_socket.accept()
        self._socket_thread.start()

    def stop(self):
        """Stop WSG emulator.
        """
        self._stop_wsg_data_loop.set()

    def data_task(self):
        """Task for handling packages from WSG gripper.
        """
        while not self._stop_wsg_data_loop.is_set():
            try:
                # Receive data and reply.
                data = self._conn.recv(1024)
                if data:
                    payload = WsgGripperTouchSdk.decode_frame(data)
                    if payload[0] == READ_LEFT_SENSOR_COMMAND[0]:
                        frame = WsgGripperTouchSdk.make_frame(
                            TEST_RAW_SENSOR_DATA)
                        self._conn.send(frame)
                    elif payload[0] == READ_RIGHT_SENSOR_COMMAND[0]:
                        frame = WsgGripperTouchSdk.make_frame(
                            TEST_RAW_SENSOR_DATA)
                        self._conn.send(frame)
            except (ConnectionResetError, ConnectionAbortedError):
                break


class EventTester(EventSuscriberInterface):
    """Handles events from WsgGripperTouchSdk.
    """

    def __init__(self):
        self.type = WsgEventType.DISCONNECTED
        self.call_count = 0

    def touch_detect_event(self, sender: object, earg: object):
        """This function can be suscribed to any WsgGripperTouchSdk event

        :param sender: identifies the device who raised the event.
        :type sender: object
        :param earg: event information
        :type earg: WsgEventData
        """

        # Check if the event is valid.
        assert isinstance(earg, WsgEventData)

        # Filter events only from one sensor.
        if earg.type == WsgEventType.CONNECTED:
            self.type = WsgEventType.CONNECTED
            self.call_count += 1
        elif earg.type == WsgEventType.DISCONNECTED:
            self.type = WsgEventType.DISCONNECTED
            self.call_count += 1
        elif earg.type == WsgEventType.ERROR_OPENING_PORT:
            self.type = WsgEventType.ERROR_OPENING_PORT
            self.call_count += 1
        elif earg.type == WsgEventType.ERROR_CLOSING_PORT:
            self.type = WsgEventType.ERROR_CLOSING_PORT
            self.call_count += 1
        elif earg.type == WsgEventType.NEW_DATA:
            self.type = WsgEventType.NEW_DATA
            self.call_count += 1


@pytest.fixture
def event_tester_setup():
    """Setup unit under test.
    """
    tester = EventTester()
    yield tester
    del tester


class TestWsgGripperTouchSdk:
    """Test WsgGripperTouchSdk
    """
# pylint: disable=redefined-outer-name

    def test_create_default_device(self):
        """Create a default object.
        """

        # Arrange
        uut = WsgGripperTouchSdk()

        # Assert
        assert uut

    def test_make_frame(self):
        """Test for creating valid frames for WSG.
        """
        # Arrange
        uut = WsgGripperTouchSdk()

        # Act
        frame = uut.make_frame(TEST_PAYLOAD_1)
        # Assert
        assert frame == TEST_ENCODED_FRAME_1

        # Act
        frame = uut.make_frame(TEST_PAYLOAD_2)
        # Assert
        assert frame == TEST_ENCODED_FRAME_2

    def test_decode_frame(self):
        """Test for converting package payloads from
        WSG into valid sensor data.
        """
        # Arrange
        uut = WsgGripperTouchSdk()

        # Frame with insufficient characters
        payload = uut.decode_frame(TEST_SHORT_FRAME)
        # Assert
        assert not payload

        # Frame with wrong TID
        payload = uut.decode_frame(TEST_WRONG_TRANSACTION_ID)
        # Assert
        assert not payload

        # Frame with wrong PID
        payload = uut.decode_frame(TEST_WRONG_PROTOCOL_ID)
        # Assert
        assert not payload

        # Correct frame
        payload = uut.decode_frame(TEST_ENCODED_FRAME_1)
        # Assert
        assert payload == TEST_PAYLOAD_1

    def test_connect(self, mocker: MockerFixture):
        """Test for starting the internal thread.
        """
        # Arrange
        create_task_mock = mocker.patch(
            "touch_detect_sdk.wsg_gripper_touch_sdk.Thread.start")
        uut = WsgGripperTouchSdk()
        test_device = WsgDevice('', socket.gethostname())

        # Act
        uut.connect(test_device)

        # Assert
        create_task_mock.assert_called_once()

    def test_disconnect(self, mocker: MockerFixture):
        """Test for finishing the internal thread.
        """
        # Arrange
        create_task_mock = mocker.patch(
            "touch_detect_sdk.wsg_gripper_touch_sdk.Thread.start")
        uut = WsgGripperTouchSdk()
        test_device = WsgDevice('', socket.gethostname())

        # Act
        uut.disconnect(test_device)

        # Assert
        create_task_mock.assert_called_once()

    def test_connection_failed(self, event_tester_setup):
        """Test for checking connection problems.
        """
        # Arrange
        uut = WsgGripperTouchSdk()
        test_device = WsgDevice(socket.gethostname(), '')
        test_device.events += event_tester_setup

        # Act
        thread = uut.connect(test_device)
        thread.join()

        # Assert
        assert event_tester_setup.type == WsgEventType.ERROR_OPENING_PORT

    def test_connection_successful(self, event_tester_setup):
        """Test for connection successful.
        """
        # Arrange
        uut = WsgGripperTouchSdk()
        test_device = WsgDevice(socket.gethostname(), '')
        test_device.events += event_tester_setup
        wsg_emulator = WsgEmulator()

        # Act
        wsg_emulator.start()
        thread = uut.connect(test_device)
        wsg_emulator.accept()

        # Assert
        assert event_tester_setup.call_count == 1
        assert event_tester_setup.type == WsgEventType.CONNECTED

        # Disconnect and check disconnection
        thread = uut.disconnect(test_device)
        thread.join()
        wsg_emulator.stop()
        assert event_tester_setup.type == WsgEventType.DISCONNECTED

    def test_get_data(self, event_tester_setup):
        """Test for connecting and getting data.
        """
        # Arrange
        uut = WsgGripperTouchSdk()
        test_device = WsgDevice(socket.gethostname(), '')
        test_device.events += event_tester_setup
        wsg_emulator = WsgEmulator()

        # Act
        wsg_emulator.start()
        thread = uut.connect(test_device)
        wsg_emulator.accept()
        # Assert
        assert event_tester_setup.call_count == 1
        assert event_tester_setup.type == WsgEventType.CONNECTED

        # Assert new data event.
        time.sleep(0.1)
        assert event_tester_setup.type == WsgEventType.NEW_DATA

        # Act
        thread = uut.disconnect(test_device)
        thread.join()
        wsg_emulator.stop()
        # Assert
        assert event_tester_setup.type == WsgEventType.DISCONNECTED

# pylint: enable=redefined-outer-name
