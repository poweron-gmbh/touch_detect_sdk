# BLE TouchDetect SDK

## Table of Contents

- [BLE TouchDetect SDK](#ble-touchdetect-sdk)
  - [Table of Contents](#table-of-contents)
  - [About](#about)
  - [Prerequisites](#prerequisites)
  - [Run the demo](#run-the-demo)

## About

This section explains how to use PowerON TouchDetect SDK to connect to BLE sensors.

## Prerequisites

Reffer to [README.md](README.md) to get a list of the requisites to use this library.

## Run the demo

- Make sure that you follow **Prerequisites** in order to run the library.

- Enable the pipenv of the SDK

  ```bash
    # Start the environment
    pipenv shell
  ```

- Turn on BLETouchDetect. The device will turn on one red led while blinking a green led. The device will enter in **Visible** mode and can be found by your PC. This mode will last only 30 seconds. After that, it will enter in **deep sleep mode** forcing the user to restart it.

- While BLE is blinking, run the demo

  ```bash
    # Start the demo.
    python.exe .\demo\ble_demo.py
  ```

  The script will search for BLE devices and will connect to the device with the name **BLE_DEVICE_NAME**. Once the connection was stablished, it will publish in the console the ADC value of each taxel node.
