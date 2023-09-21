#!/usr/bin/env python3

"""Tests for touch_detect_device"""

import logging
import pytest
import numpy as np

from pytest_mock import MockerFixture
from touch_detect_sdk.touch_detect_device import TouchDetectDevice
from touch_detect_sdk.touch_detect_device import TouchDetectType

# Change this to the device name used for tests.
TEST_NAME = 'PWRON1'
TEST_ADDRESS = ''
TEST_TOUCH_DETECT_TYPE = TouchDetectType.BLE

TEST_LOG_ERROR_1 = \
    'Attempt to write touch_detect_device array with different size.'

TEST_TAXEL_8_X_8 = np.array([[1, 2, 3, 4, 5, 6, 7, 8],
                            [1, 2, 3, 4, 5, 6, 7, 8],
                            [1, 2, 3, 4, 5, 6, 7, 8],
                            [1, 2, 3, 4, 5, 6, 7, 8],
                            [1, 2, 3, 4, 5, 6, 7, 8],
                            [1, 2, 3, 4, 5, 6, 7, 8],
                            [1, 2, 3, 4, 5, 6, 7, 8],
                            [1, 2, 3, 4, 5, 6, 7, 8]])


@pytest.fixture
def default_touch_detect_device():
    """Setup unit under test.
    """
    touch_detect_device = TouchDetectDevice()
    yield touch_detect_device
    del touch_detect_device


class TestTouchDetectDevice:
    """Test TouchDetectDevice
    """

# pylint: disable=redefined-outer-name
    def test_create_default_device(self, default_touch_detect_device):
        """Create a default object.
        """
        assert not default_touch_detect_device.name
        assert not default_touch_detect_device.address
        assert default_touch_detect_device.device_type == \
            TouchDetectType.VIRTUAL
        assert default_touch_detect_device.taxels_array_size == (6, 6)
        assert (default_touch_detect_device.taxels_array == np.zeros(
            shape=default_touch_detect_device.taxels_array_size)).all()

    def test_modify_taxel_array(self,
                                default_touch_detect_device,
                                mocker: MockerFixture):
        """Modify taxels with default array size.
        """
        # Arrange
        log_mock = mocker.patch("touch_detect_sdk.touch_detect_device.logging")
        log_mock.getLogger.return_value = logging.getLogger()

        # Act
        # the taxel array of an object shouldn't change.
        new_array = np.random.randint(
            0, 255, size=default_touch_detect_device.taxels_array_size)
        default_array_size = default_touch_detect_device.taxels_array_size
        default_touch_detect_device.taxels_array = new_array

        # Assert
        log_mock.error.assert_not_called()
        # Taxel should be resized and changed.
        assert default_touch_detect_device.taxels_array.shape == \
            default_array_size
        assert (default_touch_detect_device.taxels_array == new_array).all()

    def test_modify_taxel_array_different_size(self,
                                               default_touch_detect_device,
                                               mocker: MockerFixture):
        """Mofidy taxel values with different array size.
        """
        # Arrange
        log_mock = mocker.patch("touch_detect_sdk.touch_detect_device.logging")
        log_mock.getLogger.return_value = logging.getLogger()

        # Act
        # the taxel array of an object shouldn't change.
        default_array = default_touch_detect_device.taxels_array
        default_array_size = default_touch_detect_device.taxels_array_size
        default_touch_detect_device.taxels_array = TEST_TAXEL_8_X_8

        # Assert
        log_mock.error.assert_called_once_with(TEST_LOG_ERROR_1)
        # Taxel shouldn't be resized or changed.
        assert default_touch_detect_device.taxels_array.shape == \
            default_array_size
        assert (default_touch_detect_device.taxels_array ==
                default_array).all()


# pylint: enable=redefined-outer-name
