#!/usr/bin/env python3

from distutils.core import setup

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license_ = f.read()

setup(
    name='can_touchdetect_sdk',
    version='0.1.0',
    description='SDK for interfacing CAN TouchDetect over USB RS232 adapter',
    long_description=readme,
    author='Sascha Teutoburg-Weiss',
    author_email='sascha@poweron.one',
    url='https://www.poweron.one/#section-technology',
    license=license_
)