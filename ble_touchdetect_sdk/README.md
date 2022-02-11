# BLE Touch SDK

## Table of Contents

- [BLE Touch SDK](#ble-touch-sdk)
  - [Table of Contents](#table-of-contents)
  - [About](#about)
  - [Prerequisites](#prerequisites)
  - [Setup your environment](#setup-your-environment)
  - [Run the demo](#run-the-demo)
  - [Test the library](#test-the-library)
  - [Use the SDK in your project](#use-the-sdk-in-your-project)
  - [SDK documentation](#sdk-documentation)

## About

This is the SDK for connecting to BLE TouchDetect sensor.

## Prerequisites

- Install Python 3.8.9 (this project won't work on newer versions).
  - Download the [Python installer for windows](https://www.python.org/downloads/release/python-389/).
  - Add python to PATH. This allows to execute python from **Powershell**. Follow [these steps](https://datatofish.com/add-python-to-windows-path/).

- [Install pip](https://phoenixnap.com/kb/install-pip-windows).

- Install virtualenv. This tool allows to isolate and run the python scripts. To do so, just run:

```bash
pip install virtualenv
```

## Setup your environment

It is strongly suggested the use of virtual environments. To do so:

- Create a new environment and start it:

```bash
  # Create the environment
  python -m virtualenv myenv

  # Start the environment
  .\myvenv\Scripts\activate
```

- Install all the dependencies required for running the SDK:

```bash
  pip install -r requirements.txt
```

## Run the demo

There is simple demo inside the **sample** folder. This helps you to understand how this library works. To run it:

- Open test_ble_touch_sdk.py. Rename `BLE_DEVICE_NAME` to the device you want to connect.

- Run the demo:

```bash
# Place inside ble_touchdetect_sdk
cd ble_touch_detect_sdk

# Run the demo
python .\sample\demo.py 
```

- You will see that the demo will search for BLE devices and list them like this:

```bash
Searching BLE devices ...
Found device: 
with MAC: 4F:22:82:3B:86:8A
Found device: Galaxy Watch4 (0DEL)
with MAC: 68:63:FD:29:3B:E5
Found device: PWRON1
with MAC: CC:50:E3:A1:48:EA
Search finished. 3 device[s] found
```

- The demo will then try to connect to `BLE_DEVICE_NAME`. You will see a message like this:

```bash
INFO:root:Connected to BLE device
Successfully connnected to PWRON1
```

- After connecting to the device, it will retrieve data from TouchDetect:

```bash
-----------------------------
Time: 6.296625852584839
data: [850, 872, 874, 846, 614, 131, 307, 527, 353, 439, 620, 621, 566, 792, 994, 584, 71, 572, 396, 809, 224, 699, 153, 646, 316, 157, 721, 937, 34, 914, 914, 954, 665, 349, 552, 349]
-----------------------------
```

- Finally it will disconnect from BLE device.

## Test the library

There are also tests implemented for testing the correct behavior of the library. To do so, place inside `ble_touchdetect_sdk` folder:

- To run all tests at once, run:

```bash
pytest .\test\
```

- To run a speicif test, run:

```bash
pytest .\test\test_ble_touch_sdk.py
```

## Use the SDK in your project

To use this library:

- Organize your project with this structure:

```bash
├───ble_touchdetect_sdk
└───your_app.py
```

- Inside `your_app.py` include the library:

```bash
from ble_touchdetect_sdk import BleTouchSdk
```

- Start using the SDK.

## SDK documentation

For detailed information about the SDK, please check the [SDK documentation](/ble_touchdetect_sdk/docs/_build/html/index.html).