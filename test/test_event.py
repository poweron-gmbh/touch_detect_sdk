#!/usr/bin/env python3

""" Tests for event.py class. """

from threading import Thread

from src.event import Event

DEFAULT_DESCRIPTION = 'Testing Event'
TEST_MESSAGE = 'test'


class Publisher(object):
    """Helper class for testing events
    """

    # Set event object in class declaration.
    event = Event(DEFAULT_DESCRIPTION)
    handler_1_data = 0
    handler_2_data = 0
    earg = None

    def fire_event(self, earg: object = None):
        """Fires the event of the class.

        :param earg: parameters to send through the event, defaults to None
        :type earg: object, optional
        """
        self.event(earg)


def handler_1(sender: object, earg : object):
    """ Handler for event
    """
    sender.handler_1_data += 1
    sender.earg = earg


def handler_2(sender: object, earg):
    """ Handler for event
    """
    sender.handler_2_data += 1
    sender.earg = earg


class TestEvent:
    """Test Event
    """

# pylint: disable=redefined-outer-name
    def test_create_default_device(self):
        """Create single event object
        """

        # Create and assert
        try:
            event = Event(DEFAULT_DESCRIPTION)
        except RuntimeError:
            assert False
        assert event

    def test_call_once(self):
        """Subscribe listener and call once
        """

        # Arrange
        uut = Publisher()
        uut.event += handler_1

        # Act
        uut.fire_event()

        # Assert
        assert uut.handler_1_data == 1
        assert not uut.earg

    def test_call_multiple_times(self):
        """Subscribe listener and call multiple times.
        """

        # Arrange
        uut = Publisher()
        uut.event += handler_1

        # Act
        uut.fire_event()
        uut.fire_event()
        uut.fire_event()

        # Assert
        assert uut.handler_1_data == 3
        assert not uut.earg

    def test_call_multiple_listeners(self):
        """Subscribe multiple subscribers.
        """

        # Arrange
        uut = Publisher()
        uut.event += handler_1
        uut.event += handler_2

        # Act
        uut.fire_event()
        uut.fire_event()

        # Assert
        assert uut.handler_1_data == 2
        assert uut.handler_2_data == 2
        assert not uut.earg

    def test_unsubscribe(self):
        """Subscribe to an event and check unsubscribing
        """

        # Arrange
        uut = Publisher()
        uut.event += handler_1
        uut.event += handler_2

        # Act
        uut.fire_event()
        uut.event -= handler_1
        uut.fire_event()

        # Assert
        # Handler 1 should be called only once
        assert uut.handler_1_data == 1
        # Handler 2 calls shouldn't be affected at all
        assert uut.handler_2_data == 2
        assert not uut.earg

    def test_call_arguments(self):
        """Sending parameters to subscriber
        """

        # Arrange
        uut = Publisher()
        uut.event += handler_1

        # Act
        uut.fire_event(TEST_MESSAGE)

        # Assert
        assert uut.handler_1_data == 1
        assert uut.earg == TEST_MESSAGE

        # Act
        uut.fire_event()

        # Assert
        assert uut.handler_1_data == 2
        assert not uut.earg

    def test_call_multiple_threads(self):
        """Triggering the event from different threads.
        """

        # Arrange
        uut = Publisher()
        uut.event += handler_1

        # Act. Trigger the event from different threads.
        Thread(target=(uut.fire_event())).start()
        Thread(target=(uut.fire_event(TEST_MESSAGE))).start()

        # Assert. The threads must be called in order.
        assert uut.handler_1_data == 2
        assert uut.earg == TEST_MESSAGE

# pylint: enable=redefined-outer-name
