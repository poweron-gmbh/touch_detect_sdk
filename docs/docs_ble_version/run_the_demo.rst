Run the demo
============

There is simple demo inside the **sample** folder. This helps you to understand how this library works. To run it:

-  Open test_ble_touch_sdk.py. Rename :file:`BLE_DEVICE_NAME` to the device you want to connect.

-  Run the demo:

.. code-block:: bash

   # Place inside ble_touchdetect_sdk
   cd ble_touch_detect_sdk

   # Run the demo
   python .\sample\demo.py 

- You will see that the demo will search for BLE devices and list them like this:

.. code-block:: bash

   Searching BLE devices ...
   Found device: 
   with MAC: 4F:22:82:3B:86:8A
   Found device: Galaxy Watch4 (0DEL)
   with MAC: 68:63:FD:29:3B:E5
   Found device: PWRON1
   with MAC: CC:50:E3:A1:48:EA
   Search finished. 3 device[s] found


- The demo will then try to connect to :file:`BLE_DEVICE_NAME`. You will see a message like this:

.. code-block:: bash

   INFO:root:Connected to BLE device
   Successfully connnected to PWRON1


- After connecting to the device, it will retrieve data from TouchDetect:

.. code-block:: bash

   -----------------------------
   Time: 6.296625852584839
   data: [850, 872, 874, 846, 614, 131, 307, 527, 353, 439, 620, 621, 566, 792, 994, 584, 71, 572, 396, 809, 224, 699, 153, 646, 316, 157, 721, 937, 34, 914, 914, 954, 665, 349, 552, 349]
   -----------------------------

- Finally it will disconnect from BLE device.

