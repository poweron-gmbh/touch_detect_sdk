# This Python program creates a GUI which interfaces with PowerON BLE device.
# It is recommended to run this program with Python version 3.8.
# There seem to be a bug with the BLE library "bleak" when it is run with Python version 3.9.
import tkinter as tk
import numpy as np
from PIL import ImageTk, Image
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from bleak import BleakClient, BleakScanner
import asyncio
import threading
import csv
import time

# import BLE_connection1
matplotlib.use("TkAgg")

# BLE Addresses
# MAC_ADDRESS = "00:80:E1:26:F6:97"
# MAC_ADDRESS = 0
# MAC_OS_ADDRESS = "83010004-0000-0080-E126-F697"
GAP_PROFILE_UUID = "00001800-0000-1000-8000-00805f9b34fb"
GATT_PROFILE_UUID = "00001801-0000-1000-8000-00805f9b34fb"
SERVICE_UUID = "0000fe40-cc7a-482a-984a-7f2ed5b3e58f"
WRITE_UUID = "0000fe41-8e22-4541-9d4c-21edae82ed19"
NOTIFY_UUID = "0000fe42-8e22-4541-9d4c-21edae82ed19"

CHARACTERISTIC_UUID = NOTIFY_UUID  # <--- Change to the characteristic you want to enable notifications from.

# Declare global variables
global loop_dataBLE
global timestamp_start
global data_logger_file
global data_writer
global client
BLE_address = "00:00:00:00:00:00"
BLE_device_name = "PWRON1"
BLE_device_found = False
sensor_array_size = 36
data2 = np.zeros([6, 6])
data_ready = np.zeros([6, 6])
ble_device_connected = 0
exiting = False
log_data_file_opened = False

# system state:
# 0 = start up / standby
# 1 = connected
# 2 = receiving data
system_state = 0

# log data state:
# 0 = not logging
# 1 = logging
log_data_state = 0

# graph state:
# 0 = ADC voltage reading
# 1 = Resistance value in kOhm
# 2 = Force reading in N
graph_state = 0

# debug state:
# 0 = no debug, no print statements in console
# 1 = debug on, print statements in console
debug_state = 0

# Plot figure
fig = Figure(figsize=(5.1, 5.1), dpi=100)
ax = fig.add_subplot()
fig.patch.set_facecolor('#F0F0F0')  # This is to match the grey background to windows grey

def animate(i):
    try:
        global data_ready
        plot_graph(data_ready)

    except:
        if debug_state == 1:
            print("error animating")
    finally:
        pass


def plot_graph(data_plot):
    sensor_row = ["Row1", "Row2", "Row3", "Row4", "Row5", "Row6"]
    sensor_col = ["Col1", "Col2", "Col3", "Col4", "Col5", "Col6"]

    data_plot2 = data_plot

    # ax.clear()
    # ax.imshow(data_plot, cmap='Purples', vmin=0, vmax=4095)

    voltage = np.zeros([6, 6])
    resistance = np.zeros([6, 6])

    for i in range(len(sensor_row)):
        for j in range(len(sensor_col)):
            voltage[i, j] = data_plot[i, j] / 4095 * 3.3
            # Resistance measurement => R1 = R2 * (Vi-Vo)/Vo
            if data_plot[i, j] == 0:
                data_plot[i, j] = 1     # This is for ensuring that it does not divide by 0

            resistance[i, j] = round(511 * ((4095 - data_plot[i, j]) / data_plot[i, j]), 1)
            voltage[i, j] = round(voltage[i, j], 2)
            # if resistance[i, j] > 1000:
            #     voltage[i, j] = 1
            # else:
            #     voltage[i, j] = 0

    ax.clear()  # clear the plot first
    if graph_state == 0:
        # ax.imshow(voltage, cmap='Purples', vmin=0, vmax=255)
        ax.imshow(voltage, cmap='Purples_r', vmin=2.5, vmax=3.3)

    elif graph_state == 1:
        ax.imshow(resistance, cmap='Purples_r', vmin=0, vmax=7000)

    elif graph_state == 2:
        data_plot = data_plot
        ax.imshow(data_plot, cmap='Purples_r', vmin=0, vmax=2000)

    # We want to show all ticks...
    ax.set_xticks(np.arange(len(sensor_col)))
    ax.set_yticks(np.arange(len(sensor_row)))
    # ... and label them with the respective list entries
    ax.set_xticklabels(sensor_col)
    ax.set_yticklabels(sensor_row)

    # Loop over data dimensions and create text annotations.
    for i in range(len(sensor_row)):
        for j in range(len(sensor_col)):
            # ax.text(j, i, data_plot[i, j], ha="center", va="center", color="black")
            if graph_state == 0:
                if voltage[i, j] < 2.8:
                    ax.text(j, i, voltage[i, j], ha="center", va="center", color="w")
                else:
                    ax.text(j, i, voltage[i, j], ha="center", va="center", color="black")
            elif graph_state == 1:
                if resistance[i, j] < 2000:
                    ax.text(j, i, "{:.0f}".format(resistance[i, j]), ha="center", va="center", color="w")
                else:
                    ax.text(j, i, "{:.0f}".format(resistance[i, j]), ha="center", va="center", color="black")
            elif graph_state == 2:
                if data_plot[i, j] < 220:
                    ax.text(j, i, data_plot[i, j], ha="center", va="center", color="w")
                else:
                    ax.text(j, i, data_plot[i, j], ha="center", va="center", color="black")


