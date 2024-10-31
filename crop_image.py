import cv2
import os
import numpy as np
import tkinter as tk
from tkinter import filedialog
import spectral

# Initialize global variables for cropping
start_point = None
end_point = None
cropping = False
cropped_img = None
cropped_cube = None

def select_image():
    """Opens a file dialog for the user to select an image."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    image_path = filedialog.askopenfilename(title="Select an Image")
    return image_path

def crop_event(event, x, y, flags, param):
    """Handles the mouse events for selecting the cropping region."""
    global start_point, end_point, cropping, cropped_img, cropped_cube

    if event == cv2.EVENT_LBUTTONDOWN:
        start_point = (x, y)
        cropping = True
    elif event == cv2.EVENT_MOUSEMOVE:
        if cropping:
            end_point = (x, y)
            img_copy = img.copy()
            cv2.rectangle(img_copy, start_point, end_point, (0, 255, 0), 2)
            cv2.imshow("Image", img_copy)
    elif event == cv2.EVENT_LBUTTONUP:
        end_point = (x, y)
        cropping = False

        # Check if crop dimensions are valid
        x_min, y_min = min(start_point[0], end_point[0]), min(start_point[1], end_point[1])
        x_max, y_max = max(start_point[0], end_point[0]), max(start_point[1], end_point[1])

        if x_max > x_min and y_max > y_min:
            cropped_img = img[y_min:y_max, x_min:x_max]
            cropped_cube = cube[y_min:y_max, x_min:x_max, :]
            cv2.imshow("Cropped Image", cropped_img)
        else:
            print("Invalid crop area. Please try again.")
            cropped_img, cropped_cube = None, None

def save_cropped_cube(crop_folder, count, hdr_metadata):
    """Saves the cropped spectral cube in the specified folder with wavelength metadata."""
    global cropped_cube
    import pdb; pdb.set_trace()
    if cropped_cube is not None:
        # Check if the cropped area is non-zero
        if cropped_cube.size == 0:
            print("Warning: Cropped area is empty. Skipping save.")
            return

        # Handle NaN values by replacing them with zero
        if np.isnan(cropped_cube).any():
            print("Warning: NaN values found in cropped cube. Replacing with zero.")
            cropped_cube = np.nan_to_num(cropped_cube, nan=0.0)

        # Prepare metadata and save path
        save_path = os.path.join(crop_folder, f"cropped_cube_{count}.hdr")
        metadata = hdr_metadata.copy()
        metadata['wavelength'] = hdr_metadata['wavelength']

        # Save the cropped cube with updated metadata
        spectral.envi.save_image(save_path, cropped_cube, dtype=np.float32, metadata=metadata)
        print(f"Cropped spectral cube saved as: {save_path}")

def main():
    count = 1
    while True:
        image_path = select_image()
        if not image_path:
            print("No image selected. Exiting.")
            break

        global img, cube

        # Load the image
        img = cv2.imread(image_path)
        if img is None:
            print("Error loading image. Try again.")
            continue

        # Find the HDR file in the 'capture' subfolder
        base_folder = os.path.dirname(image_path)
        hdr_folder = os.path.join(base_folder, "capture")
        hdr_file = [f for f in os.listdir(hdr_folder) if f.endswith('.hdr')]
        if not hdr_file:
            print(f"No HDR file found in '{hdr_folder}'.")
            continue

        hdr_path = os.path.join(hdr_folder, hdr_file[0])
        print(f"Loading HDR file: {hdr_path}")
        hdr_info = spectral.envi.open(hdr_path)
        cube = hdr_info.load()

        hdr_metadata = hdr_info.metadata

        # Create 'crop' folder if it doesn't exist
        crop_folder = os.path.join(base_folder, "crop")
        os.makedirs(crop_folder, exist_ok=True)

        cv2.namedWindow("Image")
        cv2.setMouseCallback("Image", crop_event)

        print("Press 's' to save the cropped cube, 'c' to crop a new region, or 'q' to quit.")
        while True:
            cv2.imshow("Image", img)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("s"):
                save_cropped_cube(crop_folder, count, hdr_metadata)
                count += 1
            elif key == ord("c"):
                cv2.destroyWindow("Cropped Image")
                break
            elif key == ord("q"):
                cv2.destroyAllWindows()
                return

if __name__ == "__main__":
    main()
