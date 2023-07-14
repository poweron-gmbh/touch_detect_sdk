#!/usr/bin/env python3

""" Tests for can_device.py class. """

import numpy as np
import pytest

from touch_detect_sdk.can_touch_sdk import CanFrameDecoder

TEST_VALID_FRAME_1 = bytearray(
    b'\xFF\x00\x53\x00\x02\x80\x41\x80\x6D\x80\x6C\x00\x45\x00\x04\x80\x6F\x80\x23\x80\x47\xFE')

TEST_VALID_FRAME_2 = bytearray(
    b'\xFF\x00\x53\x00\x06\x80\x2B\x80\x72\x80\x6B\x00\x45\x00\x04\x80\x6F\x80\x23\x80\x47\xFE')

TEST_MISSING_START_FRAME = bytearray(
    b'\x00\x53\x00\x02\x80\x38\x80\x6F\x80\x7B\x00\x45\x00\x04\x80\x6F\x80\x23\x80\x47\xFE')

TEST_MISSING_END_FRAME = bytearray(
    b'\xFF\x00\x53\x00\x02\x80\x38\x80\x6F\x80\x7B\x00\x45\x00\x04\x80\x6F\x80\x23\x80\x47')

TEST_EMBEDDED_FRAME_IN_MESSAGE = bytearray(
    b'\x6F\x80\x23\x80\x47\xFE\xFF\x00\x53\x00\x02\x80\x22\x80\x6F\x80\x5F\x00\x45\x00'
    b'\x04\x80\x6F\x80\x23\x80\x47\xFE\xFF\x00\x53\x00\x03\x80\x26')

TEST_VALID_PACKAGE = [
    bytearray(
        b'\xFF\x00\x53\x00\x00\x80\x16\x00\x01\x80\x62'
        b'\x00\x55\x00\x04\x80\x6F\x80\x23\x80\x47\xFE'),
    bytearray(
        b'\xFF\x00\x53\x00\x01\x80\x17\x80\x2C\x80\x30'
        b'\x00\x55\x00\x05\x80\x6F\x80\x23\x80\x47\xFE'),
    bytearray(
        b'\xFF\x00\x53\x00\x02\x80\x32\x80\x5C\x80\x73'
        b'\x00\x45\x00\x04\x80\x6F\x80\x23\x80\x47\xFE'),
    bytearray(
        b'\xFF\x00\x53\x00\x03\x80\x1B\x80\x3B\x80\x39'
        b'\x00\x55\x00\x05\x80\x6F\x80\x23\x80\x47\xFE'),
    bytearray(
        b'\xFF\x00\x53\x00\x04\x80\x2F\x80\x72\x80\x69'
        b'\x00\x45\x00\x04\x80\x6F\x80\x23\x80\x47\xFE'),
    bytearray(
        b'\xFF\x00\x53\x00\x05\x80\x24\x80\x3C\x80\x3E'
        b'\x00\x55\x00\x05\x80\x6F\x80\x23\x80\x47\xFE'),
    bytearray(
        b'\xFF\x00\x53\x00\x06\x80\x2D\x80\x5E\x80\x79'
        b'\x00\x45\x00\x04\x80\x6F\x80\x23\x80\x47\xFE'),
    bytearray(
        b'\xFF\x00\x53\x00\x07\x80\x25\x80\x2D\x80\x4C'
        b'\x00\x55\x00\x05\x80\x6F\x80\x23\x80\x47\xFE'),
    bytearray(
        b'\xFF\x00\x53\x00\x08\x80\x25\x00\x0C\x80\x78'
        b'\x00\x55\x00\x04\x80\x6F\x80\x23\x80\x47\xFE'),
    bytearray(
        b'\xFF\x00\x53\x00\x09\x80\x2D\x80\x31\x80\x3D'
        b'\x00\x55\x00\x05\x80\x6F\x80\x23\x80\x47\xFE'),
    bytearray(
        b'\xFF\x00\x53\x00\x0A\x80\x2C\x80\x78\x00\x02'
        b'\x00\x45\x00\x05\x80\x6F\x80\x23\x80\x47\xFE'),
    bytearray(
        b'\xFF\x00\x53\x00\x0B\x80\x31\x80\x4F\x80\x41'
        b'\x00\x55\x00\x05\x80\x6F\x80\x23\x80\x47\xFE')
]

