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
			
			hiddenWindow = QtOpenGL.QGLWidget( QtOpenGL.QGLContext(fmt, None) )
			GLWidget.sharedWidget = hiddenWindow
			hiddenWindow.makeCurrent()
	
		return GLWidget.sharedWidget

	def __init__(self,parent=None):
		sharedWidget = GLWidget.getSharedWidget()
		QtOpenGL.QGLWidget.__init__(self, parent, sharedWidget)

		self.setFocusPolicy(QtCore.Qt.StrongFocus)
		self.setMinimumSize( 32, 32 )
		self.allowRefresh   = False
		self.pendingRefresh = False

		self.refreshTimer   = QtCore.QTimer(self)
		self.refreshTimer.setSingleShot( True )
		self.refreshTimer.timeout.connect(self.onRefreshTimer)
		self.setMouseTracking(True)

	def startRefreshTimer( self, fps = 60 ):
		# self.refreshTimer.start( 1000/fps )
		self.allowRefresh = True
		self.refreshTimer.setInterval( 10 )

	def stopRefreshTimer(self):
		self.allowRefresh = False
		self.refreshTimer.stop()

	def forceUpdateGL(self):
		self.allowRefresh = True
		self.refreshTimer.stop()
		self.updateGL()

	def minimumSizeHint(self):
		return QtCore.QSize(50, 50)

	def onRefreshTimer(self): #auto render if has pending render
		if self.pendingRefresh:
			self.pendingRefresh = False
			self.allowRefresh = True
			self.updateGL()
		self.allowRefresh = True

	def paintGL( self ):		
		self.onDraw()

	def updateGL( self ):
		if not self.allowRefresh:
			self.pendingRefresh = True
			return
		self.allowRefresh = False
		self.refreshTimer.start()
		super( GLWidget, self ).updateGL()

	def onDraw(self):
		pass
