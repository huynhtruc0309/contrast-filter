import os
import numpy as np
import shutil
from tkinter import filedialog, Tk
from scipy.interpolate import interp1d
import h5py

def load_transmission_data(file_path):
    """Load transmission data for AMP and neural glasses from an Excel file."""
    import pandas as pd
    df = pd.read_excel(file_path)
    wavelengths = df['Wavelength (nm)'].values
    amp_transmission = df['AMP PRO'].values
    neural_transmission = df['Neutral density filters'].values
    return wavelengths, amp_transmission, neural_transmission

def match_transmission_to_cube(cube_wavelengths, transmission_wavelengths, transmission_values):
    """Interpolate transmission values to match cube wavelengths."""
    interpolation_func = interp1d(transmission_wavelengths, transmission_values, kind='linear', fill_value="extrapolate")
    return interpolation_func(cube_wavelengths)

def apply_transmission(cube, transmission):
    """Apply transmission values to the hyperspectral cube."""
    for i in range(cube.shape[0]):
        cube[:, :, i] *= transmission[i]
    return cube

def process_scene(scene_folder, amp_transmission, neural_transmission, cube_wavelengths):
    """Process hyperspectral cubes within a given scene folder."""
    input_original_folder = os.path.join(scene_folder, "Original images")
    output_amp_folder = os.path.join(scene_folder, "DBAMP")
    output_neural_folder = os.path.join(scene_folder, "DBN")
    
    os.makedirs(output_amp_folder, exist_ok=True)
    os.makedirs(output_neural_folder, exist_ok=True)

    for file_name in os.listdir(input_original_folder):
        if file_name.endswith(".mat"):
            mat_path = os.path.join(input_original_folder, file_name)
            print(f"Processing: {mat_path}")

            # Load hyperspectral cube
            cube = h5py.File(mat_path, 'r')['hsi'][:]
            wavelengths = np.linspace(410, 1000, 160)

            # Match transmission to cube wavelengths
            amp_transmission_matched = match_transmission_to_cube(wavelengths, cube_wavelengths, amp_transmission)
            neural_transmission_matched = match_transmission_to_cube(wavelengths, cube_wavelengths, neural_transmission)
            # Apply AMP transmission
            amp_cube = apply_transmission(cube.copy(), amp_transmission_matched)
            amp_mat_path = os.path.join(output_amp_folder, file_name)
            with h5py.File(amp_mat_path, 'w') as file:
                file.create_dataset('hsi', data=amp_cube)

            # Apply Neural transmission
            neural_cube = apply_transmission(cube.copy(), neural_transmission_matched)
            neural_mat_path = os.path.join(output_neural_folder, file_name)
            with h5py.File(neural_mat_path, 'w') as file:
                file.create_dataset('hsi', data=neural_cube)

            print(f"Saved processed AMP and Neural cubes for {file_name}")

def main():
    Tk().withdraw()  # Hide the root Tkinter window

    # Load transmission data
    transmission_file = filedialog.askopenfilename(title="Select Transmission Data Excel File", filetypes=[("Excel files", "*.xlsx")])
    wavelengths, amp_transmission, neural_transmission = load_transmission_data(transmission_file)

    # Select base folder containing scenes
    base_folder = filedialog.askdirectory(title="Select Base Folder with Scene Subfolders")
    if not base_folder:
        print("No folder selected. Exiting.")
        return

    process_scene(base_folder, amp_transmission, neural_transmission, wavelengths)

    print("Processing completed. Output saved in DBAMP and DBN folders for each scene.")

if __name__ == "__main__":
    main()
