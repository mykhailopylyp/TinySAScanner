import csv
import matplotlib.pyplot as plt
import numpy as np

def read_csv_and_plot(csv_file, num_snapshots):
    """
    Reads the CSV file, extracts the specified number of snapshots, and plots them.
    
    :param csv_file: Path to the CSV file.
    :param num_snapshots: Number of snapshots to plot.
    """
    
    frequencies = []
    snapshots = []

    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # First row is the header with frequencies
        
        # Extract frequencies from the header (ignoring 'Snapshot' label)
        frequencies = [float(freq.split()[0]) for freq in header[1:]]
        
        # Read the snapshot data
        for row in reader:
            if len(snapshots) < num_snapshots:
                snapshots.append([float(dbm) for dbm in row[1:]])  # Collect dBm values for each snapshot
            else:
                break  # Stop reading if the required number of snapshots is read

    if not snapshots:
        print("No snapshots available for plotting.")
        return

    # Convert frequencies and snapshots to NumPy arrays for easier plotting
    frequencies = np.array(frequencies)
    snapshots = np.array(snapshots)

    # Plot the snapshots
    plt.figure(figsize=(10, 6))
    for idx, snapshot in enumerate(snapshots):
        plt.plot(frequencies, snapshot, label=f"Snapshot {idx + 1}")

    plt.title(f"Plot of {num_snapshots} Snapshots")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("dBm")
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    # csv_file = "recordings\outputslowarm_start865000000.0_stop867000000.0_points100.csv"  # Path to the CSV file
    csv_file = "recordings\outputslowarm_start865000000.0_stop868000000.0_points100.csv"  # Path to the CSV file
    # csv_file = "recordings\output_start865000000.0_stop868000000.0_points1000.csv"  # Path to the CSV file
    num_snapshots = 8  # Number of snapshots to plot

    read_csv_and_plot(csv_file, num_snapshots)
