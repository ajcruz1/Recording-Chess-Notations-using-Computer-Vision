#!/usr/bin/env

import pprint
import chess
import chess.pgn
import numpy as np
import cv2 as cv
import math
import operator

################################################
# translate following methods
# [/] locateChessboard
# [/] defineSquares
# [/] boardRotations
# [/] locateMove
# implement following methods
# [x] validateMove
# [x] writeMove
# [x] chessClock
################################################

def locateChessboard(corners):
	tempx = corners[8][0][0] - corners[0][0][0]
	tempy = corners[8][0][1] - corners[0][0][1]
	
	tempx1 = (tempx * math.cos(180 * math.pi / 180)) - (tempy * math.sin(180 * math.pi / 180))
	tempy1 = (tempx * math.sin(180 * math.pi / 180)) + (tempy * math.cos(180 * math.pi / 180))

	ll = [tempx1+corners[0][0][0],tempy1+corners[0][0][1]]

	tempx = corners[12][0][0] - corners[6][0][0]
	tempy = corners[12][0][1] - corners[6][0][1]
	
	tempx1 = (tempx * math.cos(180 * math.pi / 180)) - (tempy * math.sin(180 * math.pi / 180))
	tempy1 = (tempx * math.sin(180 * math.pi / 180)) + (tempy * math.cos(180 * math.pi / 180))

	ul = [tempx1+corners[6][0][0],tempy1+corners[6][0][1]]	

	tempx = corners[36][0][0] - corners[42][0][0]
	tempy = corners[36][0][1] - corners[42][0][1]
	
	tempx1 = (tempx * math.cos(180 * math.pi / 180)) - (tempy * math.sin(180 * math.pi / 180))
	tempy1 = (tempx * math.sin(180 * math.pi / 180)) + (tempy * math.cos(180 * math.pi / 180))

	lr = [tempx1+corners[42][0][0],tempy1+corners[42][0][1]]

	tempx = corners[40][0][0] - corners[48][0][0]
	tempy = corners[40][0][1] - corners[48][0][1]
	
	tempx1 = (tempx * math.cos(180 * math.pi / 180)) - (tempy * math.sin(180 * math.pi / 180))
	tempy1 = (tempx * math.sin(180 * math.pi / 180)) + (tempy * math.cos(180 * math.pi / 180))

	ur = [tempx1+corners[48][0][0],tempy1+corners[48][0][1]]

	return ul, ll, ur, lr

def defineSquares(corners):
	# define boundaries of regions of interests
	# these coordinates will be used to locate where the changes are
	squares = dict()
	squares['a8'] = [0, int(corners[0][0][1]), 0, int(corners[0][0][0])]
	squares['h8'] = [0, int(corners[6][0][1]), int(corners[6][0][0]), 300]
	squares['a1'] = [int(corners[42][0][1]), 300, 0, int(corners[42][0][0])]
	squares['h1'] = [int(corners[48][0][1]), 300, int(corners[48][0][0]), 300]
	
	c = 97
	x = 7

	for i in range(1,7):
		squares[chr(c)+str(x)] = [int(corners[(i*7)-7][0][1]), int(corners[i*7][0][1]), 0, int(corners[i*7][0][0])]
		x = x - 1

	c = c + 1
	x = 7

	for i in range(1,7):
		squares[chr(c)+str(8)] = [0, int(corners[i][0][1]), int(corners[i-1][0][0]), int(corners[i][0][0])]
		squares[chr(c)+str(1)] = [int(corners[i+42][0][1]), 300, int(corners[i+41][0][0]), int(corners[i+42][0][0])]
		c = c + 1

	c = 98

	for i in range(1,7):
		x = 7
		for j in range(1,7):
			squares[chr(c)+str(x)] = [int(corners[((j*7)-7)+i][0][1]), int(corners[(j*7)+i][0][1]), int(corners[((j*7)-7)+(i-1)][0][0]), int(corners[(j*7)+i][0][0])]
			x = x - 1
		c = c + 1

	x = 7

	for i in range(1,7):
		squares[chr(c)+str(x)] = [int(corners[(i*7)-1][0][1]), int(corners[((i*7)-1)+7][0][1]), int(corners[(i*7)-1][0][0]), 300]
		x = x - 1

	return squares

def boardRotations(img, squares):
	rectA8 = img[squares['a8'][0]:squares['a8'][1],squares['a8'][2]:squares['a8'][3]]
	rectH8 = img[squares['h8'][0]:squares['h8'][1],squares['h8'][2]:squares['h8'][3]]

	piecesA8 = cv.countNonZero(rectA8)
	piecesH8 = cv.countNonZero(rectH8)

	if piecesA8 == 0 and piecesH8 > 0:
		return cv.ROTATE_90_COUNTERCLOCKWISE
	elif piecesA8 > 0 and piecesH8 == 0:
		return cv.ROTATE_90_CLOCKWISE
	elif piecesA8 == 0 and piecesH8 == 0:
		return cv.ROTATE_180
	else:
		return -1000

def locateMove(img, squares):
	whitePixels = 0
	counted = dict()

	for key in squares:
		print key
		square = img[squares[key][0]:squares[key][1],squares[key][2]:squares[key][3]]
		whitePixels = cv.countNonZero(square)
		counted[key] = whitePixels

	return counted

def validateMove(board, sorted_by_value, writer, node):

	if(chess.Move.from_uci(sorted_by_value[0][0] + sorted_by_value[1][0]) in board.legal_moves):
		board.push(chess.Move.from_uci(sorted_by_value[0][0] + sorted_by_value[1][0]))

		if node == None:
			node = writer.add_main_variation(chess.Move.from_uci(sorted_by_value[0][0] + sorted_by_value[1][0]))
		else:
			node = node.add_main_variation(chess.Move.from_uci(sorted_by_value[0][0] + sorted_by_value[1][0]))

	elif(chess.Move.from_uci(sorted_by_value[1][0] + sorted_by_value[0][0]) in board.legal_moves):
		board.push(chess.Move.from_uci(sorted_by_value[1][0] + sorted_by_value[0][0]))

		if node == None:
			node = writer.add_main_variation(chess.Move.from_uci(sorted_by_value[1][0] + sorted_by_value[0][0]))
		else:
			node = node.add_main_variation(chess.Move.from_uci(sorted_by_value[1][0] + sorted_by_value[0][0]))

	else:
		print "INVALID MOVE"
	
	return node

# initialization of chess board
# 'board' keeps track of the current state of the game
# and will also be used to validate the moves later on
board = chess.Board()
writer = chess.pgn.Game()

# asks the user for the IP address of the camera to be used
ipAdd = raw_input('Enter IP address of camera: ')
# formats the address for it to be properly opened in opencv
address = "http://" + ipAdd + ":8080/video"

# opens the IP camera
cap = cv.VideoCapture(address)
key = 0

# Take initial image of empty board
# waits for the user to press the enter key
# once the user presses the enter key, the program takes a screenshot of the board
while(key != ord('\n')):
	ret, frame = cap.read()

	cv.namedWindow('chessboard',cv.WINDOW_NORMAL)
	cv.resizeWindow('chessboard',720,480)
	cv.imshow('chessboard',frame)

	key = cv.waitKey(1)

cv.destroyWindow('chessboard')

frame = cv.resize(frame, (0,0), fx=0.33, fy=0.33)
# looks for the inner chessboard corners of the chessboard
found, corners = cv.findChessboardCorners(frame,(7,7))

if(found == True):
	# computes for the four outermost corners of the chessboard
	ul, ll, ur, lr = locateChessboard(corners)
	pts1 = np.float32([ul,ll,ur,lr])
	pts2 = np.float32([[0,0], [0,300], [300,0], [300,300]])

	# creates a transformation matrix to change the perspective 
	# and then transforms the image onto a 300x300 matrix
	perspective = cv.getPerspectiveTransform( pts1, pts2 )
	transformed = cv.warpPerspective(frame,perspective,(300,300))

	# updates the values of the corners
	found, corners = cv.findChessboardCorners(transformed,(7,7))

# test = cv.cornerHarris(transformed, 2, 3, 0.04)
# test = cv.dilate(test, None)
# transformed[test>0.01*test.max()] = 0
cv.imshow('test', transformed)
squares = defineSquares(corners)

# initializes background for MOG
print "Initializing background, this may take a few moments..."

fgbg = cv.createBackgroundSubtractorMOG2()

for i in range(1,500):
	ret, bg = cap.read()
	bg = cv.resize(bg, (0,0), fx=0.33, fy=0.33)
	
	croppedBG = cv.warpPerspective(bg,perspective,(300,300))

	cv.imshow('background', croppedBG)
	check = fgbg.apply(croppedBG, learningRate = 0.1)

print "Initalization done"

key = 0
while(key != ord('\n')):
	ret, prevState = cap.read()
	prevState = cv.resize(prevState, (0,0), fx=0.33, fy=0.33)

	croppedP = cv.warpPerspective(prevState,perspective,(300,300))

	cv.namedWindow('chessboard',cv.WINDOW_NORMAL)
	cv.resizeWindow('chessboard',720,480)
	cv.imshow('chessboard', croppedP)

	key = cv.waitKey(1)

# rotates the image to ensure that the black pieces are always at the top
hsv = np.copy(croppedP)
hsv = cv.cvtColor(croppedP, cv.COLOR_BGR2HSV)
imgThreshold = cv.inRange(hsv,(0,0,0),(180,255,30))
cv.imshow('imgThreshold', imgThreshold)

angle = boardRotations(imgThreshold, squares)

print "backsub"
for i in range(1,10):
	piecesP = fgbg.apply(croppedP,learningRate = 0)
piecesP[piecesP==127]=0
kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(9,9))
piecesP = cv.morphologyEx(piecesP, cv.MORPH_OPEN, kernel)

croppedP[piecesP==0] = (255,0,0)
print "done"

node = None
while True:
	key = 0
	while(key != ord('\n')):
		ret, currState = cap.read()
		currState = cv.resize(currState, (0,0), fx=0.33, fy=0.33)

		croppedC = cv.warpPerspective(currState,perspective,(300,300))

		cv.namedWindow('chessboard',cv.WINDOW_NORMAL)
		cv.resizeWindow('chessboard',720,480)
		cv.imshow('chessboard', croppedC)

		key = cv.waitKey(1)

	print "backsub"
	for i in range(1,10):
		piecesC = fgbg.apply(croppedC,learningRate = 0)
	piecesC[piecesC==127]=0
	kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(9,9))
	piecesC = cv.morphologyEx(piecesC, cv.MORPH_OPEN, kernel)
	
	croppedC[piecesC==0] = (255,0,0)
	print "done"

	diff = cv.absdiff(croppedC, croppedP)
	diff = cv.cvtColor(diff, cv.COLOR_BGR2GRAY)
	diff = cv.threshold(diff, 25, 255, cv.THRESH_BINARY)[1]
	kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(9,9))
	diff = cv.morphologyEx(diff, cv.MORPH_OPEN, kernel)
	diff = cv.rotate(diff,angle)

	# count number of non 0 pixels in the image
	counted = locateMove(diff,squares)
	sorted_by_value = sorted(counted.items(), key=operator.itemgetter(1), reverse = True)
	print sorted_by_value[0][0] + sorted_by_value[1][0]

	node = validateMove(board, sorted_by_value, writer, node)
	print writer

	cv.imshow('diff',diff)
	cv.imshow('croppedC', croppedC)
	cv.imshow('croppedP', croppedP)

	croppedP = np.copy(croppedC)


# When everything done, release the capture
# cap.release()
cv.destroyAllWindows()
