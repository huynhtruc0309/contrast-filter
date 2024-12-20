import numpy as np
import cv2
from scipy.ndimage import gaussian_filter

def ahumada_beard_contrast(image, sigma_b=3, sigma_i=1):
    """
    Compute the contrast measure proposed by Ahumada and Beard.
    Args:
        image: Grayscale input image.
        sigma_b: Standard deviation for the blurring Gaussian filter.
        sigma_i: Standard deviation for the local luminance Gaussian filter.
    Returns:
        contrast_map: Contrast map based on Ahumada and Beard's measure.
    """
    # Blurred image b(x, y)
    b = gaussian_filter(image, sigma=sigma_b)
    
    # Local luminance image m(x, y)
    m = gaussian_filter(b, sigma=sigma_i)
    
    # Ahumada and Beard's contrast
    contrast_map = (b / (m + 1e-6)) - 1  # Avoid division by zero
    
    return contrast_map

def iordache_contrast(image):
    """
    Compute the contrast measure proposed by Iordache et al.
    Args:
        image: Grayscale input image.
    Returns:
        contrast_map: Contrast map based on Iordache's measure.
    """
    # Kernel for 8-neighbor averaging
    kernel = np.ones((3, 3)) / 8.0
    kernel[1, 1] = 0  # Exclude the center pixel
    
    # Compute bs(x, y) (average luminance of 8 neighbors)
    bs = cv2.filter2D(image, -1, kernel)
    
    # Iordache's contrast
    contrast_map = image / (bs + 1e-6)  # Avoid division by zero
    
    return contrast_map

def normalize_image(image):
    """
    Normalize the image to range [0, 1] for visualization.
    Args:
        image: Input image to normalize.
    Returns:
        Normalized image.
    """
    return (image - np.min(image)) / (np.max(image) - np.min(image) + 1e-6)

def visualize_contrast_measures(image_path):
    """
    Visualize contrast measures for a given image using Ahumada & Beard and Iordache methods.
    Args:
        image_path: Path to the input image (grayscale or RGB).
    """
    # Load image and convert to grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Image could not be loaded. Please check the path.")
    image = image.astype(np.float32) / 255.0  # Normalize to [0, 1]

    # Compute contrast maps
    cab_contrast = ahumada_beard_contrast(image)
    cbl_contrast = iordache_contrast(image)

    # Normalize for visualization
    cab_contrast_normalized = normalize_image(cab_contrast)
    cbl_contrast_normalized = normalize_image(cbl_contrast)

    # Visualization
    import matplotlib.pyplot as plt

    plt.figure(figsize=(15, 5))
    plt.subplot(1, 3, 1)
    plt.title("Original Image")
    plt.imshow(image, cmap='gray')
    plt.axis('off')

    plt.subplot(1, 3, 2)
    plt.title("Ahumada & Beard Contrast (CAB)")
    plt.imshow(cab_contrast_normalized, cmap='gray')
    plt.axis('off')

    plt.subplot(1, 3, 3)
    plt.title("Iordache Contrast (CBL)")
    plt.imshow(cbl_contrast_normalized, cmap='gray')
    plt.axis('off')

    plt.tight_layout()
    plt.show()

# Example Usage
image_path = "lena.png"  # Replace with your image path
visualize_contrast_measures(image_path)
