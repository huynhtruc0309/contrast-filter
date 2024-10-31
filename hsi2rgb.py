import numpy as np
import spectral
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import os
from tkinter import Tk
from tkinter import filedialog
import pandas as pd

# Function to load the hyperspectral image
def load_hyperspectral_image(file_path):
    hdr_image = spectral.open_image(file_path)
    cube = hdr_image.load()
    return cube

def load_csv_data(file_path):
    """Load wavelength and values from a CSV file."""
    df = pd.read_csv(file_path)
    wavelengths = df.iloc[:, 0].values  # First column for wavelengths
    values = df.iloc[:, 1].values       # Second column for corresponding values
    return wavelengths, values

# Function to convert XYZ to sRGB
def xyz_to_srgb(XYZ):
    matrix = np.array([[3.2406, -1.5372, -0.4986],
                       [-0.9689, 1.8758, 0.0415],
                       [0.0557, -0.2040, 1.0570]])
    RGB = np.dot(XYZ, matrix.T)
    return np.clip(RGB, 0, 1)

def match_values_to_cube(cube_wavelengths, target_wavelengths, target_values):
    """Interpolate target values to match cube wavelengths."""
    interpolation_func = interp1d(target_wavelengths, target_values, kind='linear', fill_value="extrapolate")
    return interpolation_func(cube_wavelengths)

# Function to convert and save RGB images
def convert_and_save_images(folder_path, illuminant_file, cmf_file):
    # Load illuminant and CMF data
    illuminant_wavelengths, illuminant_values = load_csv_data(illuminant_file)
    cmf_wavelengths, cmf_values = load_csv_data(cmf_file)

    # Create the output directory with illuminant and CMF info
    illuminant_name = os.path.splitext(os.path.basename(illuminant_file))[0]
    cmf_name = os.path.splitext(os.path.basename(cmf_file))[0]
    output_root = os.path.join(os.path.dirname(folder_path), f'crop_rgb_{illuminant_name}_{cmf_name}')
    os.makedirs(output_root, exist_ok=True)

    # Iterate through each folder and file
    for dirpath, _, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith('.hdr'):
                file_path = os.path.join(dirpath, filename)
                cube = load_hyperspectral_image(file_path)

                # Extract wavelengths from the hyperspectral cube
                hdr_info = spectral.envi.open(file_path)
                cube_wavelengths = np.array(hdr_info.metadata['wavelength'])

                # Match illuminant and CMF values to the cube's wavelengths
                matched_illuminant = match_values_to_cube(cube_wavelengths, illuminant_wavelengths, illuminant_values)
                matched_cmf = match_values_to_cube(cube_wavelengths, cmf_wavelengths, cmf_values)
                
                # Convert Reflectance to Radiance
                radiance = cube * matched_illuminant[np.newaxis, np.newaxis, :]

                # Transform Radiance to CIE XYZ
                r, c, w = radiance.shape
                radiance_flat = radiance.reshape((r * c, w))
                XYZ_flat = np.dot(radiance_flat, matched_cmf)
                XYZ = XYZ_flat.reshape((r, c, 1)) 
                XYZ = np.concatenate([XYZ, XYZ, XYZ], axis=2) 
                XYZ = np.clip(XYZ / np.max(XYZ), 0, 1)

                # Convert XYZ to sRGB
                RGB = xyz_to_srgb(XYZ)

                # Apply gamma correction for sRGB display
                gamma = 2.2
                RGB_corrected = np.power(RGB, 1/gamma)

                # Create output subfolder structure
                relative_path = os.path.relpath(dirpath, folder_path)
                output_subfolder = os.path.join(output_root, relative_path)
                os.makedirs(output_subfolder, exist_ok=True)

                # Save the RGB image
                output_filename = os.path.join(output_subfolder, f"{os.path.splitext(filename)[0]}_rgb.png")
                plt.imsave(output_filename, RGB_corrected)

                print(f"Saved: {output_filename}")

# Main code to select folder and convert images
def main():
    Tk().withdraw()  # Hides the root window
    folder_path = filedialog.askdirectory(title='Select Folder with HDR Images')

    # Select illuminant file
    illuminant_file = filedialog.askopenfilename(title="Select Illuminant CSV File", filetypes=[("CSV files", "*.csv")])
    if not illuminant_file:
        print("No illuminant file selected. Exiting.")
        return

    # Select CMF file
    cmf_file = filedialog.askopenfilename(title="Select CMF CSV File", filetypes=[("CSV files", "*.csv")])
    if not cmf_file:
        print("No CMF file selected. Exiting.")
        return

    convert_and_save_images(folder_path, illuminant_file, cmf_file)

if __name__ == "__main__":
    main()
