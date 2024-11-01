import spectral
import numpy as np
import cv2

def load_hyperspectral_image(file_path):
    hdr_image = spectral.open_image(file_path)
    cube = hdr_image.load()
    return cube  # The cube shape is (height, width, bands)

# Example usage
cube = load_hyperspectral_image('path/to/image.hdr')

def max_min_luminance_ratio(band):
    L_max = np.max(band)
    L_min = np.min(band)
    return L_max / L_min if L_min > 0 else 0

def weber_contrast(band):
    L_max = np.max(band)
    L_min = np.min(band)
    return (L_max - L_min) / L_min if L_min > 0 else 0

def michelson_contrast(band):
    L_max = np.max(band)
    L_min = np.min(band)
    return (L_max - L_min) / (L_max + L_min) if (L_max + L_min) > 0 else 0

def rms_contrast(band):
    mean_luminance = np.mean(band)
    return np.sqrt(np.mean((band - mean_luminance) ** 2))


def peli_contrast(band, sigma1=1.0, sigma2=2.0):
    lowpass = cv2.GaussianBlur(band, (0, 0), sigma2)
    bandpass = cv2.GaussianBlur(band, (0, 0), sigma1) - lowpass
    contrast_map = np.divide(bandpass, lowpass + 1e-5)  # Avoid division by zero
    return np.mean(np.abs(contrast_map))  # Average local contrast

def difference_of_gaussians(band, sigma1=1.0, sigma2=2.0):
    g1 = cv2.GaussianBlur(band, (0, 0), sigma1)
    g2 = cv2.GaussianBlur(band, (0, 0), sigma2)
    return g1 - g2

def local_mean_difference(band, kernel_size=3):
    local_mean = cv2.blur(band, (kernel_size, kernel_size))
    contrast_map = np.abs(band - local_mean)
    return np.mean(contrast_map)  # Average local contrast

def just_noticeable_difference(band):
    mean_luminance = np.mean(band)
    return 0.02 + 0.1 * np.sqrt(mean_luminance)

def contrast_sensitivity_function(frequency, a=75, b=0.2, c=0.8):
    return a * (frequency ** c) * np.exp(-b * frequency)
