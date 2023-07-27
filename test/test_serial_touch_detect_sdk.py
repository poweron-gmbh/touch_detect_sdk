#!/usr/bin/env python3

""" Tests for Serial touch detect SDK """

from pytest_mock import MockerFixture

from touch_detect_sdk.serial_touch_detect_sdk import SerialTouchSdk
from touch_detect_sdk.serial_device import SerialDevice


TEST_PORT = 'COM1'

# sensor array data split in pairs of 8bit.
TEST_RAW_SENSOR_DATA = bytearray(b'\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00\x06\x00'
                                 b'\x01\x01\x02\x01\x03\x01\x04\x01\x05\x01\x06\x01'
                                 b'\x01\x02\x02\x02\x03\x02\x04\x02\x05\x02\x06\x02'
                                 b'\x01\x03\x02\x03\x03\x03\x04\x03\x05\x03\x06\x03'
                                 b'\x01\x04\x02\x04\x03\x04\x04\x04\x05\x04\x06\x04'
                                 b'\x01\x05\x02\x05\x03\x05\x04\x05\x05\x05\x06\x05')


class TestSerialTouchDetectSdk:
    """Test SerialTouchDetectSdk
    """

# pylint: disable=redefined-outer-name

    def test_create_default_device(self):
        """Create a default object.
        """

        # Arrange
        uut = SerialTouchSdk()

        # Assert
        assert uut

    def test_connect(self, mocker: MockerFixture):
        """Test connect function.
        """
        # Arrange
        start_mock = mocker.patch(
            "touch_detect_sdk.wsg_gripper_touch_sdk.Thread.start")
        uut = SerialTouchSdk()
        test_device = SerialDevice(TEST_PORT)

        # Act
        thread = uut.connect(test_device)

        # Assert
        assert thread
        start_mock.assert_called_once()

    def test_disconnect(self, mocker: MockerFixture):
        """Test disconnect function.
        """
        # Arrange
        create_task_mock = mocker.patch(
            "touch_detect_sdk.wsg_gripper_touch_sdk.Thread.start")
        uut = SerialTouchSdk()
        test_device = SerialDevice(TEST_PORT)

        # Act
        thread = uut.disconnect(test_device)

        # Assert
        assert thread
        create_task_mock.assert_called_once()

# pylint: enable=redefined-outer-name
