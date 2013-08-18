import tempfile
import os
import sys

from PyQt4 import QtCore,QtGui
from PyQt4.QtCore import Qt, QEvent, QObject

from gii    import signals
from gii.SceneEditor import SceneEditorModule

import ui_console

signals.register('console.exec')

##----------------------------------------------------------------##
class StdouCapture():
	def __init__(self):
		self.prevfd = None
		self.prev = None

		self.file = file = tempfile.NamedTemporaryFile()
		self.where=file.tell()

		sys.stdout.flush()
		self.prevfd = os.dup(sys.stdout.fileno())
		os.dup2(file.fileno(), sys.stdout.fileno())
		self.prev = sys.stdout
		sys.stdout = os.fdopen(self.prevfd, "w")

	def stop(self):
		os.dup2(self.prevfd, self.prev.fileno())
		sys.stdout = self.prev
		self.file.close()

	def read(self):
		file=self.file
		file.seek(self.where)
		output=None
		while True:
			line = file.readline()
			if not line:
				self.where = file.tell()
				return output
			else:
				if not output: output=''
				output+=line
		
class Console( SceneEditorModule ):
	"""docstring for Console"""

	def getName(self):
		return 'console'

	def getDependency(self):
		return ['qt', 'scene_editor']

	def write(self,text):
		self.panel.appendText(text)		

	def onLoad(self):

		self.container = self.requestDockWindow('Console',
				title   = 'Console',
				minSize = (100,100),
				dock    = 'bottom'
			)
		self.panel = self.container.addWidget(
				ConsoleWindow()
			)
		self.panel.module=self
		# self.stdoutCapture = StdouCapture()
		# self.stdOutFile=self.stdoutCapture.file
		# self.refreshTimer=self.container.startTimer( 10, self.doRefresh)
		sys.stdout=self

	def doRefresh(self):
		if self.alive:
			self.panel.appendText(self.stdoutCapture.read())

	def onStart( self ):
		self.container.show()

	def onUnload(self):
		# self.refreshTimer.stop()
		pass

##----------------------------------------------------------------##
class ConsoleWindow( QtGui.QWidget, ui_console.Ui_ConsoleWindow ):
	"""docstring for ConsoleWindow"""
	def __init__(self):
		super(ConsoleWindow, self).__init__()
		
		self.setupUi(self)

		self.history=[]
		self.historyCursor=0		
		self.buttonExec.clicked.connect(self.execCommand)
		self.buttonClear.clicked.connect(self.clearText)		
		
		self.textInput.installEventFilter(self)
		self.textInput.setFocusPolicy(Qt.StrongFocus)
		self.setFocusPolicy(Qt.StrongFocus)

	def eventFilter(self, obj, event):
		if event.type() == QEvent.KeyPress:
			if self.inputKeyPressEvent(event):
				return True

		return QObject.eventFilter(self, obj, event)

	def inputKeyPressEvent(self, event):
		key=event.key()
		if key == Qt.Key_Down: #next cmd history
			self.nextHistory()
		elif key == Qt.Key_Up: #prev
			self.prevHistory()
		elif key == Qt.Key_Escape: #clear
			self.textInput.clear()
		elif key == Qt.Key_Return or key == Qt.Key_Enter:
			self.execCommand()
		else:
			return False
		return True

	def execCommand(self):
		text = self.textInput.text()
		self.history.append(text)
		if len(self.history) > 10: self.history.pop(1)
		self.historyCursor=len(self.history)
		self.textInput.clear()
		# self.appendText(self.module.stdoutCapture.read())
		self.appendText(">>")
		self.appendText(text)
		self.appendText("\n")

		signals.emit('console.exec', text.encode('utf-8'))

	def prevHistory(self):
		count=len(self.history)
		if count == 0: return
		self.historyCursor = max(self.historyCursor-1, 0)
		self.textInput.setText(self.history[self.historyCursor])

	def nextHistory(self):
		count=len(self.history)
		if count<= self.historyCursor:
			self.historyCursor=count-1
			self.textInput.clear()
			return
		self.historyCursor = min(self.historyCursor+1, count-1)
		if self.historyCursor<0: return
		self.textInput.setText(self.history[self.historyCursor])

	def appendText(self, text):
		if not text: return
		self.textOutput.insertPlainText(text)
		self.textOutput.moveCursor(QtGui.QTextCursor.End)

	def clearText(self):
		self.textOutput.clear()

##----------------------------------------------------------------##
Console().register()
