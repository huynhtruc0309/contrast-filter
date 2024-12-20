import numpy as np
import matplotlib.pyplot as plt

# Load data from amp.txt and neural.txt
amp_data = np.loadtxt('tools/filters/amp.txt')
neural_data = np.loadtxt('tools/filters/neural.txt')

# Extract wavelength and transmission values
wavelength_amp, transmission_amp = amp_data[:, 0], amp_data[:, 1]*100
wavelength_neural, transmission_neural = neural_data[:, 0], neural_data[:, 1]*100

# Plotting
plt.figure(figsize=(10, 6))

# Plot AMPLIFIER PRO Filter data
plt.plot(wavelength_amp, transmission_amp, label='Amplifier Pro Filter', linestyle='-', linewidth=2)

# Plot Neural Filter data
plt.plot(wavelength_neural, transmission_neural, label='Neural Filter', linestyle='--', linewidth=2)

# Annotation for key points in AMPLIFIER PRO Filter
max_transmission_idx = np.argmax(transmission_amp)

# Customize plot
plt.xlabel('Wavelength (nm)', fontsize=12)
plt.ylabel('Transmission (%)', fontsize=12)
plt.title('Transmission through Amplifier Pro and Neural Filters', fontsize=14)
plt.legend()
plt.grid(True)
plt.tight_layout()

# Show plot
plt.show()
