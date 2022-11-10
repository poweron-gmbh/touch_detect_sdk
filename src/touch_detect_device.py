#!/usr/bin/env python3

from enum import Enum, unique

import numpy as np


# TODO: change BleDevice and CanDevice to childs of TD Device

@unique
class TouchDetectModel(Enum):
    """Describes possible modes of TouchDetect.
    """
    VIRTUAL = 0
    CAN = 1
    BLE = 2


class TouchDetectDevice:
    """General Represents a TD Hardware device.
    """
    td_device_model_default = TouchDetectModel(0)

    def __init__(self,
                 name: str = None,
                 address: str = None,
                 model: TouchDetectModel = td_device_model_default,
                 array_xy: tuple = (6, 6)):
        """Initialize Object of TD.

        :param name:
        :type name:
        :param address:
        :type address:
        """
        # self._is_connected = False
        # self._connection_lost = False
        # self._acquisition_running = False
        self.connected = False
        self.connection_lost = False
        self.acquisition_running = False
        self.rotation = 0
        self.data_mirrorX = False
        self.data_mirrorY = False

        self._name = name
        self._address = address
        self._model = model
        self._arraysize = array_xy
        self._data = np.random.randint(0, 255, size=(10, 10))
        self._virt_c = [0, 0]
        self._virt_data = np.random.randint(0, 255, size=(10, 10))

    @property
    def name(self):
        """Name of the TD device Hardware
        :return: name of the device
        :rtype: str
        """
        return self._name

    @property
    def address(self):
        """Address of the TD device
        :return:
        :rtype:
        """
        return self._address

    @property
    def model(self):
        """Interface identification of the TD device
        :return:
        :rtype:
        """
        return self._model

    @property
    def arraySizeXY(self):
        """Size x, y of the node array of the TD device
        :return:
        :rtype:
        """
        return self._arraysize

    # @property
    # def acquisition_running(self):
    #     return self._acquisition_running
    #
    # @acquisition_running.setter
    # def acquisition_running(self, a: bool):
    #     self._acquisition_running = a

    @property
    def data(self) -> np.ndarray:
        """Current Data of the TD device
        :return: Data
        :rtype: np.ndarray
        """
        return self._data

    @data.setter
    def data(self, d):
        """Set Data to TD device in multithread applications
        :return:
        :rtype:
        """
        self._data = d

    def data_virtual(self):
        self._data = self._virt_data
        prev_act = 0
        prev2_act = 0
        next_act = 0
        d = self._data[self._virt_c[0]][self._virt_c[1]]
        if self._virt_c[1] != 0:
            prev_act = self._data[self._virt_c[0]][self._virt_c[1] - 1]
        else:
            if self._virt_c[0] != 0:
                prev_act = self._data[self._virt_c[0] - 1][5]
            else:
                prev_act = self._data[5][5]
        if self._virt_c[1] != 1:
            prev2_act = self._data[self._virt_c[0]][self._virt_c[1] - 2]
        else:
            if self._virt_c[0] != 0:
                prev2_act = self._data[self._virt_c[0] - 1][4]
            else:
                prev2_act = self._data[5][5]
        if self._virt_c[1] != 5:
            next_act = self._data[self._virt_c[0]][self._virt_c[1] + 1]
        else:
            if self._virt_c[0] != 5:
                next_act = self._data[self._virt_c[0] + 1][0]
            else:
                next_act = self._data[0][0]

        self._data = np.zeros(shape=(6, 6))
        if self._virt_c[1] != 5:
            self._data[self._virt_c[0]][self._virt_c[1] + 1] = d
        else:
            if self._virt_c[0] != 5:
                self._data[self._virt_c[0] + 1][0] = d
            else:
                self._data[0][0] = d
        self._data[self._virt_c[0]][self._virt_c[1]] = prev_act
        if self._virt_c[1] != 0:
            self._data[self._virt_c[0]][self._virt_c[1] - 1] = prev2_act
        else:
            if self._virt_c[0] != 0:
                self._data[self._virt_c[0] - 1][5] = prev2_act
            else:
                self._data[5][5] = prev2_act
        if self._virt_c[1] != 1:
            self._data[self._virt_c[0]][self._virt_c[1] - 2] = 0
        else:
            if self._virt_c[0] != 0:
                self._data[self._virt_c[0] - 1][4] = 0
            else:
                self._data[5][4] = 0

        if self._virt_c[0] == 0 and self._virt_c[1] == 0:
            self._data[5][4] = 0
            self._data[5][5] = int(4096 / 2)
            self._data[0][0] = 4096
            self._data[0][1] = int(4096 / 2)

        self._virt_c[1] += 1
        if self._virt_c[1] == 6:
            self._virt_c[1] = 0
            self._virt_c[0] += 1
            if self._virt_c[0] == 6:
                self._virt_c[0] = 0

        self._virt_data = self._data

    # @property
    # def connected(self):
    #     """Connection State of the TD device"""
    #     return self._is_connected
    #
    # @connected.setter
    # def connected(self, c):
    #     """Sets connection state to the TD device"""
    #     self._is_connected = c
    #
    # @property
    # def connection_lost(self):
    #     return self._connection_lost
    #
    # @connection_lost.setter
    # def connection_lost(self, c):
    #     self._connection_lost = c
