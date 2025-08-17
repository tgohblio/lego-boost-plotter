from time import sleep
from pylgbst import *
from pylgbst.hub import MoveHub
from pylgbst import get_connection_bleak
from pylgbst.peripherals import EncodedMotor, COLORS, VisionSensor

class PlotterController:
    """Controls LEGO BOOST plotter motors and sensors"""
    
    def __init__(self, real_write=True, hub_name='Auto Mňau'):
        self.real_write = real_write
        self.hub_name = hub_name
        self.hub = None
        self.writing = False
        self.real_x = 1
        
    def connect(self):
        """Connect to LEGO BOOST hub"""
        if self.real_write:
            conn = get_connection_bleak(hub_name=self.hub_name)
            self.hub = MoveHub(conn)
            # Turn off the LED
            self.hub.led.color = (0, 0, 0)
    
    def disconnect(self):
        """Disconnect from LEGO BOOST hub"""
        if self.real_write and self.hub:
            self.hub.disconnect()
    
    def move_motor(self, which, angle, clockwise=1, speed=0.1, wait=True):
        """Move motor by angle"""
        if self.real_write and self.hub:
            if which == 'A':
                self.hub.motor_A.angled(angle * clockwise, speed, speed, wait)
            elif which == 'B':
                self.hub.motor_B.angled(angle * clockwise, speed, speed, wait)
            elif which == 'C':
                self.hub.port_C.angled(angle * clockwise, speed, speed, wait)
    
    def pen_up(self):
        """Lift the pen"""
        if self.real_write:
            self.move_motor('A', 25, 1, 0.1)
        self.writing = False
    
    def pen_down(self):
        """Lower the pen to draw"""
        if self.real_write:
            self.move_motor('A', 25, -1, 0.1)
        self.writing = True
    
    def is_writing(self):
        """Check if pen is currently down"""
        return self.writing
    
    def move_pen(self, x_to):
        """Move pen horizontally to position x_to"""
        if x_to > self.real_x:
            direction = 1
        else:
            direction = -1
        
        if self.real_write:
            self.move_motor('C', abs(self.real_x - x_to), direction)
        
        self.real_x = x_to
    
    def load_paper(self):
        """Load paper using vision sensor feedback"""
        threshold = 1
        paper_present = 0
        while paper_present < threshold:
            self.move_motor('B', 100, -1)
            if self.hub and self.hub.vision_sensor.color == 10:
                paper_present = paper_present + 1
                self.move_motor('B', 100, 1)
    
    def eject_paper(self):
        """Eject paper using vision sensor feedback"""
        threshold = 1
        paper_out = 0
        while paper_out < threshold:
            self.move_motor('B', 1000, -1)
            if self.hub and self.hub.vision_sensor.color != 10:
                paper_out = paper_out + 1
    
    def move_to_next_line(self, y_step, step):
        """Move paper to next line (paper feed mechanism)"""
        if self.real_write:
            self.move_motor('B', y_step + step * 2.5, -1)
            self.move_motor('B', step * 2, 1)