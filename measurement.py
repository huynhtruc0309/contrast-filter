import os
import cv2
import numpy as np
from tkinter import filedialog, Tk

# Global contrast methods
def max_min_luminance_ratio(luminance):
    L_max = np.max(luminance)
    L_min = np.min(luminance)
    return L_max / L_min if L_min > 0 else 0

def weber_contrast(luminance):
    L_max = np.max(luminance)
    L_min = np.min(luminance)
    return (L_max - L_min) / L_min if L_min > 0 else 0

def michelson_contrast(luminance):
    L_max = np.max(luminance)
    L_min = np.min(luminance)
    return (L_max - L_min) / (L_max + L_min) if (L_max + L_min) > 0 else 0

def rms_contrast(luminance):
    mean_luminance = np.mean(luminance)
    return np.sqrt(np.mean((luminance - mean_luminance) ** 2))

# Additional contrast metrics
def sipk_contrast(luminance):
    return np.mean(np.abs(luminance - np.mean(luminance)))

def difference_of_gaussians(luminance, sigma1=1.0, sigma2=2.0):
    g1 = cv2.GaussianBlur(luminance, (0, 0), sigma1)
    g2 = cv2.GaussianBlur(luminance, (0, 0), sigma2)
    return np.std(g1 - g2)

def local_mean_difference(luminance, kernel_size=3):
    local_mean = cv2.blur(luminance, (kernel_size, kernel_size))
    return np.mean(np.abs(luminance - local_mean))

def peli_local_band_limited_contrast(luminance, sigma1=1.0, sigma2=2.0):
    lowpass = cv2.GaussianBlur(luminance, (0, 0), sigma2)
    bandpass = cv2.GaussianBlur(luminance, (0, 0), sigma1) - lowpass
    contrast_map = np.divide(bandpass, lowpass + 1e-5)  # Avoid division by zero
    return np.mean(np.abs(contrast_map))

def just_noticeable_difference(luminance):
    mean_luminance = np.mean(luminance)
    return 0.02 + 0.1 * np.sqrt(mean_luminance)

# Define the list of subfolders to process
SUBFOLDERS = ['DBN', 'DBG', 'DBR', 'DBW', 'DBAMP']

# Define contrast metric functions (not shown here for brevity but assume they are the same as in previous code)
def calculate_contrast_measures(image):
    # Convert to grayscale to get luminance
    luminance = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0  # Normalize luminance
    # Calculate contrast measures
    contrast_measures = {
        "max_min_ratio": max_min_luminance_ratio(luminance),
        "weber_contrast": weber_contrast(luminance),
        "michelson_contrast": michelson_contrast(luminance),
        "rms_contrast": rms_contrast(luminance),
        "sipk_contrast": sipk_contrast(luminance),
        "difference_of_gaussians": difference_of_gaussians(luminance),
        "local_mean_difference": local_mean_difference(luminance),
        "peli_local_band_limited": peli_local_band_limited_contrast(luminance),
        "jnd": just_noticeable_difference(luminance)
    }
    return contrast_measures

def calculate_folder_contrast(folder_path):
    """Calculate the average contrast for a single folder of images."""
    contrast_sums = {
        "max_min_ratio": 0,
        "weber_contrast": 0,
        "michelson_contrast": 0,
        "rms_contrast": 0,
        "sipk_contrast": 0,
        "difference_of_gaussians": 0,
        "local_mean_difference": 0,
        "peli_local_band_limited": 0,
        "jnd": 0
    }
    image_count = 0

    for file_name in os.listdir(folder_path):
        if file_name.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif')):
            image_path = os.path.join(folder_path, file_name)
            image = cv2.imread(image_path)
            if image is None:
                print(f"Error loading image {file_name}")
                continue

            contrast_measures = calculate_contrast_measures(image)
            
            # Sum the contrast measures for averaging
            for key in contrast_sums:
                contrast_sums[key] += contrast_measures[key]
            image_count += 1

    if image_count > 0:
        average_contrast = {key: contrast_sums[key] / image_count for key in contrast_sums}
    else:
        average_contrast = {key: 0 for key in contrast_sums}  # Handle empty folders

    return average_contrast

def main():
    root = Tk()
    root.withdraw()  # Hide the root window
    print("Select three folders for contrast evaluation.")

    # Let user select three folders
    folders = [filedialog.askdirectory(title=f"Select Folder {i+1}") for i in range(3)]
    if not all(folders):
        print("Selection of all three folders is required.")
        return

    # Dictionary to hold total contrast measures for each subfolder across all main folders
    contrast_keys = ["max_min_ratio", "weber_contrast", "michelson_contrast", "rms_contrast", 
                 "sipk_contrast", "difference_of_gaussians", "local_mean_difference", 
                 "peli_local_band_limited", "jnd"]

    overall_contrast_sums = {subfolder: {key: 0 for key in contrast_keys} for subfolder in SUBFOLDERS}
    subfolder_counts = {subfolder: 0 for subfolder in SUBFOLDERS}  # Counts for averaging later

    # Process each main folder
    for main_folder in folders:
        print(f"\nProcessing main folder: {main_folder}")

        for subfolder in SUBFOLDERS:
            subfolder_path = os.path.join(main_folder, subfolder)
            if not os.path.isdir(subfolder_path):
                print(f"Subfolder {subfolder} not found in {main_folder}. Skipping.")
                continue
            
            print(f"  Processing subfolder: {subfolder}")
            # Calculate average contrast for the current subfolder
            avg_contrast = calculate_folder_contrast(subfolder_path)
            
            # Sum the contrast measures for final averaging across all main folders
            for key in overall_contrast_sums[subfolder]:
                overall_contrast_sums[subfolder][key] += avg_contrast[key]
            subfolder_counts[subfolder] += 1

    # Calculate the overall average contrast for each subfolder across the three main folders
    print("\nOverall Average Contrast Metrics across all chosen folders for each subfolder:")
    for subfolder in SUBFOLDERS:
        if subfolder_counts[subfolder] > 0:
            avg_contrast_metrics = {key: overall_contrast_sums[subfolder][key] / subfolder_counts[subfolder] for key in overall_contrast_sums[subfolder]}
        else:
            avg_contrast_metrics = {key: 0 for key in overall_contrast_sums[subfolder]}  # Handle empty subfolders
        
        print(f"\nSubfolder: {subfolder}")
        for method, value in avg_contrast_metrics.items():
            print(f"  {method}: {value:.4f}")

if __name__ == "__main__":
    main()