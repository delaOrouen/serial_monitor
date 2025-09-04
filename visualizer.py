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

# Global serial object
ser = None
gui_root = None
text_widget = None
exit_event = threading.Event()

# Plotting config
time_index = []
t1r_list = []
t2r_list = []
p1_list = []
p2_list = []
IgR_list = []
SR_list = []
MAX_POINTS = 500  # Number of points to show on graph

# Get filename from user
def get_filename():
    filename = input("Enter filename to save data (without extension): ").strip()
    if not filename:
        print("Invalid filename. Using default: data_log.csv")
        return "data_log.csv"
    if not filename.endswith(".csv"):
        filename += ".csv"
    return filename

# List and choose serial port
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

    # Text area to show serial output
    text_widget = ScrolledText(gui_root, wrap=tk.WORD, height=20, width=180)
    text_widget.pack(padx=10, pady=10)

    # --- New: Command entry and send button ---
    command_frame = tk.Frame(gui_root)
    command_frame.pack(padx=10, pady=(0, 10))

    command_label = tk.Label(command_frame, text="Send Command:")
    command_label.pack(side=tk.LEFT)

    command_entry = tk.Entry(command_frame, width=60)
    command_entry.pack(side=tk.LEFT, padx=(5, 5))

    def send_command():
        command = command_entry.get().strip()
        if command:
            if ser and ser.is_open:
                try:
                    ser.write((command + '\n').encode('utf-8'))
                    append_to_gui(f">>> {command}")  # Show command in output area
                except Exception as e:
                    append_to_gui(f"Error sending command: {e}")
            else:
                append_to_gui("Serial port not open.")
            command_entry.delete(0, tk.END)  # Clear entry after sending

    send_button = tk.Button(command_frame, text="Send", command=send_command)
    send_button.pack(side=tk.LEFT)
    command_entry.bind("<Return>", lambda event: send_command())


def append_to_gui(line):
    if text_widget:
        text_widget.insert(tk.END, line + '\n')
        text_widget.see(tk.END)

def exit_cleanly():
    global exit_program
    exit_program = True
    try:
        if ser and ser.is_open:
            ser.close()
            print("Serial port closed.")
    except Exception as e:
        print(f"Error closing serial port: {e}")
    
    # Close the tkinter GUI if it's open
    try:
        if gui_root:
            gui_root.quit()
            gui_root.destroy()
            print("GUI closed.")
    except:
        pass

    # Exit the entire program forcefully
    os._exit(0)

def get_serial_lines(port, baudrate=115200):
    global ser
    ser = serial.Serial(port, baudrate, timeout=1)
    print(f"Connected to {port} at {baudrate} baud.")

    # Start writer thread

    while not exit_event.is_set():
        try:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    yield line
        except Exception as e:
            print(f"Serial error: {e}")
            break


def save_raw_line_to_csv(line, filename):
    parts = [p.strip() for p in line.split(',')]
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # millisecond precision
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp] + parts)


# Extract specific fields to plot
def parse_line(line):
    try:
        parts = [p.strip() for p in line.split(',')]
        data = {}
        i = 0
        while i < len(parts) - 1:
            key = parts[i]
            try:
                value = float(parts[i + 1])
                data[key] = value
                i += 2
            except ValueError:
                i += 1  # skip malformed
        return {
            "T1R": data.get("T1R"),
            "T2R": data.get("T2R"),
            "P1": data.get("P1"),
            "P2": data.get("P2"),
            "IgR": data.get("IgR"),
            "SR": data.get("SR"),
        }
    except Exception as e:
        print(f"Parse error: {e}")
        return None

def update_plot(frame):
    if exit_event.is_set():
        plt.close(fig)
        exit_cleanly()
        return

    if not hasattr(update_plot, "data_gen"):
        port = select_serial_port()
        filename = get_filename()
        update_plot.filename = filename
        update_plot.data_gen = get_serial_lines(port)

        # Create file if it doesn't exist, and write header
        if not os.path.exists(filename):
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Raw Data..."])  # Optional header

    try:
        line = next(update_plot.data_gen)
        append_to_gui(line)

        save_raw_line_to_csv(line, update_plot.filename)

        # Parse values to plot
        parsed = parse_line(line)
        if parsed:
            now = datetime.now()
            time_index.append(now)
            t1r_list.append(parsed["T1R"])
            t2r_list.append(parsed["T2R"])
            p1_list.append(parsed["P1"])
            p2_list.append(parsed["P2"])
            IgR_list.append(parsed["IgR"])
            SR_list.append((-144+parsed["SR"])/6)

            # Trim lists
            time_index[:] = time_index[-MAX_POINTS:]
            t1r_list[:] = t1r_list[-MAX_POINTS:]
            t2r_list[:] = t2r_list[-MAX_POINTS:]
            p1_list[:] = p1_list[-MAX_POINTS:]
            p2_list[:] = p2_list[-MAX_POINTS:]
            IgR_list[:] = IgR_list[-MAX_POINTS:]
            SR_list[:] = SR_list[-MAX_POINTS:]

            # Plotting
            ax1.clear()
            ax2.clear()

            ax1.plot(time_index, t1r_list, label="T1R", color='red')
            ax1.plot(time_index, t2r_list, label="T2R", color='orange')
            ax1.set_ylabel("Temperature (C)")
            ax1.legend()
            ax1.grid(True)

            ax2.plot(time_index, p1_list, label="Tank Pressure P1", color='blue')
            ax2.plot(time_index, p2_list, label="Nozzle Pressure P2", color='green')
            ax2.plot(time_index, IgR_list, label="Ignitor 1=ON/0=OFF", color='brown')
            ax2.plot(time_index, SR_list, label="Valves 1=OPEN/0=CLOSED", color='grey')
            ax2.set_ylabel("Pressure")
            ax2.set_xlabel("Time")
            ax2.legend()
            ax2.grid(True)

            for ax in (ax1, ax2):
                ax.tick_params(axis='x', rotation=45)

    except StopIteration:
        print("No more data.")
    except Exception as e:
        print(f"Update error: {e}")
        if ser and ser.is_open:
            ser.close()

def signal_handler(sig, frame):
    print("Keyboard interrupt received. Exiting...")
    exit_event.set()
    exit_cleanly()

# Set up the figure
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
ani = animation.FuncAnimation(fig, update_plot, interval=200, cache_frame_data=False)
plt.tight_layout()
setup_gui()
signal.signal(signal.SIGINT, signal_handler)
plt.show()
