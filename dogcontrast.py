import numpy as np
import cv2
import matplotlib.pyplot as plt

def center_surround_response(image, rc, rs):
    """
    Compute the center and surround responses based on 2D Gaussian weights.
    Args:
        image: Grayscale input image.
        rc: Radius for center Gaussian.
        rs: Radius for surround Gaussian.
    Returns:
        Rc: Center response.
        Rs: Surround response.
    """
    # Create Gaussian kernels
    kernel_size_c = int(6 * rc + 1)  # Kernel size for center
    kernel_size_s = int(6 * rs + 1)  # Kernel size for surround
    
    center_gaussian = cv2.getGaussianKernel(kernel_size_c, rc)
    surround_gaussian = cv2.getGaussianKernel(kernel_size_s, rs)
    
    center_kernel = np.outer(center_gaussian, center_gaussian)
    surround_kernel = np.outer(surround_gaussian, surround_gaussian)
    
    # Normalize the surround kernel to have the same total weight as the center
    surround_kernel *= (0.85 * (rc / rs) ** 2)
    
    # Compute center and surround responses
    Rc = cv2.filter2D(image, -1, center_kernel)
    Rs = cv2.filter2D(image, -1, surround_kernel)
    
    return Rc, Rs

def dog_contrast_metrics(image, rc=2, rs=5):
    """
    Compute DoG-based contrast metrics.
    Args:
        image: Grayscale input image.
        rc: Radius for center Gaussian.
        rs: Radius for surround Gaussian.
    Returns:
        contrast_center_only: Center-only scheme contrast.
        contrast_surround_only: Surround-only scheme contrast.
        contrast_center_plus_surround: Center-plus-surround scheme contrast.
    """
    # Compute center and surround responses
    Rc, Rs = center_surround_response(image, rc, rs)
    
    # Compute contrast metrics
    contrast_center_only = (Rc - Rs) / (Rc + 1e-6)  # Center-only contrast
    contrast_surround_only = (Rc - Rs) / (Rs + 1e-6)  # Surround-only contrast
    contrast_center_plus_surround = (Rc - Rs) / (Rc + Rs + 1e-6)  # Center-plus-surround contrast
    
    return contrast_center_only, contrast_surround_only, contrast_center_plus_surround

def normalize_image(image):
    """
    Normalize the image to range [0, 1] for visualization.
    Args:
        image: Input image to normalize.
    Returns:
        Normalized image.
    """
    return (image - np.min(image)) / (np.max(image) - np.min(image) + 1e-6)

def visualize_dog_contrast(image_path, rc=2, rs=5):
    """
    Visualize DoG-based contrast metrics for a given image.
    Args:
        image_path: Path to the input image (grayscale or RGB).
        rc: Radius for center Gaussian.
        rs: Radius for surround Gaussian.
    """
    # Load image and convert to grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Image could not be loaded. Please check the path.")
    image = image.astype(np.float32) / 255.0  # Normalize input image to [0, 1]

    # Compute DoG contrast metrics
    contrast_center_only, contrast_surround_only, contrast_center_plus_surround = dog_contrast_metrics(image, rc, rs)

    # Normalize contrast maps for visualization
    contrast_center_only = normalize_image(contrast_center_only)
    contrast_surround_only = normalize_image(contrast_surround_only)
    contrast_center_plus_surround = normalize_image(contrast_center_plus_surround)

    # Visualization
    plt.figure(figsize=(15, 5))
    plt.subplot(1, 4, 1)
    plt.title("Original Image")
    plt.imshow(image, cmap='gray')
    plt.axis('off')

    plt.subplot(1, 4, 2)
    plt.title("Center-Only Contrast")
    plt.imshow(contrast_center_only, cmap='gray')
    plt.axis('off')

    plt.subplot(1, 4, 3)
    plt.title("Surround-Only Contrast")
    plt.imshow(contrast_surround_only, cmap='gray')
    plt.axis('off')

    plt.subplot(1, 4, 4)
    plt.title("Center-Plus-Surround Contrast")
    plt.imshow(contrast_center_plus_surround, cmap='gray')
    plt.axis('off')

    plt.tight_layout()
    plt.show()

# Example Usage
image_path = "lena.png"  # Replace with your image path
visualize_dog_contrast(image_path, rc=2, rs=5)
