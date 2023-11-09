#!/usr/bin/env python3

""" Tests for Serial touch detect SDK """

import math
import time

import pytest

from touch_detect_sdk.periodic_timer import PeriodicTimer, \
    PeriodicTimerSuscriber

TEST_PERIOD = 0.020
TEST_TIMER_RUNNING_TIME = 3.0
MAX_ERROR_PERCENTAGE = 2.0


class MockPeriodicTimerSuscriber(PeriodicTimerSuscriber):
    """Mock class for PeriodicTimerSuscriber.
    """
    def __init__(self) -> None:
        super().__init__()
        self.callback_count = 0

    def on_timer_event(self):
        """Mock function for on_timer_event.
        """
        self.callback_count += 1


@pytest.fixture
def default_periodic_timer():
    """Setup unit under test.
    """
    uut = PeriodicTimer()
    yield uut
    del uut


class TestPeriodicTimer:
    """Test PeriodicTimer class.
    """

# pylint: disable=redefined-outer-name

    def test_create_default_timer(self):
        """Create a default object.
        """

        # Arrange
        uut = PeriodicTimer()

        # Assert
        assert uut

    def test_suscribe_and_run(self, default_periodic_timer):
        """Suscribe mock and check if is called the right amount of times.
        """
        # Arrange
        suscriber_mock = MockPeriodicTimerSuscriber()

        # Act
        default_periodic_timer.start(suscriber_mock, TEST_PERIOD)
        time.sleep(TEST_TIMER_RUNNING_TIME)
        default_periodic_timer.stop()

        # Assert
        error = abs((float(suscriber_mock.callback_count) /
                    (TEST_TIMER_RUNNING_TIME / TEST_PERIOD) - 1.0) * 100.0)
        error = math.floor(error)
        assert error <= MAX_ERROR_PERCENTAGE

# # pylint: enable=redefined-outer-name
