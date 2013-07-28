import os.path
import time
import logging

from PyQt4        import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt

from gii.qt       import QtEditorModule
from gii.core     import signals, app

from MOAIRuntime  import getAKU
from canvas       import MOAICanvasBase

##----------------------------------------------------------------##
class MOAIGameView( QtEditorModule ):
	"""docstring for MOAIGameView"""
	def __init__(self):
		super(MOAIGameView, self).__init__()
		self.runningScript  = False
		self.pendingScript  = False
		self.restartPending = False
		self.paused         = False
		self.waitActivate   = False

		self.viewWidth      = 0
		self.viewHeight     = 0

	def getName(self):
		return 'moai.game'

	def getDependency(self):
		return [ 'qt', 'moai' ]

	def getRuntime(self):
		return self.getManager().affirmModule('moai')

	def tryResizeContainer(self, w,h):
		self.getQtSupport().getMainWindow().resize(w,h)
		return True
		# if self.container.isFloating():
		# 	self.container.resize(w,h)
		# 	return True
		# else:
		# 	return False

	def setOrientationPortrait( self ):
		if self.container.isFloating():
			pass #TODO
		getAKU().setOrientationPortrait()

	def setOrientationLandscape( self ):
		if self.container.isFloating():
			pass #TODO
		getAKU().setOrientationLandscape()

	def onOpenWindow(self, title, w,h):
		#no argument accepted here, just use full window
		self.getRuntime().initGLContext()
		self.originalSize = (w,h)
		self.tryResizeContainer( *self.originalSize )

		size=self.canvas.size()
		w,h = size.width(),size.height()

		if w > h:
			getAKU().setOrientationLandscape()
		else:
			getAKU().setOrientationPortrait()

		getAKU().setScreenSize(w,h)
		getAKU().setViewSize(w,h)

		self.container.show()
		self.setFocus()

	def onLoad(self):
		self.container = self.requestDocumentWindow('MOAIGameView',
			title   = "Game",
			minSize = (100,100),			
			size    = (300,300),
			dock    = 'main'
			)

		fps = 60
		self.canvas = self.container.addWidget(MOAIGameViewCanvas(self.container))
		self.canvas.startRefreshTimer(fps)
		self.paused = True
		
		self.canvas.module = self

		self.updateTimer = self.container.startTimer(1000/fps, self.updateView)
		self.container.setFocusPolicy(Qt.StrongFocus)
		
		signals.connect( 'app.command',    self.onAppCommand )
		signals.connect( 'app.activate',   self.onAppActivate )
		signals.connect( 'app.deactivate', self.onAppDeactivate )
		
		signals.connect( 'debug.enter',    self.onDebugEnter )
		signals.connect( 'debug.exit',     self.onDebugExit )
		signals.connect( 'debug.stop',     self.onDebugStop )
		
		signals.connect( 'game.pause',     self.onGamePause )
		signals.connect( 'game.resume',    self.onGameResume )
		signals.connect( 'moai.reset',     self.onMoaiReset )

		self.addMenu( 'main/game' )
		self.findMenu( 'main/game' ).addChild([
				'----',
				{'name':'orient_landscape', 'label':'Landscape'  },
				{'name':'orient_portrait', 'label':'Portrait'  },
				'----',
				{'name':'size_original', 'label':'Original Size' },
				{'name':'size_double',   'label':'Double Size'   },
				'----',
				{'name':'pause_on_leave','label':'Pause On Leave', 'type':'check', 'checked':self.getConfig('pause_on_leave')},
				'----',
				{'name':'reset_moai','label':'RESET MOAI', 'shortcut':'Ctrl+Shift+R'}
			], self)

		# self.restoreWindowState(self.container)
		self.onMoaiReset() #moai is already ready...
		


	def updateView(self):
		if self.paused: return
		before  = time.clock()
		runtime = self.getRuntime()
		runtime.setBufferSize( self.viewWidth, self.viewHeight )
		runtime.changeRenderContext('game')
		
		if runtime.updateAKU():
			used=time.clock()-before
			self.canvas.forceUpdateGL()

	def resizeView(self, w,h):
		self.viewWidth  = w
		self.viewHeight = h
		getAKU().setScreenSize(w,h)
		getAKU().setViewSize(w,h)		
			
	def renderView(self):
		if self.paused: return
		before  = time.clock()
		runtime = self.getRuntime()
		runtime.setBufferSize(self.viewWidth,self.viewHeight)
		runtime.changeRenderContext('game')

		if runtime.renderAKU():
			used=time.clock()-before

	def onFileModified(self, path):
		if path==self.runningScript:
			self.restartPending=True
			self.restartScript(path)

	def restartScript(self,src):
		runtime=self.getRuntime()
		if self.runningScript: runtime.reset()
		
		relpath = src #AssetLibrary.get().getRelPath(src)
		# src = os.path.abspath(src)
		self.runningScript=src

		runtime.changeRenderContext('game')	
		
		logging.info( 'running script:%s' % src )
		runtime.runScript( src )
		self.container.setWindowTitle( 'Game<%s>' % relpath )

		self.restartPending=False

	def onMoaiReset(self):
		runtime=self.getRuntime()
		runtime.createRenderContext( 'game' )
		self.canvas.setInputDevice(
			runtime.addDefaultInputDevice()
			)
		getAKU().setFuncOpenWindow(self.onOpenWindow)

		
	def onAppCommand(self, cmd, data=None, *args):
		if cmd=='exec':
			src = app.getProjectPath(data)
			if app.isDebugging():
				self.pendingScript=src
				self.restartPending=True #will load when debug ends
			else:
				signals.callAfter( self.restartScript, src )

	def start(self):
		self.paused=False
		script = self.getApp().getConfig( 'start_script', None )
		if script:
			self.restartScript( script )
	
	def onUnload(self):
		# self.saveWindowState(self.container)
		self.updateTimer.stop()
		self.container.destroy()

	def onDebugEnter(self):
		self.paused=True
		self.getRuntime().pause()
		self.container.setFocusPolicy(Qt.NoFocus)

	def onDebugExit(self, cmd=None):
		self.paused=False
		self.getRuntime().resume()
		self.container.setFocusPolicy(Qt.StrongFocus)
		if self.pendingScript:
			script=self.pendingScript
			self.pendingScript=False
			self.restartScript(script)
		self.setFocus()
		
	def onDebugStop(self):
		self.paused=True

	def setFocus(self):
		# getModule('main').setFocus()
		self.container.show()
		self.container.raise_()
		self.container.setFocus()
		self.canvas.setFocus()
		self.canvas.activateWindow()
		self.setActiveWindow(self.container)

	def onGamePause(self):
		self.getRuntime().pause()

	def onGameResume(self): #TODO: proper pause state
		self.getRuntime().resume()

	def onAppActivate(self):
		if self.waitActivate:
			self.waitActivate=False
			self.getRuntime().resume()

	def onAppDeactivate(self):
		if self.getConfig('pause_on_leave',False):
			self.waitActivate=True
			self.getRuntime().pause()

	def onMenu(self, node):
		name=node.name
		if name=='size_double':
			if self.originalSize:
				w,h=self.originalSize
				self.tryResizeContainer(w*2,h*2)

		elif name=='size_original':
			if self.originalSize:
				w,h=self.originalSize
				self.tryResizeContainer(w,h)

		elif name=='pause_on_leave':
			self.setSettingValue('pause_on_leave', node.getValue())

		elif name=='reset_moai':
			#TODO: dont simply reset in debug
			self.restartScript(self.runningScript)

		elif name=='orient_portrait':
			self.setOrientationPortrait()

		elif name=='orient_landscape':
			self.setOrientationLandscape()

##----------------------------------------------------------------##
class MOAIGameViewCanvas(MOAICanvasBase):
	def resizeGL(self, width, height):
		self.module.resizeView(width,height)
		self.updateGL()

	def onDraw(self):
		self.module.renderView()
		
##----------------------------------------------------------------##
MOAIGameView().register()
