#!/usr/bin/env python3

""" Tests for ble_device.py class. """

import pytest

from src.ble_device import BleDevice
from src.touch_detect_device import TouchDetectType

TEST_BLE_NAME = 'PWRN1'
TEST_BLE_MAC = '08:8d:08:1f:25:b5'

@pytest.fixture
def default_ble_device():
    """Setup unit under test.
    """
    ble_device = BleDevice(TEST_BLE_NAME, TEST_BLE_MAC)
    yield ble_device
    del ble_device


class TestBleDevice:
    """Test BleDevice
    """

# pylint: disable=redefined-outer-name
    def test_create_default_device(self, default_ble_device):
        """Create a default object.
        """
        assert default_ble_device.device_type == TouchDetectType.BLE
        assert default_ble_device.ble_handler.address == TEST_BLE_MAC

# pylint: enable=redefined-outer-name