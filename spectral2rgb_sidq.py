import os
import numpy as np
import spectral.io.envi as envi
from tkinter import Tk, filedialog
import matplotlib.pyplot as plt

# Function to convert XYZ to sRGB
def xyz_to_srgb(XYZ):
    """Convert CIE XYZ to sRGB."""
    matrix = np.array([[3.2406, -1.5372, -0.4986],
                       [-0.9689, 1.8758, 0.0415],
                       [0.0557, -0.2040, 1.0570]])
    RGB = np.dot(XYZ, matrix.T)
    return np.clip(RGB, 0, 1)

def process_hdr_file(hdr_file, cmf_file, output_path):
    """Process an HDR file and convert it to an RGB image."""
    print(f"Processing: {hdr_file}")
    try:
        # Load the hyperspectral cube
        cube = envi.open(hdr_file).load()

        # Get the wavelengths from the header
        wavelengths = np.array([float(w) for w in cube.metadata['wavelength']])

        # Load color matching function (CMF)
        cmf_data = np.loadtxt(cmf_file, delimiter=",")  # Assuming CMF is in CSV format
        cmf_wavelengths = cmf_data[:, 0]
        cmf_values = cmf_data[:, 1:4]  # X, Y, Z values

        # Interpolate CMF to match the cube wavelengths
        cmf_interp = np.zeros((len(wavelengths), 3))
        for i in range(3):  # For X, Y, Z
            cmf_interp[:, i] = np.interp(wavelengths, cmf_wavelengths, cmf_values[:, i])

        # Convert radiance to XYZ
        r, c, w = cube.shape
        radiances_flat = cube.reshape((r * c, w))
        XYZ_flat = np.dot(radiances_flat, cmf_interp)
        XYZ = XYZ_flat.reshape((r, c, 3))
        XYZ = np.clip(XYZ / np.max(XYZ), 0, 1)

        # Convert XYZ to sRGB
        RGB = xyz_to_srgb(XYZ)

        # Apply gamma correction
        gamma = 0.4
        RGB_corrected = np.power(RGB, gamma)

        # Save the RGB image
        output_filename = os.path.join(output_path, os.path.basename(hdr_file).replace(".hdr", ".png"))
        plt.imsave(output_filename, RGB_corrected)
        print(f"Saved: {output_filename}")

    except Exception as e:
        print(f"Error processing {hdr_file}: {e}")

def process_folder_structure(input_folder, cmf_file, output_folder):
    """Process all HDR files in the folder structure."""
    print(f"Starting processing for folder: {input_folder}")
    total_files = 0
    processed_files = 0

    for root, _, files in os.walk(input_folder):
        relative_path = os.path.relpath(root, input_folder)
        output_subfolder = os.path.join(output_folder, relative_path)
        os.makedirs(output_subfolder, exist_ok=True)

        for file_name in files:
            if file_name.endswith(".hdr"):
                total_files += 1
                hdr_path = os.path.join(root, file_name)
                process_hdr_file(hdr_path, cmf_file, output_subfolder)
                processed_files += 1

    print(f"Processed {processed_files}/{total_files} HDR files.")
    print(f"All processed images saved in: {output_folder}")

def main():
    """Main function to process all HDR files."""
    Tk().withdraw()  # Hide the root Tkinter window

    # Ask user to select the input folder
    input_folder = filedialog.askdirectory(title="Select Folder with HDR Files")
    if not input_folder:
        print("No folder selected. Exiting.")
        return

    # Ask user to select the CMF file
    cmf_file = filedialog.askopenfilename(title="Select CMF File (CSV)", filetypes=[("CSV files", "*.csv")])
    if not cmf_file:
        print("No CMF file selected. Exiting.")
        return

    # Create the output folder
    output_folder = os.path.join(os.path.dirname(input_folder), "Scott_rgb")
    os.makedirs(output_folder, exist_ok=True)

    # Process the folder structure
    process_folder_structure(input_folder, cmf_file, output_folder)

    print("Processing completed.")

if __name__ == "__main__":
    main()
