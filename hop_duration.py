import csv
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

def read_csv_for_fhss_analysis(csv_file, dBm_threshold=-90):
    """
    Reads the CSV file, extracts snapshots, and analyzes frequency hop duration.
    
    :param csv_file: Path to the CSV file.
    :param dBm_threshold: dBm threshold to identify a frequency as a carrier.
    """
    
    frequencies = []
    snapshots = []

    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # First row is the header with frequencies
        
        # Extract frequencies from the header (ignoring 'Snapshot' label)
        frequencies = [float(freq.split()[0]) for freq in header[1:]]
        
        # Read the snapshot data (dBm values)
        for row in reader:
            snapshots.append([float(dbm) for dbm in row[1:]])

    # Convert to numpy arrays for easier analysis
    frequencies = np.array(frequencies)
    snapshots = np.array(snapshots)
    
    # Analyze FHSS: Find carriers by detecting peaks above the dBm threshold
    carriers_by_snapshot = defaultdict(list)
    for idx, snapshot in enumerate(snapshots):
        carrier_indices = np.where(snapshot > dBm_threshold)[0]  # Find indices where dBm is above threshold
        carrier_frequencies = frequencies[carrier_indices]  # Get corresponding frequencies
        carriers_by_snapshot[idx] = carrier_frequencies

    all_carriers = np.concatenate(list(carriers_by_snapshot.values()))
    # Count and print the number of empty carriers_by_snapshot
    empty_snapshots_count = sum(1 for carriers in carriers_by_snapshot.values() if len(carriers) == 0)
    print(f"Number of empty carriers_by_snapshot: {empty_snapshots_count} snapshots: {len(snapshots)}")
    prev_carriers = carriers_by_snapshot[0]
    cnt_hops = 0
    hops = []
    for idx in range(1, len(snapshots)):
        curr_carriers = carriers_by_snapshot[idx]
        if (len(curr_carriers) == 0):
            hops.append(0)
            continue
        
        if not np.array_equal(prev_carriers, curr_carriers):
            cnt_hops = cnt_hops + 1
            hops.append(1)
        else:
            hops.append(1)

        prev_carriers = curr_carriers

    hop_duration = len(snapshots) / cnt_hops

    return {
        "hop_duration": hop_duration,
        "hops": hops
    }


if __name__ == "__main__":
    # Scan happens each 10.7ms
    csv_file = "recordings/outputvbw_start865000000.0_stop870000000.0_points25.csv"  # Path to the CSV file
   
    # Scan happens each 10.7ms
    # csv_file = "recordings/output200hz_start865000000.0_stop870000000.0_points25.csv"  # Path to the CSV file

    dBm_threshold = -40  # dBm threshold to detect carrier frequencies

    # Analyze the FHSS from the CSV file
    analysis_results = read_csv_for_fhss_analysis(csv_file, dBm_threshold)

    print(f"Average Hop Duration: {analysis_results['hop_duration']*0.0107} seconds")
    
    plt.figure(figsize=(10, 4))
    plt.plot(analysis_results['hops'][:200], marker='o', linestyle='-', markersize=2)
    plt.title('Hops Distribution')
    plt.xlabel('Snapshot Index')
    plt.ylabel('Hop (0 or 1)')
    plt.grid(True)
    plt.show()
