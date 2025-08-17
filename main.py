import sys
import numpy as np
from PIL import Image
from tkinter import *
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
    win = Tk(className='Drawing image')
    canvas = Canvas(win)
    
    win_size = str(full_width) + "x" + str(full_height)
    win.geometry(win_size)
    win.update_idletasks()
    win.update()
    
    canvas.configure(width=cols, height=rows)
    canvas.pack(anchor=NW)
    
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
    if len(sys.argv) != 4:
        print("Usage: python main.py <image_file> <pen_width> <test_mode_0_or_real_mode_1>")
        sys.exit(1)
    
    file = sys.argv[1]
    step = int(sys.argv[2])
    real_write = int(sys.argv[3]) > 0
    
    print(str(real_write))
    
    # Validate image
    if not validate_image(file):
        sys.exit(1)
    
    # Process image
    img_array, cols, rows, full_width, full_height = process_image(file, step)
    
    # Setup GUI
    win, canvas = setup_gui(full_width, full_height, cols, rows)
    
    # Initialize plotter
    plotter = PlotterController(real_write)
    
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
    
    input()

if __name__ == "__main__":
    main()