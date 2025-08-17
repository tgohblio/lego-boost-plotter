import sys
import argparse
import numpy as np
import tkinter as tk
from PIL import Image
from tkinter import Canvas
from draw import PlotterController

def validate_image(file_path):
    """Validate if file is a valid image using PIL"""
    try:
        with Image.open(file_path) as test_img:
            test_img.verify()
        return True
    except (IOError, SyntaxError):
        print('Input file is not an image.')
        return False

def process_image(file_path, step, max_width=486):
    """Process image for plotting: convert to grayscale, threshold, resize, and flip"""
    # Load and convert to grayscale
    img = Image.open(file_path).convert('L')
    cols, rows = img.size
    
    # Rotate if landscape to portrait
    if cols > rows:
        img = img.transpose(Image.Transpose.ROTATE_90)
        cols, rows = img.size
    
    # Apply binary threshold
    img = img.point(lambda x: 255 if x > 127 else 0, mode='1')
    
    # Resize to max size
    ratio = max_width / cols
    full_width = max_width
    full_height = int(rows * ratio)
    full_dim = (full_width, full_height)
    img = img.resize(full_dim, Image.Resampling.NEAREST)
    
    # Resize due to pen size and back
    width = int(full_width / step)
    height = int(full_height / step)
    dim = (width, height)
    img = img.resize(dim, Image.Resampling.NEAREST)
    img = img.resize(full_dim, Image.Resampling.NEAREST)
    cols, rows = img.size
    
    # Flip horizontally
    img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    
    # Convert to numpy array for pixel access
    img_array = np.array(img)
    
    return img_array, cols, rows, full_width, full_height

def detect_black(img_array, x, y):
    """Detect if pixel at (x,y) is black"""
    return img_array[y, x] < 128

def check_line(img_array, y, cols, step):
    """Check if line y has any black pixels"""
    x = 1
    while x < cols:
        if detect_black(img_array, x, y):
            return True
        x = x + step
    return False

def setup_gui(full_width, full_height, cols, rows):
    """Setup tkinter GUI for visual feedback"""
    win = tk.Tk(className='Drawing image')
    canvas = Canvas(win)

    win_size = str(full_width) + "x" + str(full_height)
    win.geometry(win_size)
    win.update_idletasks()
    win.update()
    
    canvas.configure(width=cols, height=rows)
    canvas.pack(anchor=tk.NW)
    
    return win, canvas

def parse_line(img_array, y, direction, cols, step, plotter, canvas, win):
    """Parse a single line of the image for plotting"""
    x = 1
    start_x = end_x = 0
    
    while x < cols:
        if direction > 0:
            detect_x = x
        else:
            detect_x = cols - x
            
        if detect_black(img_array, detect_x, y):
            if not plotter.is_writing():
                print("moving to", str(detect_x), "and starting to write")
                plotter.move_pen(detect_x)
                start_x = detect_x
                plotter.pen_down()
        else:
            if plotter.is_writing():
                print("moving to", str(detect_x), "and stopping writing")
                end_x = detect_x
                if end_x != start_x:
                    canvas.create_line(start_x, y, end_x, y, width=step)
                    canvas.pack()
                    win.update()
                    win.update_idletasks()
                
                plotter.move_pen(detect_x)
                plotter.pen_up()
        
        x = x + step
    
    if plotter.is_writing():
        end_x = detect_x
        canvas.create_line(start_x, y, end_x, y, width=step)
        canvas.pack()
        win.update()
        win.update_idletasks()
        
        plotter.move_pen(detect_x)
        plotter.pen_up()

def main():
    parser = argparse.ArgumentParser(
        description='LEGO BOOST plotter - converts images to line drawings',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py image.png 2 --test     # Test mode (GUI preview only)
  python main.py image.png 3 --real     # Real mode (connect to LEGO hub)
  python main.py photo.jpg 1 --real --hub "My Hub"  # Custom hub name
        '''
    )
    
    parser.add_argument('image_file', 
                       help='Path to the image file to plot')
    parser.add_argument('pen_width', type=int,
                       help='Pen width/step size (1-5 recommended)')
    
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--test', action='store_true',
                           help='Test mode: show GUI preview without connecting to LEGO hub')
    mode_group.add_argument('--real', action='store_true', 
                           help='Real mode: connect to LEGO hub and plot')
    
    parser.add_argument('--hub', default='Boost Hub',
                       help='LEGO hub name (default: "Boost Hub")')
    parser.add_argument('--max-width', type=int, default=486,
                       help='Maximum image width in pixels (default: 486)')
    
    args = parser.parse_args()
    
    file = args.image_file
    step = args.pen_width
    real_write = args.real
    hub_name = args.hub
    max_width = args.max_width
    
    print(f"Mode: {'Real plotting' if real_write else 'Test mode'}")
    if real_write:
        print(f"Hub: {hub_name}")
    
    # Validate image
    if not validate_image(file):
        sys.exit(1)
    
    # Process image
    img_array, cols, rows, full_width, full_height = process_image(file, step, max_width)
    
    # Setup GUI
    win, canvas = setup_gui(full_width, full_height, cols, rows)
    
    # Initialize plotter
    plotter = PlotterController(real_write, hub_name)
    
    if real_write:
        plotter.connect()
        plotter.load_paper()
    
    # Start plotting
    y = 1
    direction = 1
    
    while y < rows:
        # Skip empty lines
        y_step = step
        while y + y_step < rows:
            if check_line(img_array, y + y_step, cols, step):
                y = y + y_step
                if plotter.is_writing():
                    plotter.pen_up()
                
                print("moving to line n.", str(y))
                
                if real_write:
                    plotter.move_to_next_line(y_step, step)
                
                parse_line(img_array, y, direction, cols, step, plotter, canvas, win)
                direction = direction * -1
                break
            else:
                y_step = y_step + step
        
        if y + y_step >= rows:
            break
    
    if plotter.is_writing():
        plotter.pen_up()
    
    if real_write:
        plotter.eject_paper()
        plotter.disconnect()
    
    print("Press ENTER to quit")
    input()

if __name__ == "__main__":
    main()