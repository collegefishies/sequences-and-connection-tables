# Script Order
1. `extract_photon_arrival_times.py`
    
    * This converts from the P7888 file format to a usable array of arrival times in absolute units, i.e., relative to the start of the experiment. It saves the result in the HDF file.

2. `plot_photon_arrival_times.py`

	* This simply plots all photon arrival times. Very simple, doesn't need to be run.

3. `cavity_scan_analysis.py`

	* This reads the metadata that holds the types of scans performed, partitions the photon data accordingly, and then performs analysis based on the label.

# Feature List