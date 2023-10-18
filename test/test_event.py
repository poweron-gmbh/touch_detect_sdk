#!/usr/bin/env python3

""" Tests for event.py class. """

from threading import Thread

from touch_detect_sdk.event import Event, EventSuscriberInterface

DEFAULT_DESCRIPTION = 'Testing Event'
TEST_MESSAGE = 'test'


class Publisher():
    """Helper class for testing events
    """

    # Set event object in class declaration.
    event = Event(DEFAULT_DESCRIPTION)

    def fire_event(self, earg: object = None):
        """Fires the event of the class.

        :param earg: parameters to send through the event, defaults to None
        :type earg: object, optional
        """
        self.event(earg)


class Suscriber1(EventSuscriberInterface):
    """Suscriber for events.
    """

    def __init__(self):
        super().__init__()
        self.handler_data = 0
        self.earg = None

    def touch_detect_event(self, sender: object, earg: object):
        """Implement function function called on event
        """
        self.handler_data += 1
        self.earg = earg


class Suscriber2(EventSuscriberInterface):
    """Suscriber for events.
    """

    def __init__(self):
        super().__init__()
        self.handler_data = 0
        self.earg = None

    def touch_detect_event(self, sender: object, earg: object):
        """Implement function function called on event
        """
        self.handler_data += 1
        self.earg = earg


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
        suscriber_1 = Suscriber1()
        uut.event += suscriber_1

        # Act
        uut.fire_event()

        # Assert
        assert suscriber_1.handler_data == 1
        assert not suscriber_1.earg

    def test_call_multiple_times(self):
        """Subscribe listener and call multiple times.
        """

        # Arrange
        uut = Publisher()
        suscriber_1 = Suscriber1()
        uut.event += suscriber_1

        # Act
        uut.fire_event()
        uut.fire_event()
        uut.fire_event()

        # Assert
        assert suscriber_1.handler_data == 3
        assert not suscriber_1.earg

    def test_call_multiple_suscribers(self):
        """Subscribe multiple subscribers.
        """

        # Arrange
        uut = Publisher()
        suscriber_1 = Suscriber1()
        suscriber_2 = Suscriber2()

        uut.event += suscriber_1
        uut.event += suscriber_2

        # Act
        uut.fire_event()
        uut.fire_event()

        # Assert
        assert suscriber_1.handler_data == 2
        assert suscriber_2.handler_data == 2
        assert not suscriber_1.earg
        assert not suscriber_2.earg

    def test_unsubscribe(self):
        """Subscribe to an event and check unsubscribing
        """

        # Arrange
        uut = Publisher()
        suscriber_1 = Suscriber1()
        suscriber_2 = Suscriber2()

        uut.event += suscriber_1
        uut.event += suscriber_2

        # Act
        uut.fire_event()
        uut.event -= suscriber_1
        uut.fire_event()

        # Assert
        # Handler 1 should be called only once
        assert suscriber_1.handler_data == 1
        # Handler 2 calls shouldn't be affected at all
        assert suscriber_2.handler_data == 2

    def test_call_arguments(self):
        """Sending parameters to subscriber
        """

        # Arrange
        uut = Publisher()
        suscriber_1 = Suscriber1()
        uut.event += suscriber_1

        # Act
        uut.fire_event(TEST_MESSAGE)

        # Assert
        assert suscriber_1.handler_data == 1
        assert suscriber_1.earg == TEST_MESSAGE

        # Act
        uut.fire_event()

        # Assert
        assert suscriber_1.handler_data == 2
        assert not suscriber_1.earg

    def test_call_multiple_threads(self):
        """Triggering the event from different threads.
        """

        # Arrange
        uut = Publisher()
        suscriber_1 = Suscriber1()
        uut.event += suscriber_1

        # Act. Trigger the event from different threads.
        Thread(target=uut.fire_event()).start()
        Thread(target=uut.fire_event(TEST_MESSAGE)).start()

        # Assert. The threads must be called in order.
        assert suscriber_1.handler_data == 2
        assert suscriber_1.earg == TEST_MESSAGE

# pylint: enable=redefined-outer-name
