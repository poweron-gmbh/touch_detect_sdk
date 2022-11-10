#!/usr/bin/env python3
import os
import sys
import glob
import time
import logging
from threading import Thread, Event, Lock
import asyncio
import serial  #pyserial

from .can_device import CanDevice  # noqa

# Amount of time to wait for connection
WAIT_CONNECTION_TIMEOUT = 5.0
# Format for logging.
LOGGING_FORMAT = '%(asctime)s %(user)-8s %(message)s'

# Amount of time to wait for discover new devices.
CAN_DISCOVER_TIMEOUT = 2.0
# Amount of time to wait for data changes in data loop.
CAN_UPDATE_LOOP_TIME = 0.010
# Minimal amount of time to wait for connection.
CAN_CHECK_CONNECTION_SEC = 0.05
# Size of the queue for incomming data.
DATA_QUEUE_SIZE = 60
# Maximum Size of Pre Readed Bytes before acquisition to sync SOF,EOF
CAN_PRE_DATA_SCREEN = 265


class CanTouchSdk:
    """This Class manages the communication with CAN devices over RS232 USB Adapter.
    """
    def __init__(self, logfile: str = None):
        """Initialize CAN TouchDetect SDK instance

        :param logfile: URL to the nasm installer, defaults to None
        :type logfile: str, optional
        """
        self._logger = None
        #self._logger = logging.getLogger(__name__)
        # @todo actual logging implementation
        if logfile:
            logging.basicConfig(
                filename=logfile, encoding='utf-8', level=logging.INFO)
        # List of devices found
        self._devices_found = []
        # Event loop for running incoming data callback.
        self._loop_can_data = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop_can_data)
        # Queue for sharing data.
        self._incoming_data_queue = asyncio.Queue(DATA_QUEUE_SIZE)
        self._incoming_data_buffer = []
        # Timestamp for calculating time between readings.
        self._timestamp_start = time.time()
        # Thread for processing incoming data.
        self._incoming_data_thread = None

        # Lock for protecting _can_client
        self._data_thread_lock = Lock()
        # Event for stopping incoming_data_thread.
        self._stop_notify_loop_event = Event()
        # Status of the CAN connection
        self._device_connected = False
        # Instance of can_device that is going to be connected.
        self._target_device = CanDevice()
        self._acquisition_running = False
        self._data_available = False

    def __del__(self):
        """Deconstrutor to ensure threads stopped and connection closed
        """
        if self._incoming_data_thread and self._incoming_data_thread.is_alive():
            self._stop_notify_loop_event.set()
            while self._incoming_data_thread.is_alive():
                time.sleep(CAN_UPDATE_LOOP_TIME)
            logging.info('Disconnected from CAN device')

    def data_available(self):
        """Check if data is available

        :return: TRUE if queue has data entries, FALSE otherwise
        :rtype: boolean
        """
        return self._data_available

    def acquisition_running(self):
        """Check if initialisation is done and communication is synced

        :return: TRUE if initialisation is done successfully and first message synchronization is valid, FALSE otherwise
        :rtype: boolean
        """
        return self._acquisition_running

    def search_devices(self):
        """Search Can devices on serial ports nearby

        :return: list of serial devices present
        :rtype: list
        """
        self._devices_found.clear()
        asyncio.run(self._discover())
        return self._devices_found

    def connect(self, device_name: str):
        """Connect to CAN UART device

        :param device_name: name of the serial port device to find
        :type device_name: str
        :return: TRUE if connection was successful, FALSE otherwise.
        :rtype: boolean
        """
        # Run discover if didn't run before.
        if not self._devices_found:
            asyncio.run(self._discover())

        # Get the can_device instance which is target for connection and communication.
        self._target_device = self._get_device(device_name)

        if not self._target_device:
            logging.warning('Device was not found')
            return False

        if self._is_connected():
            logging.warning('Already connected to a device')
            return False

        # Setting serial communication parameters
        self._serial_handle, s_parity, s_stop = 0, 0, 0
        s_port = self._target_device.name
        s_baud = self._target_device.baudrate
        if self._target_device.parity == 0:
           s_parity = serial.PARITY_NONE
        elif self._target_device.parity == 1:
            s_parity = serial.PARITY_ODD
        elif self._target_device.parity == 2:
            s_parity = serial.PARITY_EVEN
        if self._target_device.stopbit == 1:
            s_stop = serial.STOPBITS_ONE
        elif self._target_device.stopbit == 2:
            s_stop = serial.STOPBITS_TWO
        elif self._target_device.stopbit == 15:
            s_stop = serial.STOPBITS_ONE_POINT_FIVE

        # Open serial port to target device
        try:
            self._serial_handle = serial.Serial(
                port=s_port, baudrate=s_baud, parity=s_parity,
                bytesize=serial.EIGHTBITS)
        except (OSError, serial.SerialException):
            logging.info("Serial connection refused")
            pass
        # Clear input buffer and setting serial communication flags
        time.sleep(0.2)
        self._device_connected = True
        self._target_device.connected = True
        self._serial_handle.reset_input_buffer()
        self._serial_handle.setDTR(True)
        self._serial_handle.setRTS(True)

        try:
            self._stop_notify_loop_event.clear()
            # Start thread for getting data from CAN device
            self._incoming_data_thread = Thread(
                target=self._can_data_thread)
            return self._device_connected
        except Exception as e:
            logging.error(e)
            logging.error('Error connecting from CAN device')
            return False

    def disconnect(self):
        """Disconnects CAN TouchDetect and stops thread for getting data

        :return: TRUE if disconnection was successful, FALSE otherwise
        :rtype: boolean
        """
        if not self._device_connected:
            return False

        try:
            # Send the signal to stop the thread.
            self._stop_notify_loop_event.set()
            # Wait until connection thread finishes.
            while self._incoming_data_thread.is_alive():
                time.sleep(CAN_UPDATE_LOOP_TIME)
        except Exception as e:
            logging.error(e)
            logging.error('Error disconnecting from CAN device')
            return False

        try:
            self._serial_handle.close()
        except (OSError, serial.SerialException):
            logging.info('serial closing not possible')
            pass

        self._target_device.connected = False
        logging.info('Disconnected from CAN device')
        return True

    def start_acquisition(self):
        run = False
        with self._data_thread_lock:
            if self._incoming_data_thread and self._incoming_data_thread.is_alive():
                run = True
        if run:
            return
        try:
            # Start thread for getting data from device
            self._stop_notify_loop_event.clear()
            self._incoming_data_thread = Thread(
                target=self._can_data_thread)
            self._incoming_data_thread.start()
        except Exception as e:
            logging.error(e)
            logging.error('Error starting acquisition')
            return False

    def stop_acquisition(self):
        run = True
        with self._data_thread_lock:
            if not self._incoming_data_thread.is_alive():
                run = False
        if not run:
            return
        try:
            # Send the signal to stop the thread.
            self._stop_notify_loop_event.set()
            # Wait until connection thread finishes.
            while self._incoming_data_thread.is_alive():
                time.sleep(CAN_UPDATE_LOOP_TIME)
            self._serial_handle.setDTR(True)
            self._serial_handle.setRTS(True)
        except Exception as e:
            logging.error(e)
            return False

    def single_acquisition(self):
        if self._device_connected:
            self.start_acquisition()
            time.sleep(0.5)
            d = self.get_data()
            self.stop_acquisition()
            return d

    def get_data(self):
        """Get latest data from queue.

        :return: Timestamp and additional Data_list [ID, Node_1_data, Node_2_data, Node_3_data]
        :rtype: list
        """
        if not self._is_connected():
            logging.info('Data thread not running. Call connect() first.')
            return None
        data = None
        with self._data_thread_lock:
            if self._incoming_data_queue.empty():
                if self._data_available:
                    self._data_available = False
                logging.info('No data from CAN device.')
            else:
                data =self._incoming_data_queue.get_nowait()
        return data

    def _is_connected(self):
        """Check if CAN device is connected.

        :return: TRUE if SDK is connected to device, FALSE otherwise.
        :rtype: boolean
        """        
        with self._data_thread_lock:
            if self._incoming_data_thread and self._incoming_data_thread.is_alive() and self._device_connected:
                return True
            return False

    def _get_device(self, device_name: str) -> CanDevice:
        """Returns the CAN device object of device_name.
        For running this function you should call first
        _discover().

        :param device_name: Name of the CAN device to find
        :type device_name: str
        :return: Object of can_device for device_name, None
            otherwise
        :rtype: CanDevice
        """
        if not self._devices_found:
            logging.error('No devices found. Call search_devices() first')
            return None

        for device in self._devices_found:
            if device.name == device_name:
                return device

    async def _wait_for_connection(self):
        """Blocks execution of thread until connection is reached.

        :return: TRUE if connection is successful, FALSE otherwise.
        :rtype: boolean
        """        
        n_loops = int(WAIT_CONNECTION_TIMEOUT / CAN_CHECK_CONNECTION_SEC)
        for _ in range(n_loops):
            if self._is_connected():
                return True
            await asyncio.sleep(CAN_CHECK_CONNECTION_SEC)
        return False

    async def _discover(self):
        """Search CAN devices nearby.
        """
        # maybe change to newer function call of lib
        if sys.platform.startswith("win"):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                can_device = CanDevice(port, port)
                # TODO: incorperate Can Start ID request for __init of CanDecive
                self._devices_found.append(can_device)
            except (OSError, serial.SerialException):
                pass

    def _can_data_thread(self):
        """Start loop for gathering data from CAN device
        """
        self._loop_can_data.run_until_complete(self._can_loop())

    def _can_data_callback(self, sender, data):
        """Callback for getting CAN data.
        not used at the moment
        """
        # Process incoming data and send it to queue.
        data_length = int(len(data) / 2)
        data_values = []
        for index in range(data_length):
            data_values.append(
                int(data[index * 2] * 256 + data[index * 2 + 1]))
        timestamp = time.time() - self._timestamp_start
        # Empty queue before adding new element.
        with self._data_thread_lock:
            if self._incoming_data_queue.full():
                while self._incoming_data_queue.full():
                    self._incoming_data_queue.get_nowait()
        self._incoming_data_queue.put_nowait((timestamp, data_values))

    async def _can_loop(self):
        """Initialisation of connection and loop for getting data from CAN.
        """

        # Pre data routine for asure synchronization in 22 byte reading
        data_h, pre_count = 0, 0
        self._serial_handle.reset_input_buffer()
        self._serial_handle.setDTR(False)
        self._serial_handle.setRTS(False)
        while not self._acquisition_running:
            pre_count += 1
            data_h = self._serial_handle.read(size=22)
            # if (data_h[0] == b'\xff') and (data_h[21] == b'\xfe'):
            if (data_h[0] == 255) and (data_h[21] == 254):
                self._acquisition_running = True
            if pre_count == CAN_PRE_DATA_SCREEN:
                break
        if not self._acquisition_running:
            logging.error('Synchronization fail - Check manually if device is reachable and Data incoming')

        # preparing buffer size [timestamp, [node_1_data, ... , node_n_data]
        self._incoming_data_buffer = [0, [0]*(self._target_device.arraySizeXY[0]*self._target_device.arraySizeXY[1])]
        can_start_id = self._target_device.can_id
        # starting data buffer loop
        while not self._stop_notify_loop_event.is_set():
            while not self._serial_handle.in_waiting >= 22:
                time.sleep(0.01)
            # data_h = serial_handle.read(size=22).hex()
            data_h = self._serial_handle.read(size=22)

            # debug readable serial messages coming in and print
            #data_h_bytes = ''.join('\\x{:02x}'.format(byte) for byte in data_h)
            #print(data_h_bytes)

            # handling of calculation refactoring data from message
            sof = data_h[0]
            dlc = ((data_h[1] & 0b10000000) + (data_h[2] & 0b01110000)) >> 4
            # TODO: check old: sens_id = ((data_h[2] & 0b00001111) << 4)
            #  + ((data_h[3] & 0b10000000) + (data_h[4] & 0b01111111))
            can_start_id = (data_h[2] & 0b00001111)*100
            sens_id = ((data_h[2] & 0b00001111) << 4) +\
                      ((data_h[3] & 0b10000000) + (data_h[4] & 0b01111111))
            node_1 = ((data_h[12] & 0b00001111) << 8) +\
                     ((data_h[5] & 0b10000000) + (data_h[6] & 0b011111111))
            node_2 = (((data_h[11] & 0b10000000) + (data_h[12] & 0b01110000)) << 4) +\
                     ((data_h[7] & 0b10000000) + (data_h[8] & 0b011111111))
            node_3 = ((data_h[14] & 0b00001111) << 8) +\
                     ((data_h[9] & 0b10000000) + (data_h[10] & 0b011111111))
            eof = data_h[21]
            # print('SOF: {0} || DLC: {1} || Sensor_ID: {2} || Node_1: {3} || Node_2: {4} || Node_3: {5} || EOF: {6}'.format(sof, dlc, sens_id, node_1, node_2, node_3, eof))

            timestamp = time.time() - self._timestamp_start
            # DEPRECATED - stores each message aka 3 nodes plus time in queue
            # # Empty queue before adding new element.
            # if self._incoming_data_queue.full():
            #     while self._incoming_data_queue.full():
            #         self._incoming_data_queue.get_nowait()
            # # Put message as data in the queue
            # #self._incoming_data_queue.put_nowait((timestamp, data_h))
            # # Put data as ID and measured data for the nodes only in the queue
            # data_values = [sens_id, node_1, node_2, node_3]
            # self._incoming_data_queue.put_nowait((timestamp, data_values))
            # self._data_available = True

            # NEW - stores nodes_data per ID in buffer queue
            first_node = sens_id - can_start_id  # maybe "and 0b00000011" or something like sens_id - canID
            self._incoming_data_buffer[0] = timestamp
            self._incoming_data_buffer[1][(first_node * 3)] = node_1
            self._incoming_data_buffer[1][(first_node * 3) + 1] = node_2
            self._incoming_data_buffer[1][(first_node * 3) + 2] = node_3
            # write to queue if last node reached - full sensor array read
            # if first_node+2 == ((self._target_device.arraySizeXY[0]/3) * self._target_device.arraySizeXY[1])-1

            with self._data_thread_lock:
                # Empty queue before adding new element.
                if self._incoming_data_queue.full():
                    while self._incoming_data_queue.full():
                        self._incoming_data_queue.get_nowait()
                # Put message as data in the queue
                # self._incoming_data_queue.put_nowait((timestamp, data_h))

                self._incoming_data_queue.put_nowait(self._incoming_data_buffer)
                self.data_available = True

        self._acquisition_running = False
