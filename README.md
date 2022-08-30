# BLE Touch Detect Software

## Table of Contents

- [BLE Touch Detect Software](#ble-touch-detect-software)
  - [Table of Contents](#table-of-contents)
  - [About](#about)
  - [Repo structure](#repo-structure)
  - [PC software](#pc-software)
    - [Prerequisites](#prerequisites)
    - [Running the GUI's from console](#running-the-guis-from-console)
    - [Building executibles](#building-executible-program)
    - [Running the GUI's from pycharm](#running-the-guis-from-pycharm)
    - [Problems running the GUI's](#problems-running-the-guis)
    - [Known issues](#known-issues)

## About

This repo contains the PC software for connecting to the device.

## Repo structure

You can find here a brief description of how the project is organized:

- [standard](Standard): contains the main PC programm.

- [demo_version](demo_version): similar to standard version, but does not include numeric information about ADC.

- [interfacing_uoa_ble_device](interfacing_uoa_ble_device): 

- [resources](resources): useful documents related to the project.

- [ble_touchdetect_sdk](/ble_touchdetect_sdk/README.md): SDK library for interfacing BLE TouchDetect.

## PC software

### Prerequisites

- Install Python 3.8.9 (this project won't work on newer versions).
  - Download **Windows installer** from [here](https://www.python.org/downloads/release/python-389/).
  - Add python to PATH: this allows to execute python from **Powershell**. Follow [these steps](https://datatofish.com/add-python-to-windows-path/).

- [Install pip](https://phoenixnap.com/kb/install-pip-windows).

- Install pipenv. This tool allows to isolate and run the python scripts. Just run:

```bash
pip install pipenv
```

### Running the GUI's from console

- Open Powershell inside the folder of the GUI you want to run.
  - To do so, open File explorer and navigate inside the folder of the GUI (For example, place inside `Standard` folder).
  - Press `Shift + Right click`. You should see some option like `Open PowerShell window here`.

- Create a new environment and install all the dependencies required for running the GUI:

```bash
  # Create the environment
  py -m pipenv install
```

- Start pipenv

```bash
py -m pipenv shell
```

- Run the app:

```bash
  py main.py 
```

- To exit the `pipenv` type

```bash
  exit
```

### Building executible program 

- Open Powershell inside the folder of the GUI you want to build.
  - To do so, open File explorer and navigate inside the folder of the GUI (For example, place inside `Standard` folder).
  - Press `Shift + Right click`. You should see some option like `Open PowerShell window here`.

- Create a new environment and install all the dependencies required for running the GUI:

```bash
  # Create the environment
  py -m pipenv install
```

- Start pipenv

```bash
py -m pipenv shell
```

- Run the app:

```bash
  py build_exe.py
```

- The executible file will be generated and store in the dist/ To run the executible, double click it.

To exit the `pipenv` type

```bash
  exit
```

### Running the GUI's from pycharm

- Follow the [Getting started with BLE Sensor Python GUI](/resources/Getting%20started%20with%20BLE%20Sensor%20Python%20GUI.docx) document.


### Problems running the GUI's

- `execution of scripts is disabled on this system.`
  - Take a look to [this solution](https://stackoverflow.com/questions/4037939/powershell-says-execution-of-scripts-is-disabled-on-this-system#:~:text=Go%20to%20Start%20Menu%20and,Choose%20%22Yes%22.).

### Known issues

- If GUI losses connection with the BLE device, it will stop working.
