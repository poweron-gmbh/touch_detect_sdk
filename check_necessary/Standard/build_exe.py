from genericpath import exists
import PyInstaller.__main__
from os import path
import os

def main():

    py_file = 'main.py'            # Name of Python file to be converted 
    exe_name = 'BLE_GUI.exe'       # Name of executible file

    PyInstaller.__main__.run([
        py_file,
        '--clean',
        '--onefile',
        '--add-data=..\\resources\\Element_64x.png;resources',
        '--add-data=..\\resources\\Logo_PWN_TM3.png;resources',
        '--icon=..\\resources\\logo.ico'
    ])

    old_exe_name = py_file.split(".")[0] + ".exe"

    dirname = path.dirname(__file__)
    old_exe = path.join(dirname, 'dist/' + old_exe_name)
    new_exe = path.join(dirname, 'dist/' + exe_name)

    if exists(new_exe):
        print("Removing: {}".format(exe_name))
        os.remove(new_exe)

    print("Renaming executible {} to {}...".format(old_exe_name, exe_name))
    os.rename(old_exe, new_exe)

    print("Done")


if __name__ == "__main__":
    main()