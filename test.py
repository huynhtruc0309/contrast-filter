import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from scipy.interpolate import interp1d
import os
from tkinter import Tk, filedialog

# Function to load reflectances from MATLAB .mat file
def load_mat_file(file_path, var_name):
    """Load a specific variable from a MATLAB .mat file."""
    mat_data = loadmat(file_path)
    return mat_data[var_name]

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
def convert_and_save_images(reflectance_file, illuminant_file, cmf_file):
    # Load reflectances from the .mat file
    reflectances = load_mat_file(reflectance_file, 'reflectances')
    
    # Normalize reflectances as in MATLAB
    reflectances = reflectances / np.max(reflectances)

    # Load illuminant and color matching function (CMF) data
    illuminant = load_mat_file(illuminant_file, os.path.splitext(os.path.basename(illuminant_file))[0]).flatten()
    cmf_data = load_mat_file(cmf_file, 'xyzbar')

    # Create radiance by multiplying reflectance with illuminant values
    radiances = reflectances * illuminant[np.newaxis, np.newaxis, :]

    # Convert radiance to XYZ using CMF
    r, c, w = radiances.shape
    radiances_flat = radiances.reshape((r * c, w))
    XYZ_flat = np.dot(radiances_flat, cmf_data)
    XYZ = XYZ_flat.reshape((r, c, 3))
    XYZ = np.clip(XYZ / np.max(XYZ), 0, 1)

    # Convert XYZ to sRGB
    RGB = xyz_to_srgb(XYZ)

    # Apply gamma correction for sRGB display
    gamma = 0.4  # MATLAB uses 0.4
    RGB_corrected = np.power(RGB, gamma)

    # Save the RGB image
    output_filename = os.path.join(os.path.dirname(reflectance_file), "output_rgb.png")
    plt.imsave(output_filename, RGB_corrected)
    print(f"Saved: {output_filename}")

# Main code to select files and convert images
def main():
    Tk().withdraw()  # Hides the root window

    # Select reflectance, illuminant, and CMF files
    reflectance_file = filedialog.askopenfilename(title="Select Reflectance .mat File", filetypes=[("MAT files", "*.mat")])
    if not reflectance_file:
        print("No reflectance file selected. Exiting.")
        return

    illuminant_file = filedialog.askopenfilename(title="Select Illuminant .mat File", filetypes=[("MAT files", "*.mat")])
    if not illuminant_file:
        print("No illuminant file selected. Exiting.")
        return

    cmf_file = filedialog.askopenfilename(title="Select CMF .mat File", filetypes=[("MAT files", "*.mat")])
    if not cmf_file:
        print("No CMF file selected. Exiting.")
        return

    convert_and_save_images(reflectance_file, illuminant_file, cmf_file)

if __name__ == "__main__":
    main()
