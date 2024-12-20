import os
import glob
import matplotlib.pyplot as plt
import cv2
import numpy as np

# Path to the folder containing the images
folder_path = "sidq/Original images"

# Get list of all .tif images (ignoring *_Filtered.tif)
image_paths = sorted(glob.glob(os.path.join(folder_path, "*.tif")))
filtered_paths = [p for p in image_paths if "_Filtered" in p]
original_paths = [p for p in image_paths if "_Filtered" not in p]

# Assuming both filtered and original images are paired correctly
original_paths.sort()
filtered_paths.sort()

# Make sure there are equal number of original and filtered images
num_images = min(len(original_paths), len(filtered_paths))

# Plot the images using matplotlib
fig, axes = plt.subplots(nrows=num_images, ncols=2, figsize=(10, 5 * num_images))
fig.tight_layout(pad=5.0)

for i, (orig_path, filt_path) in enumerate(zip(original_paths[:num_images], filtered_paths[:num_images])):
    # Load original and filtered images
    orig_img = cv2.imread(orig_path, cv2.IMREAD_UNCHANGED)
    filt_img = cv2.imread(filt_path, cv2.IMREAD_UNCHANGED)

    # Normalize the images to the range [0, 255] if needed
    if orig_img.dtype != np.uint8:
        orig_img = cv2.normalize(orig_img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    if filt_img.dtype != np.uint8:
        filt_img = cv2.normalize(filt_img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # Convert BGR to RGB (OpenCV loads images in BGR format by default)
    if len(orig_img.shape) == 3 and orig_img.shape[2] == 3:
        orig_img = cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB)
    if len(filt_img.shape) == 3 and filt_img.shape[2] == 3:
        filt_img = cv2.cvtColor(filt_img, cv2.COLOR_BGR2RGB)

    # Plot original image
    axes[i, 0].imshow(orig_img, cmap='gray' if len(orig_img.shape) == 2 else None)
    axes[i, 0].set_title(f"Original: {os.path.basename(orig_path)}")
    axes[i, 0].axis('off')

    # Plot filtered image
    axes[i, 1].imshow(filt_img, cmap='gray' if len(filt_img.shape) == 2 else None)
    axes[i, 1].set_title(f"Filtered: {os.path.basename(filt_path)}")
    axes[i, 1].axis('off')

# Display the plot
plt.show()
