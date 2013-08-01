from PyQt4 import QtCore, QtGui, QtOpenGL

class GLWidget(QtOpenGL.QGLWidget):
	sharedWidget = None
	@staticmethod
	def getSharedWidget():
		if not GLWidget.sharedWidget:
			fmt=QtOpenGL.QGLFormat()
			fmt.setRgba(True)
			fmt.setAlpha(True)
			fmt.setDepth(True)
			fmt.setDoubleBuffer(True)
			fmt.setSwapInterval(1)
			QtOpenGL.QGLFormat.setDefaultFormat(fmt)
			
			hiddenWindow = QtOpenGL.QGLWidget(QtOpenGL.QGLContext(fmt, None))
			GLWidget.sharedWidget = hiddenWindow
			hiddenWindow.makeCurrent()

		return GLWidget.sharedWidget

	def __init__(self,parent=None):
		sharedWidget = GLWidget.getSharedWidget()

		QtOpenGL.QGLWidget.__init__(self, parent, sharedWidget)
		self.setFocusPolicy(QtCore.Qt.StrongFocus)
		
		self.allowRefresh=False
		self.pendingRefresh=False

		self.refreshTimer=QtCore.QTimer(self)
		self.refreshTimer.timeout.connect(self.onRefreshTimer)
		self.setMouseTracking(True)
		

	def startRefreshTimer(self,fps=60):
		self.refreshTimer.start(1000/fps)

	def stopRefreshTimer(self):
		self.allowRefresh=False
		self.refreshTimer.stop()

	def forceUpdateGL(self):
		self.allowNextRefresh()
		self.updateGL()

	def allowNextRefresh(self):
		self.allowRefresh=True

	def minimumSizeHint(self):
		return QtCore.QSize(50, 50)

	def onRefreshTimer(self): #auto render if has pending render
		self.allowNextRefresh()
		if self.pendingRefresh:
			self.updateGL()

	# def sizeHint(self):
	# 	return QtCore.QSize(400, 400)
		
	def paintGL( self ):
		if not self.allowRefresh:
			self.pendingRefresh = True
			return
		self.allowRefresh     = False
		self.pendingRefresh   = False
		self.onDraw()

	def onDraw(self):
		pass
