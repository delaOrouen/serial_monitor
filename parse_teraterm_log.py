import sys
import re
import os

def process_line(line):
    # Match [timestamp] at the start of the line
    match = re.match(r'\[(.*?)\]\s*(.*)', line)
    if match:
        timestamp = match.group(1)
        rest = match.group(2)

        # TODO here, using keys of interest, remove all white 
        rest = re.sub(r'\s*,\s*', ',', rest)

        return f"{timestamp}, {rest}"
    else:
        return line.strip()

def generate_output_filename(input_file):
    base, ext = os.path.splitext(input_file)
    return f"{base}_parsed.csv"  # Force .csv output regardless of input extension

def process_file(input_file):
    if not os.path.exists(input_file):
        print(f"[!] Skipping '{input_file}' (not found)")
        return

    output_file = generate_output_filename(input_file)

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            cleaned_line = process_line(line)
            outfile.write(cleaned_line + "\n")

    print(f"[隨ｨ霆｢ Processed '{input_file}' 遶翫・'{output_file}'")

def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_csv_timestamp.py <input.csv> or <file_list.txt>")
        sys.exit(1)

    input_arg = sys.argv[1]

    # Case 1: it's a .txt file containing a list of files
    if input_arg.endswith(".txt"):
        if not os.path.exists(input_arg):
            print(f"Error: List file '{input_arg}' not found.")
            sys.exit(1)

        with open(input_arg, 'r') as list_file:
            files = [line.strip() for line in list_file if line.strip()]
            print(f"Found {len(files)} file(s) to process in '{input_arg}'...\n")
            for file_path in files:
                process_file(file_path)

    # Case 2: it's a single CSV file
    else:
        process_file(input_arg)

if __name__ == "__main__":
    main()