# Represents the converted values of TEST_VALID_PACKAGE
TAXEL_ARRAY_OF_VALID_PACKAGE = np.array(
    ([0x596, 0x501, 0x4e2, 0x597, 0x5ac, 0x5b0],
     [0x5b2, 0x4dc, 0x4f3, 0x59b, 0x5bb, 0x5b9],
     [0x5af, 0x4f2, 0x4e9, 0x5a4, 0x5bc, 0x5be],
     [0x5ad, 0x4de, 0x4f9, 0x5a5, 0x5ad, 0x5cc],
     [0x5a5, 0x50c, 0x4f8, 0x5ad, 0x5b1, 0x5bd],
     [0x5ac, 0x4f8, 0x502, 0x5b1, 0x5cf, 0x5c1]))

# CAN Device ID of package 0.
DEVICE_ID = 0x300
# Amount of frames per package.
PACKAGE_SIZE = 12


class TestCanFrameDecoder:
    """Test CanTouchDetect SDK.
    """

# pylint: disable=redefined-outer-name
    def test_valid_frame(self):
        """Tests check_frame_format
        """
        # Assert for valid frames
        assert CanFrameDecoder.check_frame_format(TEST_VALID_FRAME_1)
        assert CanFrameDecoder.check_frame_format(TEST_VALID_FRAME_2)

        # Assert for frames too long
        assert not CanFrameDecoder.check_frame_format(
            TEST_EMBEDDED_FRAME_IN_MESSAGE)

        # Assert missing start of frame
        assert not CanFrameDecoder.check_frame_format(
            TEST_MISSING_START_FRAME)

        # Assert missing end of frame
        assert not CanFrameDecoder.check_frame_format(
            TEST_MISSING_END_FRAME)

    def test_get_frame_id(self):
        """Test decoding the frame ID of frames.
        """
        # Assert single frame
        assert CanFrameDecoder.get_frame_id(
            TEST_VALID_FRAME_1) == 0x302

        # Assert another single frame
        assert CanFrameDecoder.get_frame_id(
            TEST_VALID_FRAME_2) == 0x306

        # Assert one entire package of frames
        for index in range(PACKAGE_SIZE):
            assert CanFrameDecoder.get_frame_id(
                TEST_VALID_PACKAGE[index]) == (DEVICE_ID + index), 'frame ' + str(index) + ' failed'

    def test_is_starting_frame(self):
        """ Test is_starting_frame function
        """
        # Assert
        assert CanFrameDecoder.is_starting_frame(TEST_VALID_PACKAGE[0])
        assert not CanFrameDecoder.is_starting_frame(
            TEST_VALID_PACKAGE[1])
        assert not CanFrameDecoder.is_starting_frame(
            TEST_VALID_PACKAGE[-1])

    def test_make_byte(self):
        """Test make byte
        """
        # Assert
        assert CanFrameDecoder.make_byte(0x80, 0x6D) == 0xED
        assert CanFrameDecoder.make_byte(0x00, 0x45) == 0x45

        assert CanFrameDecoder.make_byte(
            TEST_VALID_FRAME_2[7], TEST_VALID_FRAME_2[8]) == 0xF2
        assert CanFrameDecoder.make_byte(
            TEST_VALID_FRAME_2[11], TEST_VALID_FRAME_2[12]) == 0x45

    def test_make_short(self):
        """Test make short
        """
        # Assert
        assert CanFrameDecoder.make_short(0x80, 0x6D) == 0x806D
        assert CanFrameDecoder.make_short(0x00, 0x45) == 0x0045

    def test_decode_package(self):
        """Test decode a valid package
        """
        # Act
        taxel_data = CanFrameDecoder.decode_package(TEST_VALID_PACKAGE)

        # Assert
        assert (taxel_data == TAXEL_ARRAY_OF_VALID_PACKAGE).all()

# pylint: enable=redefined-outer-name