root = tk.Tk()
root.title("PowerON BLE Sensor GUI")
root.iconphoto(False, tk.PhotoImage(file='Element 6@4x.png'))
root.geometry("800x600")
# The total grid size is 10 rows and 4 columns for GUI

canvas = tk.Canvas(root, width=800, height=80)
canvas.grid(column=0, row=0, columnspan=4)

# logo
logo = Image.open('Logo_PWN_TM3.png')
logo_width, logo_height = logo.size
ratio = 0.7
logo = logo.resize((int(logo_width * ratio), int(logo_height * ratio)))
logo = ImageTk.PhotoImage(logo)
logo_label = tk.Label(image=logo)
logo_label.image = logo
logo_label.grid(column=0, row=0)

# Header - Bluetooth Communication [frame]
# BLE_Header = tk.Label(root, text="Bluetooth Communication")
# BLE_Header.grid(column=0, row=1)

BLE_Header = tk.LabelFrame(root, text="Bluetooth Communication", width=250, height=200, padx=10, pady=10)
BLE_Header.grid(column=0, row=1, padx=10, pady=10)
BLE_Header.grid_propagate(0)  # stop frame from resizing

# BLE connection name text
BLE_Connection_text = tk.Label(BLE_Header, text="Device Name")
BLE_Connection_text.grid(column=0, row=0, padx=5, pady=5, sticky=tk.W)

# BLE entry for name of BLE advertised name
BLE_Connection_entry_var = tk.StringVar()
BLE_Connection_entry = tk.Entry(BLE_Header, textvariable=BLE_Connection_entry_var)
BLE_Connection_entry_var.set(BLE_device_name)
BLE_Connection_entry.grid(column=1, row=0, padx=5, pady=5)

# BLE status - let user know whether connected, can't find etc.
BLE_Status_text = tk.StringVar()
BLE_Status_text.set("Disconnected")
BLE_Status_label = tk.Label(BLE_Header, textvariable=BLE_Status_text)
BLE_Status_label.grid(column=0, row=3, padx=10, pady=10, columnspan=2)


async def async_ble_connect():
    global client

    try:
        status1 = client.is_connected
        if not status1:
            if debug_state == 1:
                print("Trying to reconnect")
            client = BleakClient(BLE_address, timeout=5.0)
            try:
                await client.connect()
                if debug_state == 1:
                    bleIsConnected = client.is_connected
                    print("BLE connected: " + str(bleIsConnected))
            finally:
                pass

    except Exception as e:
        client = BleakClient(BLE_address, timeout=5.0)
        try:
            await client.connect()
            if debug_state == 1:
                bleIsConnected = client.is_connected
                print("BLE connected: " + str(bleIsConnected))
        except Exception as e:
            if debug_state == 1:
                print(e)
        finally:
            pass

    finally:
        global ble_device_connected
        ble_device_connected = client.is_connected


def detection_callback(device, advertisement_data):
    global BLE_address
    global BLE_device_name
    global BLE_device_found
    if device.name == BLE_device_name:
        BLE_address = device.address
        BLE_device_found = True
        if debug_state == 1:
            print("Found device")


async def discover_ble_device():
    scanner = BleakScanner(timeout=2.0)
    scanner.register_detection_callback(detection_callback)
    await scanner.start()
    await asyncio.sleep(2.0)
    await scanner.stop()


def thread_connect():
    global BLE_device_name
    global BLE_device_found
    global system_state
    BLE_device_found = False
    BLE_device_name = BLE_Connection_entry_var.get()
    asyncio.run(discover_ble_device())

    if BLE_device_found:
        asyncio.run(async_ble_connect())
        if debug_state == 1:
            print("Found device, connecting...")

    # in the event that it is not connected, do nothing
    if ble_device_connected and BLE_device_found:
        BLE_Connect_btn['state'] = tk.DISABLED  # disable the connect button first
        BLE_Receive_Data_btn['state'] = tk.NORMAL  # enable the receive data button
        BLE_Disconnect_btn["state"] = tk.NORMAL  # enable disconnect button

        Data_Log_Yes_btn['state'] = tk.NORMAL
        Data_Log_No_btn['state'] = tk.DISABLED
        # Log_data_var.set(0)

        BLE_Status_text.set("Connected")  # Change label to connected

        system_state = 1
        if debug_state == 1:
            print(f'System_state = {system_state}')

    else:
        BLE_Connect_btn['state'] = tk.NORMAL
        BLE_Receive_Data_btn['state'] = tk.DISABLED
        BLE_Disconnect_btn["state"] = tk.DISABLED
        # Log_data_var.set(0)
        Data_Log_Yes_btn['state'] = tk.DISABLED
        Data_Log_No_btn['state'] = tk.DISABLED
        BLE_Status_text.set("BLE device not found")
        system_state = 0
        if debug_state == 1:
            print(f'System_state = {system_state}')


def ble_connect_cmd():
    BLE_Status_text.set("Connecting... Please wait")  # Change label to connected
    # Log_data_var.set(0)
    BLE_Connect_btn['state'] = tk.DISABLED  # disable the connect button first
    BLE_Receive_Data_btn['state'] = tk.DISABLED  # disable the receive data button
    BLE_Disconnect_btn["state"] = tk.DISABLED  # disable disconnect button
    Data_Log_Yes_btn['state'] = tk.DISABLED   # disable data log yes button
    Data_Log_No_btn['state'] = tk.DISABLED  # disable data log yes button

    thread_connecting = threading.Thread(target=thread_connect)
    thread_connecting.start()


# BLE connect to device button
BLE_Connect_text = tk.StringVar()
BLE_Connect_btn = tk.Button(BLE_Header, width=10, textvariable=BLE_Connect_text, command=ble_connect_cmd)
BLE_Connect_text.set("Connect")
BLE_Connect_btn.grid(column=0, row=1, padx=10, pady=10)


