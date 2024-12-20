import cv2
import numpy as np
import scipy.ndimage
import matplotlib.pyplot as plt
from scipy.signal import convolve2d

# Load the grayscale image
image = cv2.imread('sidq/Original images/leaves1.mat_CIE_D50.tif', cv2.IMREAD_GRAYSCALE)

# 1. Peli's Band-Limited Contrast
# Define a set of cos-log bandpass filters
filters = [scipy.ndimage.gaussian_filter(image, sigma) for sigma in [1, 2, 4, 8]]
contrast_maps_peli = []
for k in range(1, len(filters)):
    g_k = filters[k] - filters[k - 1]  # Image component in the kth channel (bandpass)
    b_k = filters[k - 1]  # Lowpass component below kth channel
    contrast_map = g_k / (b_k + 1e-6)  # Avoid division by zero
    contrast_maps_peli.append(contrast_map)

# 2. Difference of Gaussians (DoG) Contrast
r_c = 3  # Radius for center zone
r_s = 6  # Radius for surround zone
h_c = np.exp(-((np.arange(-r_c*3, r_c*3+1)/r_c)**2))  # Gaussian kernel for center zone
h_s = 0.85 * (r_c / r_s)**2 * np.exp(-((np.arange(-r_s*3, r_s*3+1)/r_s)**2))  # Gaussian kernel for surround zone

# Convolve image with the filters
R_c = convolve2d(image, np.outer(h_c, h_c), mode='same')
R_s = convolve2d(image, np.outer(h_s, h_s), mode='same')

# Calculate DoG contrast for the three possible formulations
C1_DoG = (R_c - R_s) / (R_c + 1e-6)
C2_DoG = (R_c - R_s) / (R_s + 1e-6)
C3_DoG = (R_c - R_s) / (R_c + R_s + 1e-6)

# 3. Ahumada and Beard Contrast
# Apply Gaussian low-pass filters sequentially
h1 = scipy.ndimage.gaussian_filter(image, sigma=2)
g1 = scipy.ndimage.gaussian_filter(h1, sigma=2)

h2 = scipy.ndimage.gaussian_filter(g1, sigma=2)

C_AB = g1 / (h2 + 1e-6) - 1

# 4. Iordache et al. Contrast
# Calculate average of 8 neighboring luminance values
kernel = np.ones((3, 3)) / 8
kernel[1, 1] = 0  # Exclude the center pixel
b_s = convolve2d(image, kernel, mode='same', boundary='symm')
C_IBL = image / (b_s + 1e-6)

# Plot all contrast maps alongside the original grayscale image
plt.figure(figsize=(8, 8))

# Original Image
plt.subplot(4, 3, 1)
plt.imshow(image, cmap='gray')
plt.title('Original Grayscale Image')
plt.axis('off')

# Peli's Band-Limited Contrast Maps
for idx, contrast_map in enumerate(contrast_maps_peli):
    plt.subplot(4, 3, idx + 2)
    plt.imshow(contrast_map, cmap='gray')
    plt.title(f'Peli Contrast Map {idx + 1}')
    plt.axis('off')

# DoG Contrast Maps
plt.subplot(4, 3, 5)
plt.imshow(C1_DoG, cmap='gray')
plt.title('DoG Contrast C1')
plt.axis('off')

plt.subplot(4, 3, 6)
plt.imshow(C2_DoG, cmap='gray')
plt.title('DoG Contrast C2')
plt.axis('off')

plt.subplot(4, 3, 7)
plt.imshow(C3_DoG, cmap='gray')
plt.title('DoG Contrast C3')
plt.axis('off')

# Ahumada and Beard Contrast Map
plt.subplot(4, 3, 8)
plt.imshow(C_AB, cmap='gray')
plt.title('Ahumada and Beard Contrast')
plt.axis('off')

# Iordache et al. Contrast Map
plt.subplot(4, 3, 9)
plt.imshow(C_IBL, cmap='gray')
plt.title('Iordache et al. Contrast')
plt.axis('off')

plt.tight_layout()
plt.show()
