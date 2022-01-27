#!/usr/bin/env python3

import asyncio
from bleak import BleakClient, BleakScanner, discover

MAC = 'CC:50:E3:A1:48:EA'
NOTIFY_UUID = "0000fe42-8e22-4541-9d4c-21edae82ed19"

def notification_handler(sender, data):
    global data2
    """Simple notification handler which prints the data received."""
    # print("{0}: {1}".format(sender, data))
    # print(data)
    data1_length = len(data)
    data1_length = int(data1_length / 2)
    data2 = [0] * data1_length

    print(data)

async def main():
    devices = await discover()
    for d in devices:
        print(d)

    client = BleakClient(MAC)
    await client.connect()
    await client.start_notify(NOTIFY_UUID, notification_handler)
    await asyncio.sleep(2.0)
    await client.stop_notify(NOTIFY_UUID)
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())