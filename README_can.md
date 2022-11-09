# CAN Touch SDK

## Table of Contents

* [README](#readme---can-touch-sdk)
    * [Table of Contents](#table-of-contents)
    * [About](#about)
    * [Prerequisites](#prerequisites)
    * [Run the demo](#run-the-demo)
    * [Use the SDK in your project](#use-the-sdk-in-your-project)

## About

This is the SDK for connecting to CAN TouchDetect sensor over UART USB Adapter.

## Prerequisites

The following requirements must be met in order to run the SDK.

### Python 3.8.9


* Download the [Python installer for windows](https://www.python.org/downloads/release/python-389/).


* Add python to PATH. This allows to execute python from **Powershell**. Follow [these steps](https://datatofish.com/add-python-to-windows-path/).


* [Install pip](https://phoenixnap.com/kb/install-pip-windows).

### Virtualenv (optional)

It is suggested to isolate the execution of python scripts. To do so:


* Install virtualenv

```bash
pip install virtualenv
```


* Create a new environment and start it:

```bash
# Create the environment
python -m virtualenv myenv

# Start the environment
.\myvenv\Scripts\activate
```


* Install all the dependencies required for running the SDK:

```bash
pip install -r requirements.txt
```

## Run the Demo

There is simple demo inside the **sample** folder. This helps you to understand how this library works. To run it:


* Open demo.py. Rename `CAN_DEVICE_NAME` to the device (port) you want to connect.


* Run the demo:

```bash
# Place inside can_touch_sdk
cd can_touch_sdk

# Run the demo
python .\sample\demo.py
```


* You will see that the demo will search for Can devices and list them like this:

```bash
Searching CAN devices ...
Found device: Virtual or Actual Serial
with Adress: COM3
Found device: Virtual or Actual Serial
with Adress: dev/ttyXX
Search finished. 2 device[s] found
```


* The demo will then try to connect to `CAN_DEVICE_NAME`. You will see a message like this:

```bash
INFO:root:Connecting to CAN device
serial communication opened on port: Com3
Successfully connected to COM3
```


* After connecting to the device, there will be a request on initialisation and if data acquisition hast started:

```bash
wait for sync | cycle # of 10
with maximum of 10 tries ; each second
```


* After sync is achieved, data acquisition can be performed with get_data()

    No data in the acquisition queue is deprecated by calling state of data_available()

```bash
-----------------------------
Time: 1.296625852584839
data: [ 000, 1355, 2365, 3219]
-----------------------------
```


* Finally it will disconnect from CAN device.

## Use the SDK In Your Project

To use this library:

* Organize your project with this structure:

```bash
├───can_touchdetect_sdk
└───your_app.py
```

* Inside `your_app.py` include the library:

```bash
from can_touch_sdk import CanTouchSdk
```

* Start using the SDK.
