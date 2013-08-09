from PyQt4 import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt

from gii.qt.controls.GLWidget import GLWidget
import ContextDetection

from MOAIRuntime import getAKU


def convertKeyCode(k):
	if k>1000:
		return (k&0xff)+(255 - 0x55)
	else:
		return k


class MOAICanvasBase(GLWidget):
	def __init__( self, parentWidget = None ):
		super(MOAICanvasBase,self).__init__(parentWidget)		
		self.inputDevice = None

	def setInputDevice(self, device):
		self.inputDevice = device

	def mousePressEvent(self, event):	
		inputDevice = self.inputDevice
		if not inputDevice: return
		button = event.button()		
		inputDevice.getSensor('pointer').enqueueEvent(event.x(), event.y())
		if   button == Qt.LeftButton:
			inputDevice.getSensor('mouseLeft').enqueueEvent(True)
		elif button == Qt.RightButton:
			inputDevice.getSensor('mouseRight').enqueueEvent(True)
		elif button == Qt.MiddleButton:
			inputDevice.getSensor('mouseMiddle').enqueueEvent(True)

	def mouseReleaseEvent(self, event):
		inputDevice=self.inputDevice
		if not inputDevice: return
		button = event.button()		
		inputDevice.getSensor('pointer').enqueueEvent(event.x(), event.y())
		if   button == Qt.LeftButton:
			inputDevice.getSensor('mouseLeft').enqueueEvent(False)
		elif button == Qt.RightButton:
			inputDevice.getSensor('mouseRight').enqueueEvent(False)
		elif button == Qt.MiddleButton:
			inputDevice.getSensor('mouseMiddle').enqueueEvent(False)

	def mouseMoveEvent(self, event):
		inputDevice=self.inputDevice
		if not inputDevice: return
		inputDevice.getSensor('pointer').enqueueEvent(event.x(), event.y())

	def wheelEvent(self, event):
		#TODO
		pass
		# steps = event.delta() / 120.0;
		# dx = 0
		# dy = 0
		# if event.orientation() == Qt.Horizontal : 
		# 	dx = steps
		# else:
		# 	dy = steps
		# x,y=event.x(), event.y()
		# self.delegate.onScroll( dx, dy, x, y )

	def keyPressEvent(self, event):
		if event.isAutoRepeat(): return
		inputDevice=self.inputDevice
		if not inputDevice: return
		key=event.key()
		if   key == Qt.Key_Shift:
			inputDevice.getSensor('keyboard').enqueueShiftEvent(True)
		elif key == Qt.Key_Control:
			inputDevice.getSensor('keyboard').enqueueControlEvent(True)
		elif key == Qt.Key_Alt:
			inputDevice.getSensor('keyboard').enqueueAltEvent(True)
		else:
			inputDevice.getSensor('keyboard').enqueueEvent(convertKeyCode(key), True)

	def keyReleaseEvent(self, event):
		inputDevice=self.inputDevice
		if not inputDevice: return
		key=event.key()
		if   key == Qt.Key_Shift:
			inputDevice.getSensor('keyboard').enqueueShiftEvent(False)
		elif key == Qt.Key_Control:
			inputDevice.getSensor('keyboard').enqueueControlEvent(False)
		elif key == Qt.Key_Alt:
			inputDevice.getSensor('keyboard').enqueueAltEvent(False)
		else:
			inputDevice.getSensor('keyboard').enqueueEvent(convertKeyCode(key), False)

