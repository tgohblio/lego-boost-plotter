# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python script that controls a LEGO plotter built from the LEGO BOOST Creative Toolbox set 17101. The plotter converts images to line drawings by controlling LEGO motors via Bluetooth. It replaces a problematic JavaScript implementation with a more reliable Python solution.

## Key Dependencies

- `pylgbst`: Controls LEGO BOOST hub via Bluetooth
- `bleak`: Bluetooth Low Energy communication
- `cv2` (OpenCV): Image processing and thresholding
- `tkinter`: GUI for visual feedback during plotting

## Common Commands

### Setup and Dependencies
```bash
# Install dependencies (using uv package manager)
uv sync

# Run with uv
uv run python draw.py image.png 2 1
```

### Running the Plotter
```bash
# Basic usage: filename, pen strength, test/real mode (0/1)
python draw.py image.png 2 1

# Test mode (no actual writing, just GUI preview)
python draw.py image.png 2 0

# Real mode (connects to LEGO hub and draws)
python draw.py image.png 2 1
```

## Architecture

### Core Components

- **draw.py**: Main plotting script with image processing and motor control
- **main.py**: Simple entry point (currently just prints hello message)

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

- `parseLine()`: Processes each image row, detecting black pixels and controlling pen movement
- `loadPaper()`/`ejectPaper()`: Paper handling using vision sensor
- `penUp()`/`penDown()`: Pen control via Motor A
- `moveMotor()`: Generic motor movement wrapper

## Known Issues

- Missing `filetype` import in draw.py:29 - this will cause runtime error
- Hub name hardcoded as "Auto Mňau" in draw.py:194
- No error handling for Bluetooth connection failures
- No validation of command line arguments

## Hardware Setup

The plotter requires:
- LEGO BOOST Creative Toolbox set 17101
- Vision sensor for paper detection
- Motors connected to ports A (pen), B (paper feed), C (horizontal movement)
- Bluetooth connection to the hub named "Auto Mňau"