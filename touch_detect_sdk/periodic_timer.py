#!/usr/bin/env python3

"""This library creates a timer that calles periodically a function.
"""

from typing import Type
from threading import Event, Thread
import time


class PeriodicTimerSuscriber():
    """Interface for periodic timer suscriber.
    """

    def on_timer_event(self):
        """Event called on each period of the timer.
        """


class PeriodicTimer():
    """Set of utils for touch detect SDK
    """

    def __init__(self):
        self._thread = None
        self._stop_timer = Event()
        self._period = None
        self._target = None

    def start(self, target: Type[PeriodicTimerSuscriber], period: float):
        """Start the periodic timer.

        :param target: Target object to call on_timer_event.
        :type target: Type[PeriodicTimerSuscriber]
        :param period: period in sec in which the event is produced.
        :type period: float
        """
        # Set the target object and period.
        self._target = target
        self._period = period

        # Clear flag to stop timer.
        self._stop_timer.clear()

        # Create thread and start it.
        self._thread = Thread(target=self._run)
        self._thread.start()

    def stop(self):
        """Stop the periodic timer.
        """
        self._stop_timer.set()
        self._thread.join()

    def _run(self):
        """thread that runs the timer.
        """
        while not self._stop_timer.is_set():
            self._target.on_timer_event()
            start_time = time.perf_counter()
            current_time = start_time
            while (current_time - start_time) < self._period:
                current_time = time.perf_counter()
