import sys
import re
import os

def process_line(line):
    # Match [timestamp] at the start of the line
    match = re.match(r'\[(.*?)\]\s*(.*)', line)
    if match:
        timestamp = match.group(1)  # Remove brackets
        rest = match.group(2)
        return f"{timestamp}, {rest}"
    else:
        return line.strip()  # No match, return as-is

def generate_output_filename(input_file):
    base, ext = os.path.splitext(input_file)
    return f"{base}_parsed{ext}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_csv_timestamp.py input_file.csv")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' does not exist.")
        sys.exit(1)

    output_file = generate_output_filename(input_file)

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            cleaned_line = process_line(line)
            outfile.write(cleaned_line + "\n")

    print(f"Processed file saved as '{output_file}'.")

if __name__ == "__main__":
    main()
