#!/usr/bin/env python3

""" Tests for Serial touch detect SDK """

from touch_detect_sdk.touch_detect_utils import TouchDetectUtils
from .test_data.sensor_data import (
    TEST_RAW_SENSOR_DATA,
    TEST_CONVERTED_TAXEL_DATA
)

TRANSACTION_ID = bytearray(b'\xaa\xaa')
PROTOCOL_ID = bytearray(b'\xaa\xbb')
TEST_PAYLOAD = bytearray(b'\x74\x65\x73\x74')
TEST_PAYLOAD_2 = bytearray(b'\x47\x6f\x6e\x7a\x61\x6c\x6f\x21')

START_FRAME = bytearray(b'\x7e')
DEVICE_ADDRESS = bytearray(b'\xff')
CONTROL = bytearray(b'\x12')
COMMAND_GET_DATA = bytearray(b'\x01')
DEVICE_ADDRESS = bytearray(b'\xff')
END_FRAME = bytearray(b'\x7e')

# sensor array data split in pairs of 8bit.
TEST_RAW_SENSOR_DATA_2 = bytes(
    b'\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00\x06\x00'
    b'\x01\x01\x02\x01\x03\x01\x04\x01\x05\x01\x06\x01'
    b'\x01\x02\x02\x02\x03\x02\x04\x02\x05\x02\x06\x02'
    b'\x01\x03\x02\x03\x03\x03\x04\x03\x05\x03\x06\x03'
    b'\x01\x04\x02\x04\x03\x04\x04\x04\x05\x04\x06\x04'
    b'\x01\x05\x02\x05\x03\x05\x04\x05\x05\x05\x06')


class TestTouchDetectUtils:
    """Test SerialTouchDetectSdk
    """

# pylint: disable=redefined-outer-name
    def test_to_taxel_array_right_size(self):
        """Convert array with correct size.
        """
        # Arrange
        uut = TouchDetectUtils()

        # Act
        frame = uut.to_taxel_array((6, 6), TEST_RAW_SENSOR_DATA)

        # Assert
        assert (frame == TEST_CONVERTED_TAXEL_DATA).all()

    def test_to_taxel_array_wrong_size(self):
        """Convert array with wrong size.
        """
        # Arrange
        uut = TouchDetectUtils()

        # Act
        frame = uut.to_taxel_array((6, 6), TEST_RAW_SENSOR_DATA_2)

        # Assert
        assert not frame

    def test_valid_frame(self):
        """Tests check_frame_format with 1 byte of payload.
        """

        # Arrange
        uut = TouchDetectUtils()
        header = bytearray()
        # header += START_FRAME
        header += DEVICE_ADDRESS
        header += CONTROL
        header += COMMAND_GET_DATA

        # Act
        crc = uut.checksum_update_crc16(header)

        # this constant was taken from practical experimentation
        # on SerialTouchDetect.
        assert crc == 0xb1e6

    def test_valid_frame_2(self):
        """Tests check_frame_format with 4 bytes of payload.
        """

        # Arrange
        uut = TouchDetectUtils()
        header = bytearray()
        header += TRANSACTION_ID
        header += PROTOCOL_ID
        payload_size = len(TEST_PAYLOAD)
        header.append(payload_size & 0xFF)
        header.append((payload_size & 0xFF00) >> 8)

        # Act
        crc = uut.checksum_update_crc16(header)
        crc = uut.checksum_update_crc16(TEST_PAYLOAD, crc)

        # Assert
        assert payload_size == 4
        # this constant was taken from practical experimentation
        # on WSG gripper.
        assert crc == 0xdd2e

    def test_valid_frame_3(self):
        """Tests check_frame_format with 8 bytes of payload.
        """

        # Arrange
        uut = TouchDetectUtils()
        header = bytearray()
        header += TRANSACTION_ID
        header += PROTOCOL_ID
        payload_size = len(TEST_PAYLOAD_2)
        header.append(payload_size & 0xFF)
        header.append((payload_size & 0xFF00) >> 8)

        # Act
        crc = uut.checksum_update_crc16(header)
        crc = uut.checksum_update_crc16(TEST_PAYLOAD_2, crc)

        # Assert
        assert payload_size == 8
        # this constant was taken from practical experimentation
        # on WSG gripper.
        assert crc == 0x746a


# pylint: enable=redefined-outer-name
