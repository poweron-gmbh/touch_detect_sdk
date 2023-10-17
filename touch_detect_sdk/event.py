#!/usr/bin/python3

"""Library for implementing custom events in classes"""

from threading import Lock


class EventSuscriberInterface():
    """Interface for event suscribers
    """

    def touch_detect_event(self, sender: object, earg: object):
        """Handles the event.
        """
        pass    # pylint: disable=unnecessary-pass


class Event():
    """ Class for handling events.
    """

    def __init__(self, doc: str = None):
        """Initialize the event

        :param doc: Description about the event, defaults to None
        :type doc: str, optional
        """
        self.__doc__ = doc
        self._lock = Lock()
        self._suscriber_list = []

    def _getfunctionlist(self) -> list:
        """ Get reference to internal attributes of the class

        :return: list of suscribers
        :rtype: list
        """

        with self._lock:
            return self._suscriber_list

    def __add__(self, func):
        """ Adds a suscriber to the event.
        """
        if isinstance(func, EventSuscriberInterface):
            self._getfunctionlist().append(func)
        else:
            raise TypeError('''Only EventSuscriberInterface
                            objects can be added to EventHandler''')
        return self

    def __sub__(self, func):
        """ Removes a suscriber from the event.
        """
        if func in self._getfunctionlist():
            self._getfunctionlist().remove(func)
            return self
        return self

    def __call__(self, earg=None):
        """Fire event and call all the suscribers.
        """
        for func in self._getfunctionlist():
            func.touch_detect_event(self, earg)
