from setuptools import setup

setup(
    name='touchdetect',
    version='1.0',
    description='SDK for connecting to TouchDetect',
    author='Gonzalo Cervetti',
    author_email='gonzalo@poweron.one',
    packages=['touch_detect_sdk'],
    install_requires=['bleak', 'numpy', 'future', 'pyserial', 'pynput', 'python4yahdlc']
)