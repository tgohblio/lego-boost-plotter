# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python script that controls a LEGO plotter built from the LEGO BOOST Creative Toolbox set 17101. The plotter converts images to line drawings by controlling LEGO motors via Bluetooth. It replaces a problematic JavaScript implementation with a more reliable Python solution.

## Key Dependencies

- `pylgbst`: Controls LEGO BOOST hub via Bluetooth
- `bleak`: Bluetooth Low Energy communication
- `pillow`: Image processing and thresholding
- `numpy`: Array operations for image data
- `tkinter`: GUI for visual feedback during plotting

## Common Commands

### Setup and Dependencies
```bash
# Install dependencies (using uv package manager)
uv sync

# Run with uv
uv run python main.py image.png 2 --test
```

### Running the Plotter
```bash
# Test mode (GUI preview only, no hardware connection)
python main.py image.png 2 --test

# Real mode (connects to LEGO hub and draws)
python main.py image.png 2 --real

# Custom hub name and settings
python main.py photo.jpg 3 --real --hub "My Hub" --max-width 600

# Get help with all available options
python main.py --help
```

## Architecture

### Core Components

- **main.py**: Main entry point with image processing, GUI, and coordination logic
- **draw.py**: PlotterController class for LEGO motor control and sensor feedback

### Image Processing Pipeline

1. Load and validate image
2. Convert to grayscale and apply binary threshold
3. Rotate landscape images to portrait
4. Resize to maximum width (486px) maintaining aspect ratio
5. Quantize based on pen width parameter
6. Flip horizontally for plotter coordinate system

### Motor Control System

- **Motor A**: Pen up/down movement
- **Motor B**: Paper feed mechanism with vision sensor for detection
- **Port C**: Horizontal pen movement across paper

### Key Functions

**main.py:**
- `process_image()`: Handles image loading, thresholding, resizing, and conversion
- `parse_line()`: Processes each image row, detecting black pixels and coordinating with plotter
- `setup_gui()`: Creates tkinter window for visual feedback
- `validate_image()`: Uses PIL to verify image file validity

**draw.py (PlotterController class):**
- `pen_up()`/`pen_down()`: Pen control via Motor A
- `move_pen()`: Horizontal pen movement via Port C
- `load_paper()`/`eject_paper()`: Paper handling using vision sensor
- `move_motor()`: Generic motor movement wrapper
- `connect()`/`disconnect()`: LEGO hub connection management

## Known Issues

- No error handling for Bluetooth connection failures
- Vision sensor color detection hardcoded to value 10
- No validation for pen width range (should be 1-5)

## Hardware Setup

The plotter requires:
- LEGO BOOST Creative Toolbox set 17101
- Vision sensor for paper detection
- Motors connected to ports A (pen), B (paper feed), C (horizontal movement)
- Bluetooth connection to the hub named "Boost Hub"