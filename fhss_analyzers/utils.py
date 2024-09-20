
import csv
import numpy as np
import matplotlib.pyplot as plt

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

def calculate_euclidean_distance(peak_frequencies, num_carriers=13, freq_range=(865275000, 869575000)):
    """
    Calculates the Euclidean distance between detected peak frequencies and the actual carrier frequencies.
    
    :param peak_frequencies: Array of detected peak frequencies.
    :param num_carriers: The number of evenly spaced carriers (default is 13).
    :param freq_range: A tuple specifying the range of carrier frequencies (default is (865275000, 869575000)).
    :return: The Euclidean distance between the detected and actual carrier frequencies.
    """
    # Generate the actual carrier frequencies, evenly spaced in the specified range
    actual_carriers = np.linspace(freq_range[0], freq_range[1], num_carriers)
    
    # actual_carriers /= freq_range[1]
    # carriers = peak_frequencies / freq_range[1]
    carriers = peak_frequencies
    # Ensure that the lengths of the peak_frequencies and actual_carriers match
    if len(carriers) != num_carriers:
        raise ValueError(f"Length of peak_frequencies ({len(carriers)}) must match the number of carriers ({num_carriers}).")
    
    # Calculate the Euclidean distance between the detected and actual carrier frequencies
    euclidean_distance = np.linalg.norm(carriers - actual_carriers)/num_carriers
    
    return euclidean_distance