import cv2
import numpy as np
import matplotlib.pyplot as plt
import pywt

# Load the filtered and unfiltered grayscale images
filtered_image = cv2.imread('sidq/Original images/hat.mat_CIE_D50_Filtered.tif', cv2.IMREAD_GRAYSCALE)
unfiltered_image = cv2.imread('sidq/Original images/hat.mat_CIE_D50.tif', cv2.IMREAD_GRAYSCALE)

# Define images to process
images = {
    "Filtered": filtered_image,
    "Unfiltered": unfiltered_image
}

# 1. Peli Contrast Maps
# Use a series of low-pass filters to create progressively less detailed images
frequencies = [6, 11, 23, 45]  # Start with less blur and progress to more blur
for label, image in images.items():
    peli_contrast_maps = []
    for std_dev in frequencies:
        blurred_image = cv2.GaussianBlur(image, (0, 0), std_dev)
        peli_contrast_maps.append(blurred_image)

    plt.figure(figsize=(16, 8))
    for idx, filtered_image in enumerate(peli_contrast_maps):
        plt.subplot(2, 4, idx + 1)
        plt.imshow(filtered_image, cmap='gray')
        plt.title(f'{label} - Peli at {frequencies[idx]} cycle/image')
        plt.axis('off')
    plt.show()

# 2. Directional Bandlimited Contrast Maps
orientations = [0, np.pi / 4, np.pi / 2, 3 * np.pi / 4]  # Orientations: 0°, 45°, 90°, 135°
frequencies = [6, 11, 23, 45]  # Analogous to cycles per image, from blurrier to more detailed
for label, image in images.items():
    directional_contrast_maps = []
    for frequency in frequencies:
        for orientation in orientations:
            kernel = cv2.getGaborKernel((41, 41), 10.0, orientation, frequency, 0.5, 0, ktype=cv2.CV_32F)
            filtered_image = cv2.filter2D(image, cv2.CV_32F, kernel)
            filtered_image = cv2.normalize(filtered_image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            directional_contrast_maps.append(filtered_image)

    plt.figure(figsize=(16, 16))
    for idx, filtered_image in enumerate(directional_contrast_maps):
        plt.subplot(4, 4, idx + 1)
        plt.imshow(filtered_image, cmap='gray')
        plt.title(f'{label} - Dir {int(np.degrees(orientations[idx % 4]))}° at {frequencies[idx // 4]} cycle/image')
        plt.axis('off')
    plt.show()

# 3. Edge-Based Contrast Maps
block_sizes = [5, 11, 23, 41]  # Start with small block sizes for more detail
for label, image in images.items():
    edge_contrast_maps = []
    for block_size in block_sizes:
        blurred = cv2.GaussianBlur(image, (block_size, block_size), 0)
        edges = cv2.Canny(blurred, 50, 150)
        edge_contrast_maps.append(edges)

    plt.figure(figsize=(16, 8))
    for idx, edge_image in enumerate(edge_contrast_maps):
        plt.subplot(2, 4, idx + 1)
        plt.imshow(edge_image, cmap='gray')
        plt.title(f'{label} - Edge at block size {block_sizes[idx]}')
        plt.axis('off')
    plt.show()

# 4. Wavelet-Based Contrast Maps (From coarse to fine levels)
for label, image in images.items():
    coeffs = pywt.wavedec2(image, 'db1', level=4)  # 'db1' is the Daubechies wavelet
    wavelet_contrast_maps = []
    for i in range(1, len(coeffs)):  # Start from coarser levels and move to finer ones
        cH, cV, cD = coeffs[i]
        wavelet_map = np.sqrt(cH**2 + cV**2 + cD**2)
        wavelet_contrast_maps.append(wavelet_map)

    plt.figure(figsize=(16, 8))
    for idx, wavelet_map in enumerate(wavelet_contrast_maps):
        plt.subplot(2, 4, idx + 1)
        plt.imshow(wavelet_map, cmap='gray')
        plt.title(f'{label} - Wavelet at scale {idx + 1}')
        plt.axis('off')
    plt.show()
