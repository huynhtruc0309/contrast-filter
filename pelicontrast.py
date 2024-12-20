import numpy as np
import cv2
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

def peli_contrast(image, sigma=1.5):
    """
    Compute Peli's Local Band-Limited Contrast for an image.
    Args:
        image: Grayscale input image.
        sigma: Standard deviation for Gaussian filter (controls the bandpass and lowpass filtering).
    Returns:
        peli_contrast_map: Peli's Local Band-Limited Contrast map.
    """
    # Ensure the image is in float format for computations
    image = image.astype(np.float32) / 255.0

    # Bandpass filter: original image minus lowpass filtered version
    bandpass = image - gaussian_filter(image, sigma=sigma)

    # Lowpass filter: Gaussian smoothed image
    lowpass = gaussian_filter(image, sigma=sigma * 2)

    # Compute Peli's contrast: bandpass / lowpass
    peli_contrast_map = np.divide(bandpass, lowpass + 1e-6)  # Avoid division by zero

    return peli_contrast_map

def normalize_image(image):
    """
    Normalize the image to range [0, 1] for visualization.
    Args:
        image: Input image to normalize.
    Returns:
        Normalized image.
    """
    return (image - np.min(image)) / (np.max(image) - np.min(image) + 1e-6)

def visualize_peli_contrast(image_path, sigma=1.5):
    """
    Visualize Peli's Local Band-Limited Contrast for a given image.
    Args:
        image_path: Path to the input image (grayscale or RGB).
        sigma: Standard deviation for Gaussian filter.
    """
    # Load image and convert to grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Image could not be loaded. Please check the path.")
    
    # Compute Peli's contrast
    peli_contrast_map = peli_contrast(image, sigma=sigma)

    # Normalize for visualization
    peli_contrast_map_normalized = normalize_image(peli_contrast_map)

    # Visualization
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.title("Original Image")
    plt.imshow(image, cmap='gray')
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.title("Peli's Contrast Map")
    plt.imshow(peli_contrast_map_normalized, cmap='gray')
    plt.axis('off')

    plt.tight_layout()
    plt.show()

# Example Usage
image_path = "lena.png"  # Replace with your image path
visualize_peli_contrast(image_path, sigma=1.5)
