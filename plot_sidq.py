import matplotlib.pyplot as plt
import os
from matplotlib.image import imread

# Plotting 9 images in a 3x3 grid
folder_path = '../Scott/All'
image_files = sorted([f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg')) and not f.startswith('.')], key=lambda x: int(os.path.splitext(x)[0]))

plt.figure(figsize=(8, 8))
for i, image_file in enumerate(image_files[:9]):
    img = imread(os.path.join(folder_path, image_file))
    plt.subplot(3, 3, i + 1)
    plt.imshow(img)
    plt.axis('off')

plt.tight_layout()
plt.show()