import time
import signal
import serial
import serial.tools.list_ports
import csv
import os
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import queue

# Globals
serial_lock = threading.Lock()
ser = None
serial_queue = queue.Queue()
gui_root = None
text_widget = None
exit_event = threading.Event()

# Plotting data
time_index = []
t1r_list = []
t2r_list = []
p1_list = []
p2_list = []
IgR_list = []
SR_list = []
MAX_POINTS = 500

def get_filename():
    filename = input("Enter filename to save data (without extension): ").strip()
    if not filename:
        print("Invalid filename. Using default: data_log.csv")
        return "data_log.csv"
    if not filename.endswith(".csv"):
        filename += ".csv"
    return filename

def select_serial_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found.")
        exit(1)

    print("\nAvailable serial ports:")
    for i, port in enumerate(ports):
        print(f"{i+1}: {port.device} ({port.description})")

    while True:
        try:
            choice = int(input("Select a port by number: ")) - 1
            if 0 <= choice < len(ports):
                return ports[choice].device
            else:
                print("Invalid choice. Try again.")
        except ValueError:
            print("Enter a valid number.")

def setup_gui():
    global gui_root, text_widget

    gui_root = tk.Tk()
    gui_root.title("Serial Monitor Output")

    text_widget = ScrolledText(gui_root, wrap=tk.WORD, height=20, width=180)
    text_widget.pack(padx=10, pady=10)

    command_frame = tk.Frame(gui_root)
    command_frame.pack(padx=10, pady=(0, 10))

    command_label = tk.Label(command_frame, text="Send Command:")
    command_label.pack(side=tk.LEFT)

    command_entry = tk.Entry(command_frame, width=60)
    command_entry.pack(side=tk.LEFT, padx=(5, 5))

    def send_command():
        command = command_entry.get().strip()
        if command:
            if ser is None:
                append_to_gui("Error: Serial port has not been initialized yet.")
            elif not ser.is_open:
                append_to_gui("Error: Serial port is closed.")
            else:
                with serial_lock:
                    try:
                        ser.write((command + '\n').encode('utf-8')) #TODO instead of writing immediately, add to a queue
                        append_to_gui(f">>> {command}")
                    except Exception as e:
                        append_to_gui(f"Error sending command: {e}")
            command_entry.delete(0, tk.END)

    send_button = tk.Button(command_frame, text="Send", command=send_command)
    send_button.pack(side=tk.LEFT)
    command_entry.bind("<Return>", lambda event: send_command())

def append_to_gui(line):
    if text_widget:
        text_widget.insert(tk.END, line + '\n')
        text_widget.see(tk.END)

def exit_cleanly():
    try:
        if ser and ser.is_open:
            ser.close()
            print("Serial port closed.")
    except Exception as e:
        print(f"Error closing serial port: {e}")
    try:
        if gui_root:
            gui_root.quit()
            gui_root.destroy()
            print("GUI closed.")
    except:
        pass
    os._exit(0)

def serial_reader_thread():
    global ser
    while not exit_event.is_set():
        try:
            if ser and ser.in_waiting: # instead of checking for serial input, check to serial commands in the queue
                line = ser.readline().decode('utf-8').strip()
                if line:
                    serial_queue.put(line)
            else: # TODO instead of sleeping, check the queue for serial commands
                time.sleep(0.05)
        except Exception as e:
            append_to_gui(f"Serial read error: {e}")
            time.sleep(0.1)

def save_raw_line_to_csv(line, filename):
    parts = [p.strip() for p in line.split(',')]
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp] + parts)

def parse_line(line):
    try:
        parts = [p.strip() for p in line.split(',')]
        data = {}
        i = 0
        while i < len(parts) - 1:
            key = parts[i]
            try:
                value = float(parts[i+1])
                data[key] = value
                i += 2
            except ValueError:
                i += 1
        return {
            # TODO delete lines and add 1 lines for temperature
            "T": data.get("T"),
        }
    except Exception as e:
        print(f"Parse error: {e}")
        return None

def update_plot(frame):
    if exit_event.is_set():
        plt.close(fig)
        exit_cleanly()
        return

    now = datetime.now()
    time_index.append(now)
    time_index[:] = time_index[-MAX_POINTS:]

    try:
        while True:
            line = serial_queue.get_nowait()
            append_to_gui(line)
            save_raw_line_to_csv(line, update_plot.filename)
            parsed = parse_line(line)

            if parsed:
                update_plot.last_data = {
                    "T": parsed["T"],
                }

    except queue.Empty:
        pass

    data = getattr(update_plot, "last_data", None)
    if data:
        t1r_list.append(data["T"])
    else:
        t1r_list.append(None)

    t1r_list[:] = t1r_list[-MAX_POINTS:]

    ax1.clear()

    # TODO update t1r_list to the correct list
    ax1.plot(time_index, t1r_list, label="T1R", color='red')
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Temperature °C")
    ax1.legend()
    ax1.grid(True)
    ax1.tick_params(axis='x', rotation=45)

def signal_handler(sig, frame):
    print("Keyboard interrupt received. Exiting...")
    exit_event.set()
    exit_cleanly()

# Set up plot
fig, ax1 = plt.subplots(1, 1, figsize=(10, 6))
ani = animation.FuncAnimation(fig, update_plot, interval=200, cache_frame_data=False)
plt.tight_layout()

# Setup
port = select_serial_port()
filename = get_filename()
ser = serial.Serial(port, 115200, timeout=1)
update_plot.filename = filename
threading.Thread(target=serial_reader_thread, daemon=True).start()

setup_gui()
signal.signal(signal.SIGINT, signal_handler)
plt.show()
