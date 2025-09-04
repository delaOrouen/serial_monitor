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

def serial_writer():
    global ser
    print("You can now type commands to send over serial. Type 'exit' to stop sending.")
    while not exit_event.is_set():
        try:
            user_input = input()
            if user_input.strip().lower() == 'exit':
                print("Exit command received. Stopping program...")
                exit_event.set()
                break
            if ser and ser.is_open:
                ser.write((user_input + '\n').encode('utf-8'))
        except Exception as e:
            print(f"Error writing to serial: {e}")
            break


def setup_gui():
    global gui_root, text_widget

    gui_root = tk.Tk()
    gui_root.title("Serial Monitor Output")

    text_widget = ScrolledText(gui_root, wrap=tk.WORD, height=20, width=180)
    text_widget.pack(padx=10, pady=10)

    # Run the GUI in a separate thread so it doesn't block matplotlib
    threading.Thread(target=gui_root.mainloop, daemon=True).start()

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
    threading.Thread(target=serial_writer, daemon=True).start()

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

            # Trim lists
            time_index[:] = time_index[-MAX_POINTS:]
            t1r_list[:] = t1r_list[-MAX_POINTS:]
            t2r_list[:] = t2r_list[-MAX_POINTS:]
            p1_list[:] = p1_list[-MAX_POINTS:]
            p2_list[:] = p2_list[-MAX_POINTS:]

            # Plotting
            ax1.clear()
            ax2.clear()

            ax1.plot(time_index, t1r_list, label="T1R", color='red')
            ax1.plot(time_index, t2r_list, label="T2R", color='orange')
            ax1.set_ylabel("Temperature (ﾂｰC)")
            ax1.legend()
            ax1.grid(True)

            ax2.plot(time_index, p1_list, label="P1", color='blue')
            ax2.plot(time_index, p2_list, label="P2", color='green')
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
ani = animation.FuncAnimation(fig, update_plot, interval=200)
plt.tight_layout()
setup_gui()
signal.signal(signal.SIGINT, signal_handler)
plt.show()
