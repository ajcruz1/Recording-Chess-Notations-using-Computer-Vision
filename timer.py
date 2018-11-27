#!/usr/bin/env

import time
import threading
import thread
from PyQt5.QtWidgets import *

class Timer(threading.Thread):
	def __init__(self, time, label, color):
		threading.Thread.__init__(self)
		self.can_run = threading.Event()
		self.thing_done = threading.Event()
		self.thing_done.set()
		self.can_run.set()
		self.t = time
		self.label = label
		self.color = color
		self.running = True

	def run(self):
		while self.t > -1:
			self.can_run.wait()
			try: 
				self.thing_done.clear()

				mins, secs = divmod(self.t, 60)
				timeformat = '{:02d}:{:02d}'.format(mins, secs)
				if self.t > -1:
					self.label.setText(self.color + "\n\n" + timeformat)
				time.sleep(1)
				self.t = self.t - 1
			finally:
				self.thing_done.set()

	def pause(self):
		self.can_run.clear()
		self.thing_done.wait()
		self.running = False

	def resume(self):
		self.can_run.set()
		self.running = True

	def stop(self):
		self.can_run.set()
		self.thing_done.set()
		self.t = -1

	def isRunning(self):
		return self.running