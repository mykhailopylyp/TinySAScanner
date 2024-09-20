import numpy as np
from scipy.signal import find_peaks
from utils import calculate_euclidean_distance,plot_averaged_snapshot_with_peaks,read_csv_data

def scale_snapshots(snapshots):
    # Calculate the minimum and maximum values along the last two axes (for each 2D snapshot)
    min_vals = np.nanmin(snapshots, axis=1, keepdims=True)
    max_vals = np.nanmax(snapshots, axis=1, keepdims=True)
    # Prevent division by zero by setting max_vals equal to min_vals where they are equal
    ranges = max_vals - min_vals
    ranges[ranges == 0] = 1  # If min == max, set range to 1 to avoid division by zero

    # Normalize the snapshots array using broadcasting
    scaled_snapshots = (snapshots - min_vals) / ranges
    
    return scaled_snapshots

def square_and_average_snapshots(snapshots):
    # Square each element in the snapshots
    squared_snapshots =  snapshots ** 16
    # Take the average value across all elements and snapshots
    average_value = np.nanmean(squared_snapshots,axis=0)
    # print(average_value)
    return average_value
    
def find_carriers(frequencies, avereged_snaphot):
    min_distance = len(frequencies)//20  # Minimum number of data points between peaks

    # Find peaks with the distance constraint
    threshold = np.mean(avereged_snaphot)
    peaks, _ = find_peaks(avereged_snaphot,height=threshold, distance=min_distance)
    peak_frequencies = frequencies[peaks]
    return peak_frequencies

if __name__ == "__main__":
    # csv_file = "recordings/outputslowarm_start865000000.0_stop868000000.0_points100.csv"  # Path to the CSV file
    # csv_file = "recordings\output1_start865000000.0_stop871000000.0_points200.csv"
    csv_file = "../recordings/outputfast_start865000000.0_stop871000000.0_points200.csv"
    # csv_file = "recordings\outputnew_start865000000.0_stop871000000.0_points200.csv"
    # csv_file = "../recordings/outputfast_start865000000.0_stop871000000.0_points450.csv"

    # # Read the CSV file and extract frequency and snapshot data
    frequencies, snapshots = read_csv_data(csv_file)

    scaled_snaphots = scale_snapshots(snapshots)
    avereged_snaphot = square_and_average_snapshots(scaled_snaphots)

    peaks = find_carriers(frequencies, avereged_snaphot)
    print(f"Number of carriers {len(peaks)}")
    print(f"Carriers {peaks}")

    # distance = calculate_euclidean_distance(peaks)
    # print(f"Euclidian distance with actual frequencies={distance}")

    # Plot the average value
    plot_averaged_snapshot_with_peaks(frequencies, avereged_snaphot, peaks)

