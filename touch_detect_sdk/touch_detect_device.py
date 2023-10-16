#!/usr/bin/env python3

"""Base class for TouchDetect devices."""

from enum import Enum, unique

import logging
import threading
import numpy as np


@unique
class TouchDetectType(Enum):
    """Describes possible modes of TouchDetect.
    """
    VIRTUAL = 0
    CAN = 1
    BLE = 2
    TCP = 3
    SERIAL = 4


class ConnectionStatus(Enum):
    """Describes the connection status of touch detect.
    """
    DISCONNECTED = 0
    CONNECTED = 1
    CONNECTION_LOST = 2


class TouchDetectDevice(object):
    """Represents a Touch Detect device.
    """

    def __init__(self,
                 address: str = None,
                 name: str = None,
                 touch_detect_type: TouchDetectType = TouchDetectType.VIRTUAL,
                 taxels_array_size: tuple = (6, 6)):
        """Initialize TouchDetect.

        :param name: device name, defaults to None
        :type name: str, optional
        :param address: address of the device, defaults to None
        :type address: str, optional
        :param touch_detect_type: type of device, defaults to VIRTUAL
        :type touch_detect_type: TouchDetectType, optional
        :param taxels_array_size: size of the sensor array, defaults to (6, 6)
        :type taxels_array_size: tuple, optional
        """
        self._acquisition_running = False
        self._address = address
        self._connection_status = ConnectionStatus.DISCONNECTED
        self._name = name
        self._rotation = 0
        self._touch_detect_type = touch_detect_type
        self._taxels_array_size = taxels_array_size
        self._taxel_array = np.zeros(shape=self._taxels_array_size)

        # Lock for sharing variables across different threads.
        self._lock = threading.Lock()

        self._logger = logging.getLogger(__name__)

    @property
    def name(self) -> str:
        """Name of the TD device.
        :return: name of the device
        :rtype: str
        """
        with self._lock:
            return self._name

    @name.setter
    def name(self, data: str) -> None:
        """Set taxel data in touch detect.

        :param data: new data array.
        :type data: np.array
        """
        with self._lock:
            self._name = data

    @property
    def address(self) -> str:
        """Address of the TD device.
        :return: address of the device
        :rtype: str
        """
        with self._lock:
            return self._address

    @address.setter
    def address(self, data: str) -> str:
        """Set address in touch detect.

        :param data: new data array.
        :type data: np.array
        """
        with self._lock:
            self._address = data

    @property
    def device_type(self) -> TouchDetectType:
        """TouchDetect device type.
        :return: device type
        :rtype: TouchDetectType
        """
        with self._lock:
            return self._touch_detect_type

    @property
    def taxels_array_size(self) -> tuple:
        """Size x, y of the node array of the TD device.
        :return: size of array size.
        :rtype: tuple
        """
        with self._lock:
            return self._taxels_array_size

    @property
    def taxels_array(self) -> np.array:
        """returns information about taxel array.
        :return: taxel array.
        :rtype: np.ndarray
        """
        with self._lock:
            return self._taxel_array

    @taxels_array.setter
    def taxels_array(self, data: np.array) -> None:
        """Set taxel data in touch detect.

        :param data: new data array.
        :type data: np.array
        """
        with self._lock:
            if self._taxels_array_size != data.shape:
                logging.error(
                    '''Attempt to write touch_detect_device array
                     with different size.''')
                return
            self._taxel_array = data

    @property
    def connection_status(self) -> ConnectionStatus:
        """Status of connection of the device.
        :rtype: ConnectionStatus
        """
        with self._lock:
            return self._taxels_array_size

    @connection_status.setter
    def connection_status(self, data: ConnectionStatus) -> None:
        """Set connection status of device.

        :param data: new status.
        :type data: ConnectionStatus
        """
        with self._lock:
            self._connection_status = data

    @property
    def rotation(self) -> ConnectionStatus:
        """Status of connection of the device.
        :rtype: ConnectionStatus
        """
        with self._lock:
            return self._rotation

    @rotation.setter
    def rotation(self, data: int) -> None:
        """Set connection status of device.

        :param data: new status.
        :type data: ConnectionStatus
        """
        with self._lock:
            self._rotation = data

    @property
    def acquisition_running(self) -> bool:
        """Getter for acquisition running flag.
        :rtype: bool
        """
        with self._lock:
            return self._acquisition_running

    @acquisition_running.setter
    def acquisition_running(self, data: bool) -> None:
        """Setter for acquisition running flag.

        :param data: new status.
        :type data: bool
        """
        with self._lock:
            self._acquisition_running = data
