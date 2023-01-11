# Touch Detect SDK

## Table of Contents

- [Touch Detect SDK](#touch-detect-sdk)
  - [Table of Contents](#table-of-contents)
  - [About](#about)
  - [Project structure](#project-structure)
  - [Prerequisites](#prerequisites)
  - [Initialize the environment](#initialize-the-environment)
  - [Run the demos](#run-the-demos)
  - [Test the library](#test-the-library)
  - [Documentation](#documentation)

## About

This software development kit (SDK) handles the communication to Touch Detect devices. It supports BLE and CAN devices.

## Project structure

- demo: simple individual examples to show how the library works.
- docs: documentation about the SDK.
- resources: files and documents required by the project.
- src: source code of the app.
- test: tests for each of the elements.

## Prerequisites

- Install Python 3.9.0:
  - Download the [Python installer for windows](https://www.python.org/downloads/release/python-390/).
  - Add python to PATH. This allows to execute python from **Powershell**. Follow [these steps](https://datatofish.com/add-python-to-windows-path/).

- [Install pip](https://phoenixnap.com/kb/install-pip-windows).

- Install pipenv. This tool allows to isolate and run the python scripts. Just run:

  ```bash
  pip install pipenv
  ```

## Initialize the environment

- It is strongly suggested to use pipenv. This tool isolates the execution of the code and provides all the necessary dependencies to make it work. This repo provides a **pipenv** ready to use. To activate the environment, simply run:

  ```bash
    # Start the environment
    pipenv shell
  ```

## Run the demos

There are a set of demos under [demo](demo) folder. To run the demos run the following snippet:

  ```bash
    # Place yourself inside the root folder
    cd poweron-touchdetect-sdk

    # Run one of the demos
    py.exe .\demo\DEMO_NAME.py
  ```

## Test the library

There are also tests implemented for checking the correct behaviour of the library. To do so, simply run:

- To run all tests at once, run:

    ```bash
    # Place yourself inside the root folder
    cd poweron-touchdetect-sdk

    # Run one of the tests
    pytest.exe .\test\test_TEST_NAME.py

    # Run all tests togheter
    pytest.exe .\test
  ```

- To run a specific test, run:

## Use the SDK in your project

To use this library:

- Organize your project with this structure:

  ```bash
  ├───ble_touchdetect_sdk
  └───your_app.py
  ```

- Inside `your_app.py` include one of the libraries:

  ```bash
  from ble_touchdetect_sdk import BleTouchSdk
  ```

- Start using the SDK.

## Documentation

Detailed documentation of this project can be found [here](docs)
