import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

def read_csv_data(csv_file):
    """
    Reads the CSV file and returns frequency and snapshot data.
    
    :param csv_file: Path to the CSV file.
    :return: A tuple of (frequencies, snapshots).
    """
    frequencies = []
    snapshots = []

    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # First row is the header with frequencies
        frequencies = np.array([float(freq.split()[0]) for freq in header[1:]])

        for row in reader:
            snapshots.append([float(dbm) for dbm in row[1:]])

    snapshots = np.array(snapshots)  # Convert to numpy array for easier processing
    return frequencies, snapshots


def average_snapshots(snapshots, num_snapshots, threshold=-50):
    """
    Averages the dBm values for each frequency across a subset of snapshots,
    considering only values above the specified dBm threshold.
    
    :param snapshots: Array of snapshot dBm values (each row is a snapshot).
    :param num_snapshots: The number of snapshots to average.
    :param threshold: The dBm threshold for considering values in the average.
    :return: An array of averaged dBm values.
    """
    snapshots_subset = snapshots[:num_snapshots]  # Take only the desired number of snapshots
    mask = snapshots_subset > threshold  # Mask values above the threshold
    valid_values = np.where(mask, snapshots_subset, np.nan)  # Replace values below threshold with NaN
    # Compute the mean, ignoring NaN values
    return np.nanmean(valid_values, axis=0)

def remove_local_minima(averaged_snapshot, threshold):
    """
    Removes local minima in the averaged snapshot that are above the specified threshold 
    by replacing them with the average of their neighbors.
    After replacing, the function starts from the i-1 point.
    
    :param averaged_snapshot: Array of averaged dBm values across all snapshots.
    :param threshold: Minimum dBm value for local minima to be replaced.
    :return: Modified snapshot with local minima removed.
    """
    i = 1  # Start from the second element
    while i < len(averaged_snapshot) - 1:
        print(i)
        # Check if it's a local minimum and if it's above the threshold
        if (averaged_snapshot[i] < averaged_snapshot[i - 1] and 
            averaged_snapshot[i] < averaged_snapshot[i + 1] and 
            averaged_snapshot[i] > threshold):
            # Replace with the average of its neighbors
            averaged_snapshot[i] = (averaged_snapshot[i - 1] + averaged_snapshot[i+1]) /2
            # After modification, step back to i-1 to re-evaluate
            i = max(1, i - 1)  # Ensure we don't go out of bounds
        else:
            i += 1  # Move to the next point only if no modification was made
    return averaged_snapshot

def find_carriers(frequencies, averaged_snapshot, threshold=-50):
    """
    Finds the number of carriers (hills/peaks) in the averaged snapshot and the frequency in the middle of each carrier.
    
    :param frequencies: Array of frequency values.
    :param averaged_snapshot: Array of averaged dBm values across all snapshots.
    :param threshold: Minimum dBm value to be considered as part of a peak.
    :return: List of peak frequencies and number of carriers.
    """

    averaged_snapshot = remove_local_minima(averaged_snapshot, threshold)
    
    # Use a mask to ignore values below the threshold
    snapshot_masked = np.where(averaged_snapshot > threshold, averaged_snapshot, -np.inf)

    # Find the peaks in the masked snapshot
    peaks, _ = find_peaks(snapshot_masked, height=threshold)

    # Extract the frequencies corresponding to the peaks
    peak_frequencies = frequencies[peaks]

    return peak_frequencies, len(peak_frequencies)


def plot_averaged_snapshot_with_peaks(frequencies, averaged_snapshot, peak_frequencies):
    """
    Plots the averaged snapshot with the detected peaks highlighted.
    
    :param frequencies: Array of frequency values.
    :param averaged_snapshot: Array of averaged dBm values across all snapshots.
    :param peak_frequencies: List of detected peak frequencies.
    """
    plt.figure(figsize=(10, 6))
    plt.plot(frequencies, averaged_snapshot, label="Averaged Snapshot (dBm)")
    
    # Mark the detected peaks
    for peak_freq in peak_frequencies:
        plt.axvline(x=peak_freq, color='r', linestyle='--', label=f"Carrier at {peak_freq:.2f} Hz")
    
    plt.title("Averaged Snapshot with Detected Carriers (Peaks)")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("dBm")
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    # csv_file = "recordings/outputslowarm_start865000000.0_stop868000000.0_points100.csv"  # Path to the CSV file
    # csv_file = "recordings\output1_start865000000.0_stop871000000.0_points200.csv"
    csv_file = "recordings\outputfast_start865000000.0_stop871000000.0_points200.csv"
    num_snapshots = 1000  # Specify the number of snapshots to average
    threshold_for_averaging = -40  # Only consider values above this threshold for averaging

    # Read the CSV file and extract frequency and snapshot data
    frequencies, snapshots = read_csv_data(csv_file)

    averaged_snapshot = average_snapshots(snapshots, num_snapshots, threshold=threshold_for_averaging)

    # Find the carriers (peaks) and their corresponding frequencies in the averaged snapshot
    peak_frequencies, num_carriers = find_carriers(frequencies, averaged_snapshot, threshold_for_averaging/2)

    # Print the results
    print(f"Number of carriers: {num_carriers}")
    print(f"Carrier frequencies: {peak_frequencies}")

    # Plot the averaged snapshot with the detected peaks
    plot_averaged_snapshot_with_peaks(frequencies, averaged_snapshot, peak_frequencies)
