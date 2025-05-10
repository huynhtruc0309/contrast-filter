# 📷 Glass Filter Simulation for Contrast Enhancement

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/status-complete-brightgreen)

![Project Thumbnail](Figs/thumbnail.png)

This project simulates the impact of optical glass filters on scene contrast using hyperspectral imaging data. By applying spectral transmission profiles of real-world filters to hyperspectral images, we evaluate their effects on both global and local contrast under diverse lighting conditions. The goal is to understand how filters influence visual performance for applications in imaging systems, automotive visibility, and visual comfort.

## 🧪 Project Overview

- Simulates filter effects on hyperspectral datasets (SIDQ and Scott scenes)
- Applies transmission curves for **Amplifier Pro** and **Neutral Density** filters
- Evaluates contrast using multiple metrics:
  - **Global:** Weber, Michelson, RMS, SIPk
  - **Local:** Peli, DoG, Ahumada & Beard, Iordache
- Converts filtered hyperspectral data to RGB for visualization

## 🛠️ Features

- Hyperspectral filter simulation (`apply_filter.py`, `apply_filter_sidq.py`)
- Global contrast evaluation (`cab_clb_contrast.py`)
- Local contrast metrics and visualization (`local_metrics.py`, `dogcontrast.py`, `pelicontrast.py`, `local_vis.py`)
- RGB conversion pipeline (`hsi2rgb.py`, `spectral2rgb.py`)
- MATLAB scripts for ENVI image preprocessing (`ScottcolorIMGcalc_ENVI.m`, `colorIMGcalc_ENVI.m`)
- Utilities and visualization tools in `tools/`, `filters/`, and `Figs/`

## 📁 Repository Structure

```
├── filters/                 # Spectral transmission profiles
├── tools/                  # Supporting tools and utilities
├── Figs/                   # Output plots and figures
├── cmfs/                   # Color matching functions
├── apply_filter.py         # Apply filters to hyperspectral scenes
├── cab_clb_contrast.py     # Global contrast metrics calculation
├── local_metrics.py        # Local contrast metrics
├── local_vis.py            # Contrast map visualization
├── spectral2rgb.py         # Convert HSI to RGB
├── contrast_metrics_*.csv  # Output results
├── *.m                     # MATLAB preprocessing scripts
```

## 📊 Sample Results

Contrast metrics are exported to:

- `contrast_metrics_global.csv` — Weber, Michelson, RMS, SIPk
- `contrast_metrics_local.csv` — Peli, DoG, Ahumada, Iordache

Visual comparisons and maps are saved in the `Figs/` folder.

## 🖥️ Requirements

- Python 3.8+
- Required packages: `numpy`, `scipy`, `matplotlib`, `opencv-python`, `scikit-image`

Install dependencies:
```bash
pip install -r requirements.txt
```

## 🚀 Getting Started

1. **Preprocess** raw hyperspectral data (optional):
   - Use MATLAB scripts in ENVI-compatible format.
2. **Apply filters** to hyperspectral cubes:
   ```bash
   python apply_filter.py
   ```
3. **Evaluate contrast metrics**:
   ```bash
   python cab_clb_contrast.py
   python local_metrics.py
   ```

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 👩‍💻 Author

**Truc Luong Phuong Huynh**  
COSI Master Program – Norwegian University of Science and Technology (NTNU)
