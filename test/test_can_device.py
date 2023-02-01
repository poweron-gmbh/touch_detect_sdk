#!/usr/bin/env python3

""" Tests for can_device.py class. """

import serial
import pytest

from src.can_device import CanDevice
from src.touch_detect_device import TouchDetectType

TEST_CAN_NAME = 'TOUCH_DETECT_LEFT'
TEST_CAN_PORT = 'COM1'

# Default configurations for serial port.
BAUDRATE = 1000000
PARITY = serial.PARITY_NONE
STOP_BITS = serial.STOPBITS_ONE
BYTE_SIZE = 8


@pytest.fixture
def default_can_device():
    """Setup unit under test.
    """
    can_device = CanDevice(TEST_CAN_NAME, TEST_CAN_PORT)
    yield can_device
    del can_device


class TestCanDevice:
    """Test CanDevice
    """

# pylint: disable=redefined-outer-name
    def test_create_default_device(self, default_can_device):
        """Create a default object.
        """

        # Assert
        assert default_can_device.device_type == TouchDetectType.CAN
        assert default_can_device.port_handler.baudrate == BAUDRATE
        assert default_can_device.port_handler.port == TEST_CAN_PORT
        assert default_can_device.port_handler.parity == PARITY
        assert default_can_device.port_handler.stopbits == STOP_BITS
        assert default_can_device.port_handler.bytesize == BYTE_SIZE
        assert not default_can_device.port_handler.is_open


# pylint: enable=redefined-outer-name
