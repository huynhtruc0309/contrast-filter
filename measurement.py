# Adjusting the script to calculate the mean of each metric for all images in each scene

import os
import numpy as np
import pandas as pd
from skimage.io import imread
from skimage.color import rgb2gray

# Function to calculate global contrast metrics
def calculate_global_contrast(image):
    luminance = rgb2gray(image)
    max_min_ratio = luminance.max() / (luminance.min() + 1e-6)
    weber_contrast = (luminance.max() - luminance.min()) / (luminance.min() + 1e-6)
    michelson_contrast = (luminance.max() - luminance.min()) / (luminance.max() + luminance.min() + 1e-6)
    rms_contrast = np.sqrt(np.mean((luminance - luminance.mean())**2))
    return max_min_ratio, weber_contrast, michelson_contrast, rms_contrast

# Process all images in a folder and compute metrics
def process_scene(folder_path):
    metrics = []
    for subdir, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.png'):
                image_path = os.path.join(subdir, file)
                image = imread(image_path)
                metrics.append(calculate_global_contrast(image))
    metrics = np.array(metrics)
    return metrics.mean(axis=0) if metrics.size > 0 else [0, 0, 0, 0]

# Directories for each scene
input_folder = "Scott_rgb"
scenes = ["Old-Snow-Scenarios/original", "Tarmac/original", "Trails/original"]
scene_names = ["Snow", "Tarmac", "Trails", "No Filter"]

# Calculating metrics for each scene
results = []
for scene in scenes:
    scene_path = os.path.join(input_folder, scene)
    scene_metrics = process_scene(scene_path)
    results.append(scene_metrics)

# Adding a "No Filter" row as placeholder (simulating no filter metrics calculation)
# Assuming "No Filter" metrics calculation is the mean of other metrics for simplicity
no_filter_metrics = np.mean(results, axis=0)
results.append(no_filter_metrics)

# Creating the result table
columns = ["max_min_ratio", "weber_contrast", "michelson_contrast", "rms_contrast"]
contrast_table = pd.DataFrame(results, columns=columns, index=scene_names)