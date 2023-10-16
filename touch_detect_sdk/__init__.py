# __init__.py
"""Main module for the touch_detect_sdk package."""

from .ble_device import BleDevice, BleEventType
from .ble_touch_sdk import BleTouchSdk
from .can_device import CanDevice
from .can_device import CanEventData, CanEventType
from .can_touch_sdk import CanTouchSdk
from .event import EventSuscriberInterface
from .serial_device import SerialDevice, SerialEventData, SerialEventType
from .serial_touch_detect_sdk import SerialTouchSdk
from .touch_detect_device import TouchDetectDevice
from .touch_detect_device import TouchDetectType
from .wsg_device import WsgDevice, WsgEventType

__all__ = ["BleDevice", "BleEventType", "BleTouchSdk",
           "CanDevice", "CanEventData", "CanEventType", "CanTouchSdk",
           "EventSuscriberInterface", "SerialDevice", "SerialEventData",
           "SerialEventType", "SerialTouchSdk", "TouchDetectDevice",
           "TouchDetectType", "WsgDevice", "WsgEventType"]