def open_csv_file():
    global data_logger_file
    global data_writer
    global log_data_file_opened
    global timestamp_start
    time_string = time.strftime("%Y%m%d_%H%M%S")
    filename = (BLE_device_name + '_' + time_string + '.csv')
    data_logger_file = open(filename, 'w', newline='')
    data_writer = csv.writer(data_logger_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    log_data_file_opened = True
    sensor_array_title = ["Time(s)"]

    # Making title descriptor for .csv file
    for d in range(sensor_array_size):
        sensor_array_title += (f"Sensor {d + 1}",)

    data_writer.writerow(sensor_array_title)
    timestamp_start = time.time()  # make a global timestamp here


def notification_handler(sender, data):
    global data2
    """Simple notification handler which prints the data received."""
    # print("{0}: {1}".format(sender, data))
    # print(data)
    data1_length = len(data)
    data1_length = int(data1_length / 2)
    data2 = [0] * data1_length

    for d in range(data1_length):
        data2[d] = int(data[d * 2] * 256 + data[d * 2 + 1])

    global data_ready
    data_ready = np.array(data2).reshape(-1, 6)
    data_total = data2

    # log data if selection selected
    if log_data_state == 1:
        if log_data_file_opened:
            data_total.insert(0, time.time() - timestamp_start)
            data_writer.writerow(data_total)

    # print(f"data_total = {data_total}")


async def notify_BLE():
    await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
    await asyncio.sleep(0.010)  # sleep for short period of time


def thread_receive_data():
    if debug_state == 1:
        print("Start receive_data_command")

    if log_data_state == 1:
        if not log_data_file_opened:
            open_csv_file()

    ani.event_source.start()

    global loop_dataBLE
    loop_dataBLE = asyncio.new_event_loop()
    loop_dataBLE.create_task(notify_BLE())
    loop_dataBLE.run_forever()

    if debug_state == 1:
        print("run forever stopped")


def ble_receive_data_cmd():
    BLE_Receive_Data_btn['state'] = tk.DISABLED  # disable receive data button
    BLE_Stop_Data_btn['state'] = tk.NORMAL  # enable stop data button
    BLE_Disconnect_btn['state'] = tk.DISABLED  # disable disconnect button
    Data_Log_Yes_btn['state'] = tk.DISABLED
    Data_Log_No_btn['state'] = tk.DISABLED

    BLE_Status_text.set("Receiving data")

    global system_state
    system_state = 2
    if debug_state == 1:
        print(f'System_state = {system_state}')
        print('start threading function')

    global thread1
    thread1 = threading.Thread(target=thread_receive_data)
    thread1.start()


# BLE receive data
BLE_Receive_Data_text = tk.StringVar()
BLE_Receive_Data_btn = tk.Button(BLE_Header, width=10, textvariable=BLE_Receive_Data_text, state=tk.DISABLED,
                                 command=ble_receive_data_cmd)
BLE_Receive_Data_text.set("Receive Data")
BLE_Receive_Data_btn.grid(column=1, row=1, padx=10, pady=10)


async def stop_ble():
    try:
        ani.event_source.stop()
        global client
        await client.stop_notify(CHARACTERISTIC_UUID)
        if debug_state == 1:
            print("sent stop notify char UUID")
    except:
        if debug_state == 1:
            print("failed at stopping BLE")
    finally:
        pass


def stop_ble_cmd():
    # BLE_Status_text.set("Stop receiving data")
    BLE_Stop_Data_btn['state'] = tk.DISABLED  # disable stop data button

    # stop notify BLE loop
    global loop_dataBLE
    loop_dataBLE.stop()
    while loop_dataBLE.is_running():
        # wait for loop to stop running
        pass
    loop_dataBLE.close()
    if debug_state == 1:
        print("send stop notify")

    # send stop BLE notification
    asyncio.run(stop_ble())
    if debug_state == 1:
        print("finished stop command")

    BLE_Status_text.set("Ready")
    BLE_Receive_Data_btn['state'] = tk.NORMAL  # enable receive data button
    BLE_Disconnect_btn['state'] = tk.NORMAL  # enable disconnect button
    
    if log_data_state == 1:
        Data_Log_Yes_btn['state'] = tk.DISABLED
        Data_Log_No_btn['state'] = tk.NORMAL
    else:
        Data_Log_Yes_btn['state'] = tk.NORMAL
        Data_Log_No_btn['state'] = tk.DISABLED

    global system_state
    system_state = 1
    if debug_state == 1:
        print(f'System_state = {system_state}')


# BLE stop data
BLE_Stop_Data_text = tk.StringVar()
BLE_Stop_Data_btn = tk.Button(BLE_Header, width=10, textvariable=BLE_Stop_Data_text, command=stop_ble_cmd, state=tk.DISABLED)
BLE_Stop_Data_text.set("Stop Data")
BLE_Stop_Data_btn.grid(column=1, row=2, padx=10, pady=10, columnspan=2)


async def disconnect_ble_device():
    await client.disconnect()

    if log_data_state == 1:
        # close file
        global data_logger_file
        data_logger_file.close()


def thread_disconnection():
    try:
        asyncio.run(disconnect_ble_device())
    except:
        if debug_state == 1:
            print("known issue disconnecting")
    finally:
        if debug_state == 1:
            print('show disconnection changes')

        if not exiting:
            BLE_Status_text.set("Disconnected")
            BLE_Receive_Data_btn['state'] = tk.DISABLED  # disable receive data button
            BLE_Stop_Data_btn['state'] = tk.DISABLED  # disable stop data button
            BLE_Connect_btn['state'] = tk.NORMAL  # enable ble connect button
            BLE_Disconnect_btn['state'] = tk.DISABLED  # disable ble disconnect button
            Data_Log_Yes_btn['state'] = tk.DISABLED
            Data_Log_No_btn['state'] = tk.DISABLED

        global system_state
        system_state = 0
        if debug_state == 1:
            print(f'System_state = {system_state}')


def ble_disconnect_cmd():
    global log_data_state
    BLE_Status_text.set("Disconnecting... Please wait")

    # Log_data_var.set(0)
    # log_data_state = Log_data_var.get()
    if log_data_file_opened:
        data_logger_file.close()

    th_disconnect = threading.Thread(target=thread_disconnection)
    th_disconnect.start()

    if not exiting:
        BLE_Receive_Data_btn['state'] = tk.DISABLED  # disable receive data button
        BLE_Stop_Data_btn['state'] = tk.DISABLED  # disable stop data button
        BLE_Connect_btn['state'] = tk.DISABLED  # enable ble connect button
        BLE_Disconnect_btn['state'] = tk.DISABLED  # disable ble disconnect button
        Data_Log_Yes_btn['state'] = tk.DISABLED
        Data_Log_No_btn['state'] = tk.DISABLED


# BLE disconnect data
BLE_Disconnect_text = tk.StringVar()
BLE_Disconnect_btn = tk.Button(BLE_Header, width=10, textvariable=BLE_Disconnect_text, command=ble_disconnect_cmd,
                               state=tk.DISABLED)
BLE_Disconnect_text.set("Disconnect")
BLE_Disconnect_btn.grid(column=0, row=2, padx=10, pady=10)

# Header - Data logging [frame]
Data_Log_Header = tk.LabelFrame(root, text="Data Logging", width=250, height=150, padx=10, pady=10)
Data_Log_Header.grid(column=0, row=5, padx=10, pady=10)
Data_Log_Header.grid_propagate(0)  # stop frame from resizing

# Setting some rows and columns structure so that the buttons and text are centered in frame
Data_Log_Header.rowconfigure(0, weight=1)
Data_Log_Header.columnconfigure(0, weight=1)
Data_Log_Header.rowconfigure(3, weight=1)
Data_Log_Header.columnconfigure(3, weight=1)

# Data logger file name
Data_Log_filename = tk.Label(Data_Log_Header, text="Data logging:")
Data_Log_filename.grid(column=1, row=1)


# def data_logger_cmd():
#     global log_data_state
#     log_data_state = Log_data_var.get()
#     if debug_state == 1:
#         print(f'Radio button value is {Log_data_var.get()}')
#
#     if Log_data_var.get() == 0:
#         # close file
#         global log_data_file_opened
#         global data_logger_file
#
#         if log_data_file_opened:
#             data_logger_file.close()
#             log_data_file_opened = False


def data_logger_yes_cmd():
    global log_data_state

    log_data_state = 1
    Data_Log_Yes_btn['state'] = tk.DISABLED
    Data_Log_No_btn['state'] = tk.NORMAL


def data_logger_no_cmd():
    global log_data_state
    global log_data_file_opened
    global data_logger_file

    log_data_state = 0

    Data_Log_Yes_btn['state'] = tk.NORMAL
    Data_Log_No_btn['state'] = tk.DISABLED

    if log_data_file_opened:
        data_logger_file.close()
        log_data_file_opened = False


# Data logger start
# Log_data_var = tk.IntVar()

Data_Log_Yes_text = tk.StringVar()
Data_Log_Yes_btn = tk.Button(Data_Log_Header, width=10, textvariable=Data_Log_Yes_text, state=tk.DISABLED,
                             command=data_logger_yes_cmd)
Data_Log_Yes_text.set("Yes")
Data_Log_Yes_btn.grid(column=1, row=2, padx=10, pady=10)

Data_Log_No_text = tk.StringVar()
Data_Log_No_btn = tk.Button(Data_Log_Header, width=10, textvariable=Data_Log_No_text, state=tk.DISABLED,
                            command=data_logger_no_cmd)
Data_Log_No_text.set("No")
Data_Log_No_btn.grid(column=1, row=3, padx=10, pady=10)


# Data_Log_Receive_Data_text = tk.StringVar()
# Data_Log_Receive_Data_btn = tk.Radiobutton(root, textvariable=Data_Log_Receive_Data_text,
#                                            value=radio_value, indicator=0)
# Data_Log_Receive_Data_text.set("Data logging")
# Data_Log_Receive_Data_btn.grid(column=0, row=7)

# # Data logger stop
# Data_Log_Stop_Data_text = tk.StringVar()
# Data_Log_Stop_Data_btn = tk.Button(root, textvariable=Data_Log_Stop_Data_text)
# Data_Log_Stop_Data_text.set("Stop data logging")
# Data_Log_Stop_Data_btn.grid(column=0, row=8)


def exit_btn_command():
    global exiting
    exiting = True
    global system_state
    global log_data_file_opened
    if debug_state == 1:
        print(f'Exiting... System_state = {system_state}')

    if log_data_file_opened:    # if file is opened
        global data_logger_file
        data_logger_file.close()
        log_data_file_opened = False

    if system_state == 0:
        pass
    elif system_state == 1:
        ble_disconnect_cmd()
        while not system_state == 0:
            pass
    elif system_state == 2:
        stop_ble_cmd()
        ble_disconnect_cmd()
        while not system_state == 0:
            pass
    else:
        pass

    root.destroy()
    exit()


# Exit
Exit_text = tk.StringVar()
Exit_btn = tk.Button(root, width=10, textvariable=Exit_text, command=exit_btn_command)
Exit_text.set("Exit")
Exit_btn.grid(column=0, row=9)

# Data display
Data_Display_Header = tk.LabelFrame(root, text="Data Display", padx=10, pady=10)
Data_Display_Header.grid(column=1, row=9, padx=15, pady=0)


def graph_v_cmd():
    Graph_Voltage_btn['state'] = tk.DISABLED
    Graph_Res_btn['state'] = tk.NORMAL
    Graph_Raw_btn['state'] = tk.NORMAL

    global graph_state
    graph_state = 0


# Graph voltage measurement display
Graph_Voltage_text = tk.StringVar()
Graph_Voltage_btn = tk.Button(Data_Display_Header, width=10, textvariable=Graph_Voltage_text,
                              command=graph_v_cmd, state=tk.DISABLED)
Graph_Voltage_text.set("Voltage")
Graph_Voltage_btn.grid(column=0, row=0, padx=40)


def graph_r_cmd():
    Graph_Voltage_btn['state'] = tk.NORMAL
    Graph_Res_btn['state'] = tk.DISABLED
    Graph_Raw_btn['state'] = tk.NORMAL

    global graph_state
    graph_state = 1


# Graph resistance measurement display
Graph_Res_text = tk.StringVar()
Graph_Res_btn = tk.Button(Data_Display_Header, width=10, textvariable=Graph_Res_text, command=graph_r_cmd)
Graph_Res_text.set("Resistance")
Graph_Res_btn.grid(column=1, row=0, padx=40)


def graph_f_cmd():
    Graph_Voltage_btn['state'] = tk.NORMAL
    Graph_Res_btn['state'] = tk.NORMAL
    Graph_Raw_btn['state'] = tk.DISABLED

    global graph_state
    graph_state = 2


# Graph resistance measurement display
Graph_Raw_text = tk.StringVar()
Graph_Raw_btn = tk.Button(Data_Display_Header, width=10, textvariable=Graph_Raw_text, command=graph_f_cmd)
Graph_Raw_text.set("Raw Data")
Graph_Raw_btn.grid(column=2, row=0, padx=40)

# canvas = tk.Canvas(root, width=800, height=10)
# canvas.grid(columnspan=4, column=0, row=10)


def plot_initial_graph():
    plot_graph(np.array(data2).reshape(-1, 6))
    fig.tight_layout()

    # Integrate matplotlib figure into tkinter
    # Move the figure to the front
    canvas_fig = FigureCanvasTkAgg(fig, master=root)
    canvas_fig.draw()
    canvas_fig.get_tk_widget().grid(columnspan=3, rowspan=8, column=1, row=0)


plot_initial_graph()

root.protocol("WM_DELETE_WINDOW", exit_btn_command)  # handle event when window is closed by user

# ani = animation.FuncAnimation(fig, plot_graph, interval=500)
ani = animation.FuncAnimation(fig, animate, interval=200)
# pause animation
ani.event_source.stop()

root.mainloop()
