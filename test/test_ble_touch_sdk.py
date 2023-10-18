#!/usr/bin/env python3

""" Tests for BleGripperTouchSdk class. """

import pytest

from pytest_mock import MockerFixture

from touch_detect_sdk.ble_touch_sdk import BleTouchSdk
from touch_detect_sdk.ble_device import BleDevice, BleEventType, BleEventInfo
from touch_detect_sdk.event import EventSuscriberInterface

TEST_DEVICE_ID = 'PWRON1'
TEST_MAC = 'DC:EE:FF:C8:6A:10'


class EventTester(EventSuscriberInterface):
    """Handles events from BleTouchSdk.
    """

    def __init__(self):
        super().__init__()
        self.type = BleEventType.DISCONNECTED
        self.call_count = 0

    def touch_detect_event(self, sender: object, earg: object):
        """This function can be suscribed to any BleTouchSdk event

        :param sender: identifies the device who raised the event.
        :type sender: object
        :param event_data: event information
        :type event_data: BleEventType
        """

        # Check if the event is valid.
        assert isinstance(earg, BleEventInfo)

        # Filter events only from one sensor.
        if sender.address == TEST_MAC:
            if earg.type == BleEventType.CONNECTED:
                self.type = BleEventType.CONNECTED
                self.call_count += 1
            elif earg.type == BleEventType.DISCONNECTED:
                self.type = BleEventType.DISCONNECTED
                self.call_count += 1
            elif earg.type == BleEventType.ERROR_OPENING_PORT:
                self.type = BleEventType.ERROR_OPENING_PORT
                self.call_count += 1
            elif earg.type == BleEventType.ERROR_CLOSING_PORT:
                self.type = BleEventType.ERROR_CLOSING_PORT
                self.call_count += 1
            elif earg.type == BleEventType.NEW_DATA:
                self.type = BleEventType.NEW_DATA
                self.call_count += 1


@pytest.fixture
def event_tester_setup():
    """Setup unit under test.
    """
    tester = EventTester()
    yield tester
    del tester


class TestBleTouchSdk:
    """Test BleTouchSdk
    """
# pylint: disable=redefined-outer-name

    def test_create_default_device(self):
        """Create a default object.
        """

        # Arrange
        uut = BleTouchSdk()

        # Assert
        assert uut

    def test_connect(self, mocker: MockerFixture):
        """Test for starting the internal thread.
        """
        # Arrange
        create_task_mock = mocker.patch(
            "touch_detect_sdk.ble_touch_sdk.Thread.start")
        uut = BleTouchSdk()
        test_device = BleDevice(TEST_MAC, TEST_DEVICE_ID, '')

        # Act
        uut.connect(test_device)

        # Assert
        create_task_mock.assert_called_once()

# pylint: enable=redefined-outer-name
