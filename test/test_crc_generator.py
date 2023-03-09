#!/usr/bin/env python3

""" Tests for Crc16Gernator class. """


from src.wsg_gripper_touch_sdk import Crc16Generator

TRANSACTION_ID = bytearray(b'\xaa\xaa')
PROTOCOL_ID = bytearray(b'\xaa\xbb')
TEST_PAYLOAD = bytearray(b'\x74\x65\x73\x74')
TEST_PAYLOAD_2 = bytearray(b'\x47\x6f\x6e\x7a\x61\x6c\x6f\x21')


class TestCrcGenerator:
    """Test CRC16 generator.
    """

# pylint: disable=redefined-outer-name
    def test_valid_frame(self):
        """Tests check_frame_format with 4 bytes of payload.
        """

        # Arrange
        header = bytearray()
        header += TRANSACTION_ID
        header += PROTOCOL_ID
        payload_size = len(TEST_PAYLOAD)
        header.append(payload_size & 0xFF)
        header.append((payload_size & 0xFF00) >> 8)

        # Act
        crc = Crc16Generator.checksum_update_crc16(header)
        crc = Crc16Generator.checksum_update_crc16(TEST_PAYLOAD, crc)

        # Assert
        assert payload_size == 4
        # this constant was taken from practical experimentation on WSG gripper.
        assert crc == 0xdd2e

    def test_valid_frame_2(self):
        """Tests check_frame_format with 8 bytes of payload.
        """

        # Arrange
        header = bytearray()
        header += TRANSACTION_ID
        header += PROTOCOL_ID
        payload_size = len(TEST_PAYLOAD_2)
        header.append(payload_size & 0xFF)
        header.append((payload_size & 0xFF00) >> 8)

        # Act
        crc = Crc16Generator.checksum_update_crc16(header)
        crc = Crc16Generator.checksum_update_crc16(TEST_PAYLOAD_2, crc)

        # Assert
        assert payload_size == 8
        # this constant was taken from practical experimentation on WSG gripper.
        assert crc == 0x746a


# pylint: enable=redefined-outer-name
