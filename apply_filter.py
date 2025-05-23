import os
import numpy as np
import shutil
import spectral
from tkinter import filedialog, Tk
from scipy.interpolate import interp1d

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
    for i in range(cube.shape[2]):
        cube[:, :, i] *= transmission[i]
    return cube

def process_scene(scene_folder, amp_transmission, neural_transmission, cube_wavelengths):
    """Process hyperspectral cubes within a given scene folder."""
    input_original_folder = os.path.join(scene_folder, "original")
    output_amp_folder = os.path.join(scene_folder, "DBAMP")
    output_neural_folder = os.path.join(scene_folder, "DBN")
    
    os.makedirs(output_amp_folder, exist_ok=True)
    os.makedirs(output_neural_folder, exist_ok=True)

    for file_name in os.listdir(input_original_folder):
        if file_name.endswith(".hdr"):
            hdr_path = os.path.join(input_original_folder, file_name)
            raw_path = hdr_path.replace(".hdr", ".raw")
            print(f"Processing: {hdr_path}")

            # Load hyperspectral cube
            cube = spectral.open_image(hdr_path).load()
            cube_metadata = spectral.open_image(hdr_path).metadata
            hdr_wavelengths = np.array([float(w) for w in cube_metadata['wavelength']])

            # Match transmission to cube wavelengths
            amp_transmission_matched = match_transmission_to_cube(hdr_wavelengths, cube_wavelengths, amp_transmission)
            neural_transmission_matched = match_transmission_to_cube(hdr_wavelengths, cube_wavelengths, neural_transmission)

            # Apply AMP transmission
            amp_cube = apply_transmission(cube.copy(), amp_transmission_matched)
            amp_hdr_path = os.path.join(output_amp_folder, file_name)
            spectral.envi.save_image(amp_hdr_path, amp_cube, dtype=np.float32, metadata=cube_metadata)

            # Copy associated raw file
            amp_raw_path = amp_hdr_path.replace(".hdr", ".raw")
            if os.path.exists(raw_path):
                shutil.copy(raw_path, amp_raw_path)

            # Apply Neural transmission
            neural_cube = apply_transmission(cube.copy(), neural_transmission_matched)
            neural_hdr_path = os.path.join(output_neural_folder, file_name)
            spectral.envi.save_image(neural_hdr_path, neural_cube, dtype=np.float32, metadata=cube_metadata)

            # Copy associated raw file
            neural_raw_path = neural_hdr_path.replace(".hdr", ".raw")
            if os.path.exists(raw_path):
                shutil.copy(raw_path, neural_raw_path)

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

    # Process each scene folder
    scene_folders = ["Old-Snow-Scenarios", "Tarmac", "Trails"]
    for scene in scene_folders:
        scene_folder = os.path.join(base_folder, scene)
        process_scene(scene_folder, amp_transmission, neural_transmission, wavelengths)

    print("Processing completed. Output saved in DBAMP and DBN folders for each scene.")

if __name__ == "__main__":
    main()
