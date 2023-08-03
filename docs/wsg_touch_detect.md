# WSG TouchDetect SDK

## Table of Contents

- [WSG TouchDetect SDK](#wsg-touchdetect-sdk)
  - [Table of Contents](#table-of-contents)
  - [About](#about)
  - [Prerequisites](#prerequisites)
  - [Run the demo](#run-the-demo)

## About

This section explains how to use WSG TouchDetect SDK to gather data from 2 TouchDetect connected to WSG gripper 50-110.

## Prerequisites

- Reffer to [README.md](README.md) to get a list of the requisites to use this library.
- You will need a script that must run in WSG gripper. This script reads the data and publishes over Ethernet connector.

## Run the demo

- Make sure that you follow **Prerequisites** in order to run the library.

- Enable the pipenv of the SDK

  ```bash
    # Start the environment
    pipenv shell
  ```

- Connect TouchDetect to the fingertips of the gripper. The connector is polarized so bear this in mind when installing the gripper.
- Connect Ethernet connector to a switch. Make sure that the PC that runs this SDK is also connected to the same switch. It is also possible to connect WSG gripper directly to the PC but this requires extra configuration in your PC. Refer to WSG gripper documentation for this.
- Power-up the gripper. A led should start blinking.
- From the PC, access to the web interface of the device. There, run the LUA script provided by PowerON.

- Once the script is running, run the WSG demo. Make sure that **WSG_IP** matches the one of the device.

  ```bash
    # Start the demo
    python.exe .\demo\wsg_demo.py
  ```

  After running this, the demo will connect to the gripper and start plotting the message `New data received` every time a new package arrives.
