#!/usr/bin/python3

"""Library for implementing custom events in classes"""

from threading import Lock


class Event(object):
    """ Holds the information about the event
    """

    def __init__(self, doc: str = None):
        """Initialize the event

        :param doc: Description about the event, defaults to None
        :type doc: str, optional
        """
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        """Returns the event handler
        """
        if obj is None:
            return self
        return EventHandler(self, obj)

    def __set__(self, obj, value):
        """Setter for event handler
        """
        pass    # pylint: disable=unnecessary-pass


class EventHandler(object):
    """Handles events
    """

    def __init__(self, event: Event, obj: object):
        """Initialize EventHandler

        :param event: reference to the event that this instance belongs.
        :type event: Event
        :param obj: reference to the object this instance belongs.
        :type obj: object
        """
        self.event = event
        self.obj = obj

        self._lock = Lock()

    def add(self, func):
        """Add new event handler function.

        Event handler function must be defined like func(sender, earg).
        You can add handler also by using '+=' operator.
        """
        self._getfunctionlist().append(func)
        return self

    def remove(self, func):
        """Remove existing event handler function.

        You can remove handler also by using '-=' operator.
        """
        self._getfunctionlist().remove(func)
        return self

    def fire(self, earg=None):
        """Fire event and call all handler functions

        You can call EventHandler object itself like e(earg) instead of
        e.fire(earg).
        """
        for func in self._getfunctionlist():
            func(self.obj, earg)

    def _getfunctionlist(self):
        """ Get reference to internal attributes of the class
        """

        with self._lock:
            try:
                eventhandler = self.obj.__eventhandler__
            except AttributeError:
                eventhandler = self.obj.__eventhandler__ = {}
            return eventhandler.setdefault(self.event, [])

    __iadd__ = add
    __isub__ = remove
    __call__ = fire
