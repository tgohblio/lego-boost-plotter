import sys, getopt, random, time, cv2, filetype, pylgbst
from time import sleep
from pylgbst import *
from pylgbst.hub import MoveHub
from pylgbst import get_connection_bleak
from pylgbst.peripherals import EncodedMotor, COLORS, VisionSensor
from tkinter import *

#input file as first argument
file = sys.argv[1]

#pen width as second parameter
step = int(sys.argv[2])

#shall I really write or just draw to the screen?
realWriteInt = int(sys.argv[3])
if realWriteInt > 0:
	realWrite = True
else:
	realWrite = False
print (str(realWrite))

maxWidth = 486

win = Tk(className='Drawing image')
canvas = Canvas(win) 

#check if it is valid image
if not filetype.is_image(file):
	print('Input file is not an image.')
	exit()

#Get image dimensions
img = cv2.imread(file, 0)
rows, cols, *_ = img.shape

#Rotate if landscape to portrait
if cols > rows:	
	img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
	rows,cols, *_ = img.shape
 
#Apply thresold
_ ,img = cv2.threshold(img,127,255,cv2.THRESH_BINARY)

#Resize to max size (500)
ratio = maxWidth/cols
fullWidth = maxWidth
fullHeight = int(rows * ratio)
fullDim = (fullWidth, fullHeight) 
img = cv2.resize(img, fullDim, interpolation = cv2.INTER_NEAREST)

#resize due to pen size and back
width = int (fullWidth / step)
height = int (fullHeight / step) 
dim = (width, height) 
img = cv2.resize(img, dim, interpolation = cv2.INTER_NEAREST)
img = cv2.resize(img, fullDim, interpolation = cv2.INTER_NEAREST)
rows, cols, *_ = img.shape

#and flip vertically
img = cv2.flip(img, 1)

#cv2.imshow("preview", img) 
#cv2.waitKey(0) 

winSize = str(fullWidth) + "x" + str(fullHeight)

win.geometry(winSize)
win.update_idletasks()
win.update()

canvas.configure(width=cols, height=rows)
canvas.pack(anchor=NW)

#Lift the pen
def penUp():
	global writing
#	hub.led.color = (0, 255, 0)
	if realWrite:
		moveMotor ('A', 25, 1, .1)
	writing = False

#Draw
def penDown():
	global writing
#	hub.led.color = (255, 0, 0)
	if realWrite:
		moveMotor ('A', 25, -1, .1)
	writing = True
	
#Load paper
def loadPaper():
	thresold = 1
	paperPresent = 0
	while paperPresent<thresold:	
#		hub.led.color = (255, 0, 0)
		moveMotor ('B', 100, -1)
		if hub.vision_sensor.color == 10:
			paperPresent = paperPresent + 1
			moveMotor ('B', 100, 1)
#			hub.led.color = (0, 255, 0)	

#Eject paper
def ejectPaper():
	thresold = 1
	paperOut = 0
	while paperOut<thresold:	
#		hub.led.color = (255, 0, 255)
		moveMotor ('B', 1000, -1)
		if hub.vision_sensor.color != 10:
			paperOut = paperOut + 1
#			hub.led.color = (0, 255, 0)	

#detect black pixel
def detectBlack(x,y):
	if img[y,x] < 128:
		return True
	else:
		return False

#just to be clear...
def movePen (xFrom, xTo):
	global realX
	if xTo > xFrom:
		direction = 1
	else: 
		direction = -1
	if realWrite:		
		moveMotor ('C', abs(xFrom-xTo), direction)
	realX = xTo

#parse image line
def parseLine(y, direction):
	global writing
	global realX
	x = 1	
	startX = endX = 0
	while x < cols:
		if direction > 0:
			detectX = x
		else:
			detectX = cols - x
		if detectBlack (detectX,y):  
			if not writing:
				print ("moving to ", str(detectX), " and starting to write")				
				movePen (realX, detectX)
				startX = detectX
				penDown()				
		else:
			if writing:
				print ("moving to ", str(detectX), " and stopping writing")
				endX = detectX
				if endX != startX:
					canvas.create_line(startX, y, endX, y, width=step)
					canvas.pack()
					win.update()
					win.update_idletasks()
					
				movePen (realX, detectX)				
				penUp()
			
		x = x + step
	if writing:
		endX = detectX
		canvas.create_line(startX, y, endX, y, width=step)
		canvas.pack()
		win.update()
		win.update_idletasks()
		
		movePen (realX, detectX)
		penUp()

def checkLine (y):
	x = 1
	while x < cols:
		if detectBlack (x,y):  			
			return True
		x = x + step
	return False

#start from top left
y=1
realX = 1

#start from left to right
direction = 1

#sart with the pen up
writing = False

#connect to the unit
if realWrite:
	conn = get_connection_bleak(hub_name='Auto Mňau')
	hub = MoveHub(conn)

#turn off the light
if realWrite:
	hub.led.color = (0, 0, 0)

#Move motor by angle (just for simplification)
def moveMotor(which, angle, clockwise = 1, speed = .1, wait = True):
	if realWrite:
		if which == 'A':
			hub.motor_A.angled(angle * clockwise, speed, speed, wait)		
		elif which == 'B':
			hub.motor_B.angled(angle * clockwise, speed, speed, wait)
		elif which == 'C':
			hub.port_C.angled(angle * clockwise, speed, speed, wait)

#Load paper
if realWrite:
	loadPaper()

while y < rows:	
#skip empty line
	yStep = step
	while y + yStep < rows:
		if checkLine (y+yStep):		
			y = y + yStep
			if writing:
				penUp()
				writing = False
			print ("moving to line n. ",str(y))
#a little hacky move to next line
			if realWrite:
				moveMotor ('B', yStep+step*2.5, -1)	
				moveMotor ('B', step*2, 1)	
			parseLine (y, direction)
#revert direction every line	
			direction = direction * -1	
			break		
		else:
			yStep = yStep + step

	if y+yStep >= rows:
		break

if writing:
	penUp()

if realWrite:
	ejectPaper()
#That's all folks!

if realWrite:
	hub.disconnect()  
input()
