#!/usr/bin/env python3

""" Tests for WsgDevice class. """

import pytest

from touch_detect_sdk.wsg_device import WsgDevice
from touch_detect_sdk.touch_detect_device import TouchDetectType

TEST_WSG_NAME = 'WSG_GRIPPER_1'
TEST_WSG_PORT = 1000

# Default configurations for serial port.
TCP_PORT = 1000


@pytest.fixture
def default_wsg_device():
    """Setup unit under test.
    """
    wsg_device = WsgDevice(TEST_WSG_PORT, TCP_PORT, TEST_WSG_NAME)
    yield wsg_device
    del wsg_device


class TestWsgDevice:
    """Tests for WsgDevice class.
    """

# pylint: disable=redefined-outer-name
    def test_create_default_device(self, default_wsg_device):
        """Create a default object.
        """

        # Assert
        assert default_wsg_device.device_type == TouchDetectType.TCP
        assert default_wsg_device.name == TEST_WSG_NAME
        assert default_wsg_device.tcp_port == TCP_PORT

# pylint: enable=redefined-outer-name
