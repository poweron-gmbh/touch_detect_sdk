#!/usr/bin/python

"""Tests for ble_touch_sdk. These tests require BLE TouchDetect device to be running."""

import logging
import pytest
import time

from src.ble_touch_sdk import BleTouchSdk

# Change this to the device name used for tests.
BLE_DEVICE_NAME = 'PWRON1'
RATE = 0.2


@pytest.fixture
def bleTouchSdkDefault():
    """Setup unit under test.
    """
    ble_touch_sdk = BleTouchSdk()
    yield ble_touch_sdk
    del ble_touch_sdk

class TestBleTouchSdk:
    """Test BLE TouchDetect SDK.
    """

    def test_find_ble_devices(self, bleTouchSdkDefault):
        """Test if library can find BLE devices.
        """
        devices = bleTouchSdkDefault.search_devices()
        assert devices, 'No BLE devices found'

    def test_connect_and_disconnect(self, bleTouchSdkDefault):
        """Connect to BLE device and disconnect immediately.
        """
        # Connect to first BLE device.
        assert bleTouchSdkDefault.connect(BLE_DEVICE_NAME)
        # Disconnect immediately.
        assert bleTouchSdkDefault.disconnect()

    def test_connect_and_get_data(self, bleTouchSdkDefault):
        """Connect to BLE device and get data.
        """
        # Connect to first BLE device.
        assert bleTouchSdkDefault.connect(BLE_DEVICE_NAME)

        # Wait for device to send data.
        time.sleep(RATE)
        # Get the data.
        data = bleTouchSdkDefault.get_data()
        # Data should not be None.
        assert data, 'No data retrieved'
        # The first element of the tuple must be a timestamp that's not 0.
        assert data[0] != 0.0
        # There must be data for sensors. If touch detect has 6x6 sensors, there must be 36 values.
        assert len(data[1]) == 36

        # Disconnect immediately.
        assert bleTouchSdkDefault.disconnect()
