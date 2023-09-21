#!/usr/bin/env python3

""" Tests for can_device.py class. """

import pytest

from touch_detect_sdk.can_touch_sdk import CanTouchSdk

SUPPORTED_DEVICE_DESCRIPTION = 'USB Serial Port'
SUPPORTED_MANUFACTURERS_LIST = 'FTDI'


@pytest.fixture
def default_can_touch_sdk():
    """Setup unit under test.
    """
    can_device = CanTouchSdk()
    yield can_device
    del can_device


class TestCanTouchSdk:
    """Test CanTouchDetect SDK.
    """

# pylint: disable=redefined-outer-name
    def test_create_default_device(self, default_can_touch_sdk):
        """Create a default object.
        """
        # Assert
        assert default_can_touch_sdk is not None

# pylint: enable=redefined-outer-name
