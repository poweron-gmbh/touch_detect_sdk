#!/usr/bin/env python3

""" Tests for Serial touch detect SDK """

from pytest_mock import MockerFixture

from touch_detect_sdk.serial_touch_detect_sdk import SerialTouchSdk
from touch_detect_sdk.serial_device import SerialDevice


TEST_PORT = 'COM1'


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
