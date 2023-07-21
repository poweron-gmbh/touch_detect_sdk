#!/usr/bin/env python3

"""This demo simply connects to the sensor and gets data from it.
   It does not use any SDK.
"""

import logging
import sys
import time

import numpy as np

import serial
from serial.serialutil import SerialException

from yahdlc import (
    FRAME_ACK,
    FRAME_DATA,
    frame_data,
    get_data,
)


# Possible returning values of the script.
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

# Amount of samples to take from device.
N_SAMPLES = 1000
# Device port to connect.
SERIAL_PORT = 'COM26'

# Update rate to request new data.
UPDATE_RATE_SEC = 0.001
# Update rate of the loop for handling the communication.
LOOP_RATE_SEC = 0.010
# Min valid package size.
MIN_PACKAGE_SIZE = 6
# Size of sensor array.
ARRAY_SIZE = (6, 6)

# Default values for serial port.
DEFAULT_BAUDRATE = 115200
PARITY = serial.PARITY_NONE
STOP_BITS = serial.STOPBITS_ONE
BYTE_SIZE = 8
DEFAULT_TIMOUT_SEC = 0.5

# Definitions for building frame request.
START_FRAME = bytes(b'\x7e')
DEVICE_ADDRESS = bytes(b'\xff')
CONTROL = bytes(b'\x12')
COMMAND_GET_DATA = bytes(b'\x01') 
END_FRAME = bytes(b'\x7e')


def get_frame(port: serial.Serial, data_buffer: bytearray) -> bytes:
    """Process all the data comming from serial port. Filters the
    data into HDLC frames.

    :param port: Serial port to read data from.
    :type port: serial.Serial
    :param data_buffer: buffer required to store incomming data.
    :type data_buffer: bytearray
    :return: decoded frame.
    :rtype: bytes
    """
    # Read data when there is a package available
    if port.in_waiting != 0:
        # Read all the data available from serial port
        serial_data = port.read_all()
        # Append to data previously collected
        data_buffer.extend(serial_data)

    # Return if there is no data to process
    if len(data_buffer) < MIN_PACKAGE_SIZE:
        return

    # Find the start of the frame
    start_index = data_buffer.find(START_FRAME)
    if start_index == -1:
        # There is no starting frame, clear the whole buffer and return
        data_buffer.clear()
        return None
    elif start_index != 0:
        # Erase all the bytes that are before the start of the package
        data_buffer = data_buffer[start_index:]

    # If there are two consecutive start frames (end of one frame and start of the next one).
    # Remove the end frame
    if len(data_buffer) != 1 and data_buffer[1] == START_FRAME:
        data_buffer.pop(0)

    # Find the end of the frame. Ignore the start frame
    end_index = data_buffer.find(END_FRAME, 1)
    if end_index == -1:
        # There is starting frame but there is no end frame. Wait for the rest
        # of the data
        return None
    # There is a complete frame detected. remove it from buffer
    new_frame = bytearray()
    for _ in range(end_index + 1):
        new_frame.append(data_buffer.pop(0))

    # Check if address is correct
    if new_frame[1] != DEVICE_ADDRESS[0]:
        return None

    return bytes(new_frame)


def get_sensor_values(payload: bytes) -> np.array:
    """Transforms incomming data into frames

    :param payload: array of bytes to be process.
    :type payload: bytes
    :return: numpy array of size ARRAY_SIZE with the information converted.
    :rtype: np.array
    """
    taxel_array = np.zeros(shape=ARRAY_SIZE, dtype=int)
    max_row = ARRAY_SIZE[0]
    max_column = ARRAY_SIZE[1]
    for row in range(max_row):
        for column in range(max_column):
            index = (2 * row * max_column) + (2 * column)
            value = int(payload[index] | (
                payload[index + 1] << 8))
            taxel_array[row, column] = value
    return taxel_array


def main():
    # Stores the data comming from serial port.
    buffer = bytearray()
    # Amount of sucessful packages received from TouchDetect.
    communication_success_count = 0

    # Logger
    logger = logging.getLogger(__name__)
    # Set basic configurations for logging
    logging.basicConfig(encoding='utf-8', level=logging.INFO)

    # Port configurations.
    port = serial.Serial()
    port.port = SERIAL_PORT
    port.baudrate = DEFAULT_BAUDRATE
    port.parity = PARITY
    port.stopbits = STOP_BITS
    port.bytesize = BYTE_SIZE
    port.timeout = DEFAULT_TIMOUT_SEC

    # Attempt to open the port.
    try:
        port.open()
    except SerialException as error:
        logger.error("Could could not connect to Device: %s", error)
        return EXIT_SUCCESS

    for _ in range(N_SAMPLES):
        # Send a request.
        frame = frame_data(COMMAND_GET_DATA, FRAME_DATA, 1)
        start_time = time.time()
        port.write(frame)

        # Wait for a response.
        n_iterations = int(DEFAULT_TIMOUT_SEC / LOOP_RATE_SEC)
        itx = 0
        n_packages = 0
        packages = []

        # A successful request must be replied with one DATA_FRAME and one ACK_FRAME.
        while itx < n_iterations and n_packages != 2:
            # Get valid HDLC frame.
            new_hdlc_ = get_frame(port, buffer)
            # If there is a valid frame, decode and obtain the payload.
            if new_hdlc_:
                decoded_frame, _, _ = get_data(new_hdlc_)
                packages.append(decoded_frame)
                n_packages += 1
                itx = 0
            time.sleep(LOOP_RATE_SEC)
            itx += 1

        # If there was no timeout it means that two valid packages were returned.
        if itx < (n_iterations - 1):
            # reply with ACK.
            frame = frame_data('', FRAME_ACK, 5)
            port.write(frame)
            # Calculate elapsed time of the whole reading operation.
            timelapse = round(time.time() - start_time, 3)
            timelapse_str = str(timelapse)
            # Increase the amount of sucessful HDLC operation.
            communication_success_count += 1

            # Convert the payload into a numpy array.
            data_to_draw = get_sensor_values(packages[0])

            # Print the data of the nodes.
            sys.stdout.write(str(data_to_draw))
            print(f'\n reading operation took {timelapse_str} sec')
            sys.stdout.write('\n\n')
            sys.stdout.flush()
        else:
            logger.error('Timeout while waiting for response')

        time.sleep(UPDATE_RATE_SEC)

    logger.info('%d/%d packages were received correctly.',
                communication_success_count, N_SAMPLES)

    return EXIT_SUCCESS


if __name__ == '__main__':
    sys.exit(main())
