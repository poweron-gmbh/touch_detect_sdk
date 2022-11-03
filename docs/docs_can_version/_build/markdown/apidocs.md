# API Documentation


### _class_ can_touch_sdk.CanTouchSdk(logfile: Optional[str] = None)
This Class manages the communication with CAN devices over RS232 USB Adapter.


#### acquisition_running()
Check if initialisation is done and communication is synced


* **Returns**

    TRUE if initialisation is done successfully and first message synchronization is valid, FALSE otherwise



* **Return type**

    boolean



#### connect(device_name: str)
Connect to CAN UART device


* **Parameters**

    **device_name** (*str*) – name of the serial port device to find



* **Returns**

    TRUE if connection was successful, FALSE otherwise.



* **Return type**

    boolean



#### data_available()
Check if data is available


* **Returns**

    TRUE if queue has data entries, FALSE otherwise



* **Return type**

    boolean



#### disconnect()
Disconnects CAN TouchDetect and stops thread for getting data


* **Returns**

    TRUE if disconnection was successful, FALSE otherwise



* **Return type**

    boolean



#### get_data()
Get latest data from queue.


* **Returns**

    Timestamp and additional Data_list [ID, Node_1_data, Node_2_data, Node_3_data]



* **Return type**

    list



#### search_devices()
Search Can devices on serial ports nearby


* **Returns**

    list of serial devices present



* **Return type**

    list



### _class_ can_device.CanDevice(name: Optional[str] = None, address: Optional[str] = None)
Represents a CAN UART device.


#### _property_ address()
Address of the CAN device


* **Returns**

    Address of the CAN devices port



* **Default**

    None



* **Return type**

    str



#### _property_ baudrate()
Baudrate of the serial interface


* **Returns**

    Baudrate of the CAN devices serial communication



* **Default**

    1000000



* **Return type**

    int



#### _property_ bytesize()
Bytesize of the serial interface


* **Returns**

    Bytesize of the CAN devices serial communication



* **Default**

    8



* **Return type**

    int



#### _property_ name()
Name of the CAN device | port


* **Returns**

    name of the devices port



* **Return type**

    str



#### _property_ parity()
Parity of the serial interface


* **Returns**

    Parity of the CAN devices serial communication



* **Default**

    0  | indicates pyserial.PARITY_NONE



* **Return type**

    int



#### _property_ stopbit()
Stopbit of the serial interface


* **Returns**

    Stopbit of the CAN devices serial communication



* **Default**

    1 | indicates pyserial.STOPBITS_ONE



* **Return type**

    int
