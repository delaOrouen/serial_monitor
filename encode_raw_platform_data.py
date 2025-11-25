"""
File: encode_raw_platform_data.py
Author: Rouen de la O 
Created: 2025-11-25
Description:
    This file reads the last line from the raw_platform_telemetry.csv file created by Orb Astro's FlatSatGUI, decodes the data in the
    designated data bank and prints it to the terminal. If the Option for printing a one-time output is selected, this script will 
    decode and print the latest line to the serial monitor at a rate of 1 Hz indefinitely.
"""
import base64
import time
from collections import deque

YEAR = 25
MONTH = 11
PATCH = 0
LTR_KM_YEAR = 25
LTR_KM_MONTH = 11
LTR_KM_DAY = 07
def print_version():
    print()
    print("********************************************************")
    print("Starting up The Encode Raw Platform Data Script")
    print("version " + YEAR + "." + MONTH + "." + PATCH +"")
    print("Compatible with the ltr-km release " + LTR_KM_YEAR + "/" + LTR_KM_MONTH + "/" + LTR_KM_DAY + "")
    print("********************************************************")
    print()

def tail_base64(filepath, n=1):
    """Return the last n lines of a file as a list of base64-encoded strings."""
    decoded_lines = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in deque(f, maxlen=n):
            # Encode each line to bytes, then to base64, then back to a string
            line = line[24:]
            b64_line = base64.b64decode(line)
            decoded_lines.append(b64_line)
    return decoded_lines

def hex_to_binary(hex_string):
    """
    Converts a hexadecimal string to a binary string, maintaining correct length.
    """
    # Convert the hex string to an integer (base 16)
    decimal_value = int(hex_string, 16)

    # Calculate the desired length of the binary string (4 bits per hex digit)
    binary_length = len(hex_string) * 4
    
    # Use format() to convert the integer to binary and pad with leading zeros
    # '0' is the fill character, '>' aligns right, 'b' is the type (binary)
    binary_string = format(decimal_value, f'0>{binary_length}b')
    
    return binary_string

def get_telemetry_line_printing(line):
    print(line[0:2*1] + " response ID")
    print(line[2*1:2*9] + " time")
    print(line[2*9:2*10] + " mode")
    print("")

    print(line[2*10:2*11] + " thermocouple status")
    print(line[2*11:2*15] + " thermocouple temperature")
    print(line[2*15:2*19] + " pressure sensor value")
    print(line[2*19:2*21] + " solenoid fault 0")
    print(line[2*21:2*23] + " solenoid fault 1")
    print(line[2*23:2*25] + " power supply")
    print("")

    tmp_binary_str = hex_to_binary(line[2*25:2*26])
    print(tmp_binary_str[0:2] + " valve status")
    print(tmp_binary_str[2:3] + " ignitor status")
    print(tmp_binary_str[3:5] + " heater status")
    print(tmp_binary_str[5:8] + " reserved")
    print("")

    tmp_binary_str = hex_to_binary(line[2*26:2*27])
    print(tmp_binary_str[0:1] + " reserved")
    print(tmp_binary_str[2:8] + " IMU reliability")
    print(line[2*27:2*45] + " IMU value")
    print("")

    print(line[2*45:2*46] + " group command processing status")

    tmp_binary_str = hex_to_binary(line[2*46:2*47])
    print(tmp_binary_str[0:5] + " group command ID")
    print(tmp_binary_str[5:8] + " group command execution number")
    print("")
    print("")
    print("")

def oneHz_telemetry_line_printing(line):
    print(line[0:2*8] + " time")
    print(line[2*8:2*9] + " mode")
    print("")

    print(line[2*9:2*10] + " thermocouple status")
    print(line[2*10:2*14] + " thermocouple temperature")
    print(line[2*14:2*18] + " pressure sensor value")
    print(line[2*18:2*20] + " solenoid fault 0")
    print(line[2*20:2*22] + " solenoid fault 1")
    print(line[2*22:2*24] + " power supply")
    print("")

    tmp_binary_str = hex_to_binary(line[2*24:2*25])
    print(tmp_binary_str[0:2] + " valve status")
    print(tmp_binary_str[2:3] + " ignitor status")
    print(tmp_binary_str[3:5] + " heater status")
    print(tmp_binary_str[5:8] + " reserved")
    print("")

    tmp_binary_str = hex_to_binary(line[2*25:2*26])
    print(tmp_binary_str[0:1] + " reserved")
    print(tmp_binary_str[2:8] + " IMU reliability")
    print(line[2*26:2*44] + " IMU value")
    print("")

    # note, the following is not printed during ignition
    print(line[2*44:2*45] + " group command processing status")

    tmp_binary_str = hex_to_binary(line[2*45:2*46])
    print(tmp_binary_str[0:5] + " group command ID")
    print(tmp_binary_str[5:8] + " group command execution number")
    print("")
    print("")
    print("")

FILE_PATH = "C:\\Users\\rouen\\Documents\\OrbAstro\\telemetry\\raw_platform_data.csv" 

print_version()

option = input("one time input run? : ")

if ("yes" == option):
    option = input("enter the number of lines to process : ")
    decoded_lines = tail_base64(FILE_PATH, int(option))
    for line in decoded_lines:
        hex_str = line.hex()
        print(hex_str[1120*2:1183*2])
        get_telemetry_line_printing(hex_str[1120*2:1183*2])
elif ("no" == option):
    try:
        while True:
            try:
                decoded_lines = tail_base64(FILE_PATH2)
                for line in decoded_lines:
                    hex_str = line.hex()
                    print(hex_str[1120*2:1183*2])
                    # oneHz_telemetry_line_printing(hex_str[1120*2:1183*2])
                    get_telemetry_line_printing(hex_str[1120*2:1183*2])
            except:
                print("error reading file: {e}")
            time.sleep(1)
    except Exception as e:
        print("\nstopped by user")
else:
    print("enter \'yes\' or \'no\'")
