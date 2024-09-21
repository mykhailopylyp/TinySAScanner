import numpy as np
from scipy.signal import find_peaks
from utils import calculate_euclidean_distance,plot_averaged_snapshot_with_peaks,read_csv_data,ternary_search,scale_snapshots
from scipy.optimize import minimize_scalar
from average_square_analyzer import square_and_average_snapshots, find_carriers

# Cost function: sum of squared differences between snapshot values and nearest carrier values
def cost_function(f_start, f_spread, num_carriers, averaged_snapshot, frequencies):
    cost = 0
    max_f = np.max(frequencies)
    for i in range(len(averaged_snapshot)):
        if np.isnan(averaged_snapshot[i]):
            continue
        nearest = nearest_carrier(frequencies[i], f_start, f_spread, num_carriers)
        cost += (((frequencies[i] - nearest)/max_f)**2)*averaged_snapshot[i]

    # print(f"f_start={f_start}, cost={cost}")
    return cost

# Function to optimize the start frequency using minimize_scalar
def optimize_start_frequency(f_spread, num_carriers, averaged_snapshot, frequencies, search_range):
    result = minimize_scalar(
        cost_function, 
        bounds=search_range, 
        args=(f_spread, num_carriers, averaged_snapshot, frequencies),
        method='bounded'  # Bounded method ensures the search is within the specified range
    )
    
    # Return the optimized start frequency and the cost
    return result.x, result.fun

# Function to find the nearest carrier for a given index
def nearest_carrier(freq, f_start, f_spread, num_carriers):
    # Compute the position of all carriers
    carrier_positions = f_start + np.arange(num_carriers) * f_spread
    
    # Find the closest carrier to the given index
    return carrier_positions[np.argmin(np.abs(carrier_positions - freq))]

if __name__ == "__main__":
    # csv_file = "recordings/outputslowarm_start865000000.0_stop868000000.0_points100.csv"  # Path to the CSV file
    # csv_file = "recordings\output1_start865000000.0_stop871000000.0_points200.csv"
    csv_file = "../recordings/outputfast_start865000000.0_stop871000000.0_points200.csv"
    # csv_file = "../recordings/output47_start865000000.0_stop871000000.0_points75.csv"
    # csv_file = "../recordings/output47_start865000000.0_stop871000000.0_points600.csv"
    # csv_file = "recordings\outputnew_start865000000.0_stop871000000.0_points200.csv"
    # csv_file = "../recordings/outputfast_start865000000.0_stop871000000.0_points450.csv"

    # Read the CSV file and extract frequency and snapshot data
    frequencies, snapshots = read_csv_data(csv_file)
    scaled_snaphots = scale_snapshots(snapshots)
    averaged_snapshot = square_and_average_snapshots(scaled_snaphots)
    peaks = find_carriers(frequencies, averaged_snapshot)
    num_carriers = len(peaks)
    start = 865*1000*1000
    end = 870*1000*1000
    # Find the first frequency that is bigger than 'end' and remove all frequencies that are bigger than 'end' from 'frequencies'
    # Also, remove corresponding values from 'averaged_snapshot'
    first_index_bigger_than_end = np.argmax(frequencies > end)
    frequencies = frequencies[:first_index_bigger_than_end]
    averaged_snapshot = averaged_snapshot[:first_index_bigger_than_end]

    def cost_function_for_freq_spread(freq_spread):
        _, cost = optimize_start_frequency(freq_spread, num_carriers, averaged_snapshot, frequencies, [start, end])
        return cost

    f_spread_opt = ternary_search(cost_function_for_freq_spread, 0, 1000*1000*10)
    f_start_opt, cost = optimize_start_frequency(f_spread_opt, num_carriers, averaged_snapshot, frequencies, [start, end])
    print(f"cost={cost}")
    print(f"start frequency={f_start_opt}")
    print(f"frequency spread={f_spread_opt}")

    # Generate the optimized carrier positions
    optimized_carriers = f_start_opt + np.arange(num_carriers) * f_spread_opt

    print(f"Number of carriers {len(optimized_carriers)}")
    print(f"Carriers {optimized_carriers}")

    distance = calculate_euclidean_distance(optimized_carriers)
    print(f"Euclidian distance with actual frequencies={distance}")

    # Plot the average value
    plot_averaged_snapshot_with_peaks(frequencies, averaged_snapshot, optimized_carriers)

