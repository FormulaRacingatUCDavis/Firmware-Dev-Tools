#!/usr/bin/python3
"""
fastfast_parser - made by IanKM

This script parses a fastfast (performance marker) file from UART and converts
it into a human-readable format.
Usage: python3 fastfast_parser.py <uart_file_name>
"""

import sys
import json
from pathlib import Path

MAGIC_NUMBER = 0xFA57FA57

def run(file_name):
    try:
        with open(file_name, mode="rb") as f:
            # Grab header first
            out_file_name = Path(file_name).stem + "-trace.json"
            out = open(out_file_name, "w")

            print("Starting to parse, please wait...")

            # Enter the parse loop
            line_count = 0
            data = {
                "traceEvents": []
            }

            entries = f.read().split(MAGIC_NUMBER.to_bytes(4, "little"))[1::]
            for entry in entries:
                entry_threadid = int.from_bytes(entry[0:4], "little")
                entry_start = int.from_bytes(entry[4:12], "little")
                entry_end = int.from_bytes(entry[12:20], "little")
                entry_scopename = entry[20:52].decode('ascii').replace("\0", "")
                entry_duration = entry_end - entry_start
                marker = {
                    "cat": "function",
                    "dur": (entry_end - entry_start) * 1000 or 1000,
                    "name": entry_scopename,
                    "ph": "X",
                    "pid": 0,
                    "tid": entry_threadid,
                    "ts": entry_start * 1000,
                }
                if (entry_end - entry_start) < 20 and (entry_end - entry_start) > -20:
                    data["traceEvents"].append(marker)

            json.dump(data, out)
            out.close()

            marker_count = len(data["traceEvents"])
            print(f"Finished writing {marker_count} marker{'s' if marker_count != 1 else ''} to {out_file_name}.")
    except FileNotFoundError:
        print(f"Error: file '{file_name}' doesn't exist!")

def main():
    if len(sys.argv) != 2:
        print("Usage: ./python3 fastfast_parser.py <uart_file_name>")
        sys.exit(1)
    
    file_name = sys.argv[1]

    run(file_name)

if __name__ == "__main__":
    main()