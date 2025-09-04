import sys
import csv
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox

Y1_MIN = 18 # Degrees C
Y1_MAX = 40.5 # Degrees C
Y2_MIN = -0.5 # Degrees C
Y2_MAX = 8 # Degrees C

# --- Handle command-line argument ---
if len(sys.argv) < 2:
    print("Error: No CSV file provided.\nUsage: python plot_data.py <file.csv>")
    sys.exit(1)

csv_file = sys.argv[1]

# --- Keys to extract ---
keys_of_interest = ['T', 'T1R', 'T2R', 'P1', 'P2']

# --- Parse the CSV file ---
def parse_csv(filename):
    data = {key: [] for key in keys_of_interest}
    try:
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                row = row[1:]  # Skip the first item
                row_dict = dict(zip(row[::2], row[1::2]))
                for key in keys_of_interest:
                    value = row_dict.get(key)
                    if value is not None:
                        try:
                            data[key].append(float(value))
                        except ValueError:
                            data[key].append(None)
        return data
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

data = parse_csv(csv_file)

# --- Check data validity ---
if not data['T']:
    print("Error: No 'T' (time) data found in the CSV. Check the CSV format.")
    sys.exit(1)

# --- Convert T from ms to seconds ---
data['T'] = [t / 1000.0 for t in data['T']]

# --- Plotting ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
fig.subplots_adjust(
    top=0.92,
    bottom=0.42,  # enough space for text boxes
    hspace=0.4    # spacing between subplot rows
)


# Plot T1R and T2R
line1, = ax1.plot(data['T'], data['T1R'], label='T1R', color='red')
line2, = ax1.plot(data['T'], data['T2R'], label='T2R', color='orange')
ax1.set_title('T1R & T2R')
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Degrees C')
ax1.legend()
ax1.grid(True)

# Plot P1 and P2
line3, = ax2.plot(data['T'], data['P1'], label='Tank P1', color='blue')
line4, = ax2.plot(data['T'], data['P2'], label='Nozzle P2', color='green')
ax2.set_title('Tank and Nozzle Pressure')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Pressure MPa')
ax2.legend()
ax2.grid(True)

# --- TextBox Widgets for Axis Limits ---

# Axes for TextBoxes
ax_text_xmin = plt.axes([0.15, 0.26, 0.15, 0.04])
ax_text_xmax = plt.axes([0.42, 0.26, 0.15, 0.04])
ax_text_y1min = plt.axes([0.15, 0.18, 0.15, 0.04])
ax_text_y1max = plt.axes([0.42, 0.18, 0.15, 0.04])
ax_text_y2min = plt.axes([0.15, 0.10, 0.15, 0.04])
ax_text_y2max = plt.axes([0.42, 0.10, 0.15, 0.04])

# Create TextBoxes
text_xmin = TextBox(ax_text_xmin, 'X Min (s)', initial=str(min(data['T'])))
text_xmax = TextBox(ax_text_xmax, 'X Max (s)', initial=str(max(data['T'])))
text_y1min = TextBox(ax_text_y1min, 'Tmp Y Min', initial=str(Y1_MIN))
text_y1max = TextBox(ax_text_y1max, 'Tmp Y Max', initial=str(Y1_MAX))
text_y2min = TextBox(ax_text_y2min, 'Prs Y Min', initial=str(Y2_MIN))
text_y2max = TextBox(ax_text_y2max, 'Prs Y Max', initial=str(Y2_MAX))

# --- Update function for text input ---
def update_axes(_):
    try:
        # Read and convert input values
        xmin = float(text_xmin.text)
        xmax = float(text_xmax.text)
        y1min= float(text_y1min.text)
        y1max = float(text_y1max.text)
        y2min= float(text_y2min.text)
        y2max = float(text_y2max.text)

        # Set x-axis limits for both plots
        ax1.set_xlim(xmin, xmax)
        ax2.set_xlim(xmin, xmax)

        # Set y-axis limits (min remains fixed to data min)
        ax1.set_ylim(y1min, y1max)
        ax2.set_ylim(y2min, y2max)

        fig.canvas.draw_idle()

    except ValueError:
        print("Invalid input. Please enter valid numeric values.")

xmin = float(text_xmin.text)
xmax = float(text_xmax.text)
y1min= float(text_y1min.text)
y1max = float(text_y1max.text)
y2min= float(text_y2min.text)
y2max = float(text_y2max.text)

# Set x-axis limits for both plots
ax1.set_xlim(xmin, xmax)
ax2.set_xlim(xmin, xmax)

# Set y-axis limits (min remains fixed to data min)
ax1.set_ylim(y1min, y1max)
ax2.set_ylim(y2min, y2max)

# --- Connect TextBoxes to update function ---
text_xmin.on_submit(update_axes)
text_xmax.on_submit(update_axes)
text_y1max.on_submit(update_axes)
text_y2max.on_submit(update_axes)

# --- Show the plot ---
plt.show()
