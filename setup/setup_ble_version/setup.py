#!/usr/bin/env python3

from distutils.core import setup

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='ble_touchdetect_sdk',
    version='0.1.0',
    description='SDK for interfacing BLE TouchDetect',
    long_description=readme,
    author='Gonzalo Cervetti',
    author_email='gonzalo@poweron.one',
    url='https://www.poweron.one/#section-technology',
    license=license
)