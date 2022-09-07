Run the demo
============

There is simple demo inside the **sample** folder. This helps you to understand how this library works. To run it:

-  Open demo.py. Rename :file:`CAN_DEVICE_NAME` to the device (port) you want to connect.

-  Run the demo:

.. code-block:: bash

   # Place inside can_touch_sdk
   cd can_touch_sdk

   # Run the demo
   python .\sample\demo.py 

- You will see that the demo will search for Can devices and list them like this:

.. code-block:: bash

    Searching CAN devices ...
    Found device: Virtual or Actual Serial
    with Adress: COM3
    Found device: Virtual or Actual Serial
    with Adress: dev/ttyXX
    Search finished. 2 device[s] found


- The demo will then try to connect to :file:`CAN_DEVICE_NAME`. You will see a message like this:

.. code-block:: bash

    INFO:root:Connecting to CAN device
    serial communication opened on port: Com3
    Successfully connected to COM3


- After connecting to the device, there will be a request on initialisation and if data acquisition hast started:

.. code-block:: bash

    wait for sync | cycle # of 10
    with maximum of 10 tries ; each second

- After sync is achieved, data acquisition can be performed with get_data()
    No data in the acquisition queue is deprecated by calling state of data_available()

.. code-block:: bash

   -----------------------------
   Time: 1.296625852584839
   data: [ 000, 1355, 2365, 3219]
   -----------------------------

- Finally it will disconnect from CAN device.

