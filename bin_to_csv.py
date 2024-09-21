import sys
import os
import struct
import csv
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

def read_binary_file(input_file, snapshot_size, buffer_size):
    """
    Generator function to read binary data from a file in chunks and yield snapshots one by one.
    
    :param input_file: Path to the binary data file.
    :param snapshot_size: Size of one snapshot in bytes (including '{' and '}').
    :param buffer_size: Number of snapshots to process in one buffer.
    :return: Yields individual snapshots from the binary file.
    """
    buffer_byte_size = snapshot_size * buffer_size  # Size of the buffer in bytes

    with open(input_file, 'rb') as infile:
        while True:
            # Read buffer_size snapshots at a time
            buffer_data = infile.read(buffer_byte_size)
            if not buffer_data:
                break  # No more data to read

            # Ensure that the data read has complete snapshots
            if len(buffer_data) % snapshot_size != 0:
                logging.warning("Last snapshot in the buffer is incomplete. Discarding it.")
                buffer_data = buffer_data[:-(len(buffer_data) % snapshot_size)]

            # Process each snapshot in the buffer
            for snapshot_start in range(0, len(buffer_data), snapshot_size):
                snapshot_data = buffer_data[snapshot_start:snapshot_start + snapshot_size]

                # Ensure the snapshot starts with '{' and ends with '}'
                if snapshot_data[0] != ord('{') or snapshot_data[-1] != ord('}'):
                    logging.warning("Corrupted or incomplete snapshot found. Discarding it.")
                    continue

                yield snapshot_data


def bin_to_csv(input_file, output_file, points, start_freq, stop_freq, scan_duration, buffer_size=10):
    """
    Parse binary data from a file and convert it to CSV, handling snapshots surrounded by {}.
    
    :param input_file: Path to the binary data file.
    :param output_file: Path to the output CSV file.
    :param points: Number of points expected in each scan.
    :param start_freq: Start frequency in Hz.
    :param stop_freq: Stop frequency in Hz.
    :param buffer_size: Number of snapshots to read from file in one buffer.
    :return: None
    """
    
    # Calculate frequencies
    frequencies = np.linspace(start_freq, stop_freq, points)
    
    # Each point consists of 'x' followed by 2 bytes (LSB and MSB), so each block is 3 bytes long
    snapshot_size = points * 3 + 2  # Size of one snapshot in bytes (including '{' and '}')

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write the header (frequencies)
        header = ['Snapshot'] + [f"{freq:.2f} Hz" for freq in frequencies]
        writer.writerow(header)

        snapshot_count = 0

        # Use the generator to read the binary file, yielding each snapshot
        for snapshot_data in read_binary_file(input_file, snapshot_size, buffer_size):
            snapshot_data = snapshot_data[1:-1]  # Remove the surrounding braces '{}'
            snapshot_values = []

            for i in range(points):
                # Each point has the format: 'x' LSB MSB
                x_char = snapshot_data[3 * i]  # This should be 'x'
                lsb = snapshot_data[3 * i + 1]
                msb = snapshot_data[3 * i + 2]

                # Validate that the 'x' character is present
                if chr(x_char) != 'x':
                    logging.warning(f"Expected 'x' character at position {3 * i}, but got {chr(x_char)}. Discarding snapshot.")
                    snapshot_values = None
                    break

                # Combine LSB and MSB to form a 16-bit signed value (little-endian)
                value = struct.unpack("<h", bytes([lsb, msb]))[0]

                # Convert the value to dBm (TinySA Ultra adjustment)
                dBm = (value / 32.0) - 174
                snapshot_values.append(dBm)

            if snapshot_values:
                snapshot_count += 1
                # Write the snapshot dBm values to the CSV file
                writer.writerow([f"Sweep {snapshot_count}"] + snapshot_values)

    scan_time = scan_duration / snapshot_count
    print(f"CSV file written to {output_file} with {snapshot_count} snapshots. scan_time={scan_time}ms")


if __name__ == "__main__":
    if len(sys.argv) < 5 or len(sys.argv) > 6:
        print("Usage: python bin_to_csv.py <filename> <points> <start_freq> <stop_freq> [buffer_size]")
        sys.exit(1)

    filename = sys.argv[1]
    input_file = os.path.join("recordings", f"{filename}.bin")
    output_file = os.path.join("recordings", f"{filename}.csv")
    points = int(sys.argv[2])
    start_freq = float(sys.argv[3])
    stop_freq = float(sys.argv[4])
    buffer_size = int(sys.argv[5]) if len(sys.argv) == 6 else 10  # Default buffer_size to 10 if not provided

    bin_to_csv(input_file, output_file, points, start_freq, stop_freq, buffer_size)
