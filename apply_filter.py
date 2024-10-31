import os
import numpy as np
import pandas as pd
import spectral
from tkinter import filedialog, Tk
from scipy.interpolate import interp1d

def load_transmission_data(file_path):
    """Load transmission data for AMP and neural glasses from an Excel file."""
    df = pd.read_excel(file_path, sheet_name=None)  # Load all sheets
    amp_transmission = df['Sheet1']['AMP PRO'].values
    neural_transmission = df['Sheet1']['Neutral density filters'].values
    wavelengths = df['Sheet1']['Wavelength (nm)'].values  # Assuming both sheets have the same wavelengths
    
    return wavelengths, amp_transmission, neural_transmission

def match_transmission_to_cube(transmission_wavelengths, transmission_values, cube_wavelengths):
    """Interpolate transmission values to match cube wavelengths if necessary."""
    if not np.array_equal(transmission_wavelengths, cube_wavelengths):
        # Interpolate transmission data to match cube wavelengths
        interpolation_func = interp1d(transmission_wavelengths, transmission_values, kind='linear', fill_value="extrapolate")
        matched_values = interpolation_func(cube_wavelengths)
        if np.any(np.isnan(matched_values)):
            print("Warning: NaN values in matched transmission data.")
        return matched_values
    else:
        return transmission_values

def apply_transmission(cube, transmission):
    """Apply transmission values to the hyperspectral cube."""
    for i in range(cube.shape[2]):
        if np.isnan(transmission[i]):
            print(f"Warning: Transmission value for wavelength index {i} is NaN.")
            continue  # Skip NaN transmission values
        cube[:, :, i] *= transmission[i]
    
    if np.any(np.isnan(cube)):
        print("Warning: NaN values found in the cube after applying transmission.")
        
    return cube

def process_hyperspectral_cubes(input_folder, output_folder_amp, output_folder_neural, amp_transmission, neural_transmission, cube_wavelengths):
    """Read hyperspectral cubes, apply AMP and Neural transmission, and save the results."""
    os.makedirs(output_folder_amp, exist_ok=True)
    os.makedirs(output_folder_neural, exist_ok=True)
    
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.hdr'):
            hdr_path = os.path.join(input_folder, file_name)
            print(hdr_path)
            cube = spectral.open_image(hdr_path).load()
            
            # Extract wavelengths from the hyperspectral cube
            hdr_info = spectral.envi.open(hdr_path)
            cube_wavelengths_from_hdr = np.array([float(wl) for wl in hdr_info.metadata['wavelength']])
            
            # Match transmission data to cube wavelengths
            amp_transmission_matched = match_transmission_to_cube(cube_wavelengths, amp_transmission, cube_wavelengths_from_hdr)
            neural_transmission_matched = match_transmission_to_cube(cube_wavelengths, neural_transmission, cube_wavelengths_from_hdr)
            
            hdr_metadata = hdr_info.metadata
            metadata = hdr_metadata.copy()
            metadata['wavelength'] = hdr_metadata['wavelength']

            # Apply AMP transmission
            amp_cube = apply_transmission(cube.copy(), amp_transmission_matched)
            amp_output_path = os.path.join(output_folder_amp, f"AMP_{file_name}")
            spectral.envi.save_image(amp_output_path, amp_cube, dtype=np.float32, metadata=metadata)
            
            # Apply Neural transmission
            neural_cube = apply_transmission(cube.copy(), neural_transmission_matched)
            neural_output_path = os.path.join(output_folder_neural, f"Neural_{file_name}")
            spectral.envi.save_image(neural_output_path, neural_cube, dtype=np.float32, metadata=metadata)
            
            print(f"Processed and saved AMP and Neural cubes for {file_name}")

def main():
    # Load transmission data from Excel
    file_path = filedialog.askopenfilename(title="Select Transmission Data Excel File", filetypes=[("Excel files", "*.xlsx")])
    wavelengths, amp_transmission, neural_transmission = load_transmission_data(file_path)
    
    # Select the folder containing hyperspectral .hdr images
    root = Tk()
    root.withdraw()  # Hide Tkinter main window
    input_folder = filedialog.askdirectory(title="Select Folder with HDR Hyperspectral Cubes")
    
    # Define output folders
    output_folder_amp = os.path.join(os.path.dirname(input_folder), "DBAMP")
    output_folder_neural = os.path.join(os.path.dirname(input_folder), "DBN")
    
    # Process and apply transmission to each hyperspectral cube
    process_hyperspectral_cubes(input_folder, output_folder_amp, output_folder_neural, amp_transmission, neural_transmission, wavelengths)
    print("Processing completed.")

if __name__ == "__main__":
    main()
