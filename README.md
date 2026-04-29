# BoneVision DX-Ray

**Dual-Energy X-Ray Material Decomposition & Visualization Tool**

A Python desktop application (PyQt5) that simulates dual-energy X-ray acquisition and performs material decomposition to visualize separate **bone** and **soft-tissue** maps.

## Features

- **Phantom Generation** — Synthetic 512×512 ribcage, cylinder, and layered phantoms
- **Dual-Energy Acquisition** — Configurable low/high energy projections with noise & scatter
- **Material Decomposition** — Matrix-inversion method to isolate bone vs. soft tissue
- **Live Metrics** — MAE, CNR, and SNR computed against ground truth
- **Interactive Attenuation Chart** — Real-time Matplotlib curves tracking μ values

## Requirements

- Python 3.11+
- macOS (tested) / Linux / Windows

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

## Project Structure

```
├── main.py                  # Application entry point
├── controllers/
│   └── main_controller.py   # State management & signal binding
├── core/
│   ├── phantom.py           # Geometric phantom generation
│   ├── physics.py           # Attenuation model & decomposition
│   └── metrics.py           # Quality metric calculations
├── ui/
│   ├── main_window.py       # Root window layout
│   ├── styles.py            # Design tokens & colormap config
│   ├── colormap.py          # NumPy vectorized colormapping
│   └── components/          # Reusable widgets
│       ├── image_card.py
│       ├── knob.py
│       ├── charts.py
│       ├── selectors.py
│       └── layout.py
├── utils/
│   └── cleanup.py           # Teardown & cache cleanup
├── docs/
│   ├── CLAUDE.md            # Architecture reference
│   └── TASK.md              # Development execution plan
└── requirements.txt
```

## Architecture

MVC pattern with strict separation:
- **Model** (`core/`) — Pure NumPy/SciPy physics, no UI awareness
- **View** (`ui/`) — PyQt5 widget assembly
- **Controller** (`controllers/`) — Binds signals to core actions