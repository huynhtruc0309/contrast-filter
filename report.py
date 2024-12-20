import pandas as pd
import numpy as np

# Simulated results for global and local contrast measures
# (Note: Replace these placeholder values with actual computations)
scenes = ["Snow", "Trails", "Tarmac"]

# Simulated global contrast measures (mean for each scene)
global_contrast_data = {
    "Scene": scenes,
    "Max-Min Luminance Ratio": [2.57, 3.1, 2.9],
    "Weber Contrast": [1.57, 1.8, 1.7],
    "Michelson Contrast": [0.38, 0.45, 0.4],
    "RMS Contrast": [0.07, 0.08, 0.06]
}

# Simulated local contrast statistics (mean, variance, max, min) for each scene
local_contrast_data = {
    "Scene": scenes,
    "Mean (Local Contrast)": [0.1, 0.15, 0.12],
    "Variance (Local Contrast)": [0.02, 0.03, 0.025],
    "Max (Local Contrast)": [0.3, 0.4, 0.35],
    "Min (Local Contrast)": [0.01, 0.02, 0.015],
}

# Overall statistics across all scenes
overall_statistics = {
    "Global Contrast": {
        "Max-Min Luminance Ratio": np.mean([2.57, 3.1, 2.9]),
        "Weber Contrast": np.mean([1.57, 1.8, 1.7]),
        "Michelson Contrast": np.mean([0.38, 0.45, 0.4]),
        "RMS Contrast": np.mean([0.07, 0.08, 0.06]),
    },
    "Local Contrast": {
        "Mean": np.mean([0.1, 0.15, 0.12]),
        "Variance": np.mean([0.02, 0.03, 0.025]),
        "Max": np.mean([0.3, 0.4, 0.35]),
        "Min": np.mean([0.01, 0.02, 0.015]),
    }
}

# Create DataFrames for global and local contrast
global_contrast_df = pd.DataFrame(global_contrast_data)
local_contrast_df = pd.DataFrame(local_contrast_data)

# Add overall statistics to the tables
global_contrast_df.loc[len(global_contrast_df)] = ["Overall Average"] + list(overall_statistics["Global Contrast"].values())
local_contrast_df.loc[len(local_contrast_df)] = ["Overall Average"] + list(overall_statistics["Local Contrast"].values())


