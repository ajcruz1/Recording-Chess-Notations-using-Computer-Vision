#!/usr/bin/env

import sys
import record_chess
import timer
import cv2 as cv
import numpy as np
import datetime
import chess
import chess.pgn
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from selenium import webdriver

#################################################
# translate following methods					#
# [/] locateChessboard							#
# [/] defineSquares								#
# [/] boardRotations							#
# [/] locateMove								#
# implement following methods					#
# [/] validateMove								#
# [/] writeMove									#
# [|] chessClock ****almost done				#
# [x] GUI 										#
#################################################

class App(QMainWindow):
	keyPressed = pyqtSignal(QEvent)

	def __init__(self):
		super(App, self).__init__()
		self.title = 'ChessRecorder'
		self.left = 10
		self.top = 10
		self.width = 1280
		self.height = 720
		self.status = 'none'
		self.initUI()

	def initUI(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)
		self.mainMenu()
		
	def mainMenu(self):
		mainMenuPanel = QWidget()
		setupButton = QPushButton('Setup')
		helpButton = QPushButton('Help')
		quitButton = QPushButton('Quit')

		setupButton.setFixedWidth(50)
		helpButton.setFixedWidth(50)
		quitButton.setFixedWidth(50)

		setupButton.clicked.connect(self.getIpAddress)
		quitButton.clicked.connect(self.quit);

		layout = QVBoxLayout();
		layout.addWidget(setupButton)
		layout.addWidget(helpButton)
		layout.addWidget(quitButton)
		layout.setAlignment(Qt.AlignHCenter)
		layout.setSpacing(40)

		mainMenuPanel.setLayout(layout)

		self.setCentralWidget(mainMenuPanel)

	def infoMenu(self):
		infoPrompt = QDialog()
		
		self.formGroupBox = QGroupBox()
		layout = QFormLayout()
		self.eventLine = QLineEdit()
		self.whiteLine = QLineEdit()
		self.blackLine = QLineEdit()
		self.roundLine = QSpinBox()
		self.timeLine = QSpinBox()

		layout.addRow(QLabel("Event:"), self.eventLine)
		layout.addRow(QLabel("White:"), self.whiteLine)
		layout.addRow(QLabel("Black:"), self.blackLine)
		layout.addRow(QLabel("Round:"), self.roundLine)
		layout.addRow(QLabel("Time (in minutes):"), self.timeLine)
		self.formGroupBox.setLayout(layout)

		buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
		buttonBox.accepted.connect(self.accept)

		infoPromptLayout = QVBoxLayout()
		infoPromptLayout.addWidget(self.formGroupBox)
		infoPromptLayout.addWidget(buttonBox)
		infoPrompt.setLayout(infoPromptLayout)
		self.setCentralWidget(infoPrompt)


	def accept(self):		
		self.writer.headers["Event"] = self.eventLine.text()
		self.writer.headers["White"] = self.whiteLine.text()
		self.writer.headers["Black"] = self.blackLine.text()
		self.writer.headers["Round"] = self.roundLine.text()
		time = int(self.timeLine.text()) * 60
		self.writer.headers["Date"] = datetime.datetime.now().strftime("%Y.%m.%d")

		self.record = Record(int(time))
		self.setCentralWidget(self.record)
		self.record.forfeitButton.clicked.connect(self.forfeitAction)
		self.record.offerButton.clicked.connect(self.offerAction)
		self.record.start()


	def getIpAddress(self):
		text, ok = QInputDialog.getText(self, 'Setup', 'Enter IP Address of camera')
		if ok:
			self.ipAddress = text
			self.cap, self.driver = record_chess.openVideoStream(self.ipAddress)
			self.status = 'setup'

			self.stream = Stream(self.cap)
			self.setCentralWidget(self.stream)
			self.stream.start()

	def setAngle(self, item):
		if item == "Left":
			self.angle = cv.ROTATE_90_CLOCKWISE
		elif item == "Right":
			self.angle = cv.ROTATE_90_COUNTERCLOCKWISE
		elif item == "Bottom":
			self.angle = cv.ROTATE_180
		else:
			self.angle = -999

	def forfeitAction(self):
		confirm = QMessageBox.question(self, 'Confirmation', 'Are you sure you want to forfeit?')
		if confirm == QMessageBox.Yes:
			if self.record.whiteTimer.isRunning():
				if self.record.move > 0:
					self.record.notationsPanel.insertRow(self.record.move)
					self.record.notationsPanel.scrollToBottom()
				self.record.notationsPanel.setItem(self.record.move, 0, QTableWidgetItem("0-1"))
				self.writer.headers["Result"] = "0-1"
			else:
				self.record.notationsPanel.setItem(self.record.move, 1, QTableWidgetItem("1-0"))
				self.writer.headers["Result"] = "1-0"

			self.record.stop()
			self.gameOver()

	def offerAction(self):
		confirm = QMessageBox.question(self, 'Confirmation', 'Do you want to accept draw?')
		if confirm == QMessageBox.Yes:
			if self.record.whiteTimer.isRunning():
				if self.record.move > 0:
					self.record.notationsPanel.insertRow(self.record.move)
					self.record.notationsPanel.scrollToBottom()
				self.record.notationsPanel.setItem(self.record.move, 0, QTableWidgetItem("1/2-1/2"))
			else:
				self.record.notationsPanel.setItem(self.record.move, 1, QTableWidgetItem("1/2-1/2"))

			self.record.stop()
			self.writer.headers["Result"] = "1/2-1/2"
			self.gameOver()

	def gameOver(self):
		buttonReply = QMessageBox.question(self, 'Game Over', "Would you like to save the game?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		if buttonReply == QMessageBox.Yes:
			# file = open(writer.headers["Event"]+writer.headers["Date"]+writer.headers["Round"]+writer.headers["White"]+writer.headers["Black"], 'w')
			file = open("saved_games/"+self.writer.headers["White"]+"_vs_"+self.writer.headers["Black"]+"_"+self.writer.headers["Round"]+"_"+self.writer.headers["Event"]+"_"+self.writer.headers["Date"]+".pgn", 'w')
			print >>file, self.writer
			file.close()

		buttonReply = QMessageBox.question(self, 'Game Over', "Would you like to play again?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
		if buttonReply == QMessageBox.Yes:
			QMessageBox.about(self, "Reset", "Setup pieces then press enter.")
			self.status = 'setup1'
			self.stream = Cropped(self.cap, self.perspective)
			self.setCentralWidget(self.stream)
			self.stream.start()
		else:
			self.status = 'setup'
			self.mainMenu()

	def getImage(self):
		frame = None
		while type(frame) == type(None):
			self.cap.release()
			address = "http://" + self.ipAddress + ":8080/video"
			self.cap = cv.VideoCapture(address)
			__, frame = self.cap.read()

		return frame

	def quit(self):
		self.close()

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Return and self.status == 'setup':
			QMessageBox.about(self, "", "Setting up...")
			chessboard = self.getImage()
			found = False
			found, self.corners, self.perspective = record_chess.isolateChessboard(chessboard)
			self.stream.stop()
			self.stream.deleteLater()
			self.stream = Cropped(self.cap, self.perspective)
			self.setCentralWidget(self.stream)
			self.stream.start()
			if found:
				self.squares = record_chess.defineSquares(self.corners)
				self.fgbg = record_chess.initializeBackground(self.cap, self.driver, self.perspective)
				self.status = 'setup1'
				QMessageBox.about(self, "", "Setup chess pieces then press enter")
			else:
				QMessageBox.about(self, "Error", "Chessboard not found, please make sure that the whole chessboard is visible on the camera.")

		elif event.key() == Qt.Key_Return and self.status == 'setup1':
			self.stream.stop()
			self.stream.deleteLater()
			self.prevState = self.getImage()
			record_chess.findOptimalExposure(self.driver, self.cap, self.perspective, self.fgbg, self.squares)
			self.prevState = self.getImage()
			self.croppedP = record_chess.processImages(self.prevState, self.perspective, self.fgbg)
			
			items = ("Left", "Right", "Top", "Bottom")
			item, ok = QInputDialog.getItem(self, "", "Where are the black pieces in the image", items, 0, False)
			if ok and item:
				self.setAngle(item)
				self.status = 'recording'
				self.board = chess.Board()
				self.writer = chess.pgn.Game()
				self.node = None
				self.infoMenu()

		elif event.key() == Qt.Key_Return and self.status == 'recording':
			self.currState = self.getImage()
			self.croppedC = record_chess.processImages(self.currState, self.perspective, self.fgbg)
			valid, self.node, en_passant = record_chess.processMoves(self, self.croppedC, self.croppedP, self.angle, self.squares, self.board, self.writer, self.node)
			ok = False

			if valid:
				self.croppedP = np.copy(self.croppedC)
				self.record.updateTable(self.node.san())

				if self.node.san() == 'O-O' or self.node.san() == 'O-O-O':
					ok = QMessageBox.question(self, "", "Found castling, move rook to other side then press OK!", QMessageBox.Ok)
					while True:
						self.currState = self.getImage()
						self.croppedP = record_chess.processImages(self.currState, self.perspective, self.fgbg)
						if ok == QMessageBox.Ok:
							break

				if en_passant:
					ok = QMessageBox.question(self, "", "Found en passant, remove captured piece then press OK!", QMessageBox.Ok)
					while True:
						self.currState = self.getImage()
						self.croppedP = record_chess.processImages(self.currState, self.perspective, self.fgbg)
						if ok == QMessageBox.Ok:
							break
			        
				if self.board.is_game_over():
					self.record.stop()
					self.record.deleteLater()
					self.writer.headers["Result"] = self.board.result()
					if not self.record.whiteTimer.isRunning():
						if self.record.move > 0:
							self.record.notationsPanel.insertRow(self.record.move)
							self.record.notationsPanel.scrollToBottom()
						self.record.notationsPanel.setItem(self.record.move, 0, QTableWidgetItem(self.board.result()))
					else:
						self.record.notationsPanel.setItem(self.record.move, 1, QTableWidgetItem(self.board.result()))
					self.gameOver()

				self.record.toggle()

			else:
				QMessageBox.about(self, "", "INVALID MOVE!!")
			

class Stream(QWidget):
	def __init__(self, cap):
		super(Stream, self).__init__()

		self.fps = 30
		self.cap = cap

		self.video_frame = QLabel()
		layout = QVBoxLayout()
		layout.addWidget(self.video_frame)
		layout.setAlignment(Qt.AlignHCenter)
		self.setLayout(layout)

	def nextFrameSlot(self):
		ret, frame = self.cap.read()
		frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
		img = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
		pix = QPixmap.fromImage(img)
		pix = pix.scaledToWidth(700)
		self.video_frame.setPixmap(pix)

	def start(self):
		self.timer = QTimer()
		self.timer.timeout.connect(self.nextFrameSlot)
		self.timer.start(1000./self.fps)

	def stop(self):
		self.timer.stop()

	def deleteLater(self):
		super(QWidget, self).deleteLater()

class Cropped(QWidget):
	def __init__(self, cap, perspective):
		super(Cropped, self).__init__()

		self.fps = 30
		self.cap = cap
		self.perspective = perspective

		self.video_frame = QLabel()
		layout = QVBoxLayout()
		layout.addWidget(self.video_frame)
		layout.setAlignment(Qt.AlignHCenter)
		self.setLayout(layout)

	def nextFrameSlot(self):
		ret, frame = self.cap.read()
		frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
		frame = cv.resize(frame, (0,0), fx=0.33, fy=0.33)
		cropped = cv.warpPerspective(frame,self.perspective,(300,300))

		img = QImage(cropped, cropped.shape[1], cropped.shape[0], QImage.Format_RGB888)
		pix = QPixmap.fromImage(img)
		self.video_frame.setPixmap(pix)

	def start(self):
		self.timer = QTimer()
		self.timer.timeout.connect(self.nextFrameSlot)
		self.timer.start(1000./self.fps)

	def stop(self):
		self.timer.stop()

	def deleteLater(self):
		super(QWidget, self).deleteLater()

class Record(QWidget):
	def __init__(self, time):
		super(Record, self).__init__()

		wholePanelLayout = QHBoxLayout()

		#create a panel for the chess clocks
		timerPanel = QWidget()
		timerPanelLayout = QHBoxLayout()
		
		self.whiteTimerLabel = QLabel()
		self.blackTimerLabel = QLabel()
		self.whiteTimerLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.whiteTimerLabel.setFont(QFont('SansSerif', 20))
		self.whiteTimerLabel.setAlignment(Qt.AlignCenter)
		self.blackTimerLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.blackTimerLabel.setAlignment(Qt.AlignCenter)
		self.blackTimerLabel.setFont(QFont('SansSerif', 20))
		
		timerPanelLayout.addWidget(self.whiteTimerLabel)
		timerPanelLayout.addWidget(self.blackTimerLabel)
		timerPanelLayout.setAlignment(Qt.AlignVCenter)
		
		timerPanel.setLayout(timerPanelLayout)
		timerPanel.setStyleSheet('background-color: blue')

		#create a panel for buttons to forfeit, offer draw, claim draw
		buttonPanel = QWidget()
		buttonPanelLayout = QHBoxLayout()
		
		self.forfeitButton = QPushButton('Forfeit')
		self.offerButton = QPushButton('Offer Draw')
		self.claimButton = QPushButton('Claim Draw')
		
		self.forfeitButton.setFixedWidth(100)
		self.offerButton.setFixedWidth(100)
		self.claimButton.setFixedWidth(100)

		buttonPanelLayout.addWidget(self.forfeitButton)
		buttonPanelLayout.addWidget(self.offerButton)
		buttonPanelLayout.addWidget(self.claimButton)
		buttonPanel.setFixedHeight(80)
		buttonPanel.setLayout(buttonPanelLayout)

		#create left panel
		leftPanel = QWidget()
		leftPanelLayout = QVBoxLayout()
		leftPanelLayout.addWidget(timerPanel)
		leftPanelLayout.addWidget(buttonPanel)
		leftPanel.setLayout(leftPanelLayout)

		#creates the count down timer of chess clocks
		self.whiteTimer = timer.Timer(time, self.whiteTimerLabel, "WHITE")
		self.blackTimer = timer.Timer(time, self.blackTimerLabel, "BLACK")

		#creates the display for moves recorded
		self.notationsPanel = QTableWidget()
		self.notationsPanel.setColumnCount(2)
		self.notationsPanel.setRowCount(1)
		self.notationsPanel.setHorizontalHeaderLabels(['White','Black'])
		self.notationsPanel.setFixedWidth(self.notationsPanel.columnWidth(0)+self.notationsPanel.columnWidth(1)+15)

		wholePanelLayout.addWidget(leftPanel)
		wholePanelLayout.addWidget(self.notationsPanel)

		self.move = 0
		self.setLayout(wholePanelLayout)

	def start(self):
		self.whiteTimer.start()
		self.blackTimer.start()
		self.blackTimer.pause()
		self.whiteTimerLabel.setFont(QFont('SansSerif', 20, QFont.Bold))
	
	def stop(self):
		self.whiteTimer.stop()
		self.blackTimer.stop()

	def deleteLater(self):
		super(QWidget, self).deleteLater()

	def toggle(self):
		if self.whiteTimer.isRunning():
			self.blackTimer.resume()
			self.whiteTimer.pause()
			self.whiteTimerLabel.setFont(QFont('SansSerif', 20))	
			self.blackTimerLabel.setFont(QFont('SansSerif', 20, QFont.Bold))

		else:
			self.whiteTimer.resume()
			self.blackTimer.pause()
			self.blackTimerLabel.setFont(QFont('SansSerif', 20))	
			self.whiteTimerLabel.setFont(QFont('SansSerif', 20, QFont.Bold))

	def updateTable(self, notation):
		if self.whiteTimer.isRunning():
			if self.move > 0:
				self.notationsPanel.insertRow(self.move)
				self.notationsPanel.scrollToBottom()
			self.notationsPanel.setItem(self.move, 0, QTableWidgetItem(notation))
		else:
			self.notationsPanel.setItem(self.move, 1, QTableWidgetItem(notation))
			self.move = self.move + 1

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = App()
	ex.show()

sys.exit(app.exec_())