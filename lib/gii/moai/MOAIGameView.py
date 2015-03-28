import os.path
import time
import logging

from gii.qt                 import QtEditorModule
from gii.core               import signals, app
from gii.qt.controls.Window import MainWindow

from MOAIRuntime            import getAKU
from MOAICanvasBase         import MOAICanvasBase

from PyQt4                  import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore           import Qt

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
		return 'game'

	def getDependency(self):
		return [ 'qt', 'moai' ]

	def getMainWindow( self ):
		return self.mainWindow

	def setupMainWindow( self ):
		self.mainWindow = QtMainWindow( None )
		self.mainWindow.setBaseSize( 800, 600 )
		self.mainWindow.resize( 800, 600 )
		self.mainWindow.setWindowTitle( 'GAME' )
		self.mainWindow.setMenuWidget( self.getQtSupport().getSharedMenubar() )

		self.mainWindow.module = self

		# self.mainToolBar = self.mainWindow.requestToolBar( 'main' )

		self.statusBar = QtGui.QStatusBar()
		self.mainWindow.setStatusBar(self.statusBar)

	def getRuntime(self):
		return self.getManager().affirmModule('moai')

	def tryResizeContainer(self, w,h):
		self.getMainWindow().resize(w,h)
		#TODO:client area
		return True		

	def setOrientationPortrait( self ):
		if self.mainWindow.isFloating():
			pass #TODO
		getAKU().setOrientationPortrait()

	def setOrientationLandscape( self ):
		if self.mainWindow.isFloating():
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

		self.setFocus()

	def onLoad(self):
		self.setupMainWindow()

		self.canvas = MOAIGameViewCanvas( self.mainWindow ) 
		self.canvas.startRefreshTimer()
		self.paused = True
		self.mainWindow.setCentralWidget( self.canvas )
		
		self.canvas.module = self

		self.updateTimer = None
		self.mainWindow.setFocusPolicy(Qt.StrongFocus)
		
		signals.connect( 'app.command',    self.onAppCommand )
		signals.connect( 'app.activate',   self.onAppActivate )
		signals.connect( 'app.deactivate', self.onAppDeactivate )
		
		signals.connect( 'debug.enter',    self.onDebugEnter )
		signals.connect( 'debug.exit',     self.onDebugExit )
		signals.connect( 'debug.stop',     self.onDebugStop )
		
		signals.connect( 'game.pause',     self.onGamePause )
		signals.connect( 'game.resume',    self.onGameResume )
		signals.connect( 'moai.reset',     self.onMoaiReset )
		self.menu = self.addMenu( 'main/game', dict( label = 'Game' ) )
		self.menu.addChild([
				{'name':'run_game',   'label':'Run Game' },
				{'name':'pause_game', 'label':'Pause Game' },
				{'name':'stop_game',  'label':'Stop Game' },
				'----',
				{'name':'pause_on_leave','label':'Pause On Leave', 'type':'check', 'checked':self.getConfig('pause_on_leave')},
				'----',
				{'name':'reset_moai','label':'RESET MOAI', 'shortcut':'Ctrl+Shift+R'}
			], self)

		self.onMoaiReset() #moai is already ready...

	def onStart( self ):
		self.show()
		self.restoreWindowState(self.mainWindow)

	def onStop( self ):
		if self.updateTimer:
			self.updateTimer.stop()
		self.saveWindowState( self.mainWindow )

	def show( self ):
		self.mainWindow.show()

	def hide( self ):
		self.mainWindow.hide()

	def startScript( self, script = None ):
		logging.info('starting script')
		self.paused = False
		self.updateTimer = self.mainWindow.startTimer( fps, self.updateView)
		if not script:
			script = self.getApp().getConfig( 'start_script', 'game/script/main.lua' )
		if script:
			self.show()		
			self.restartScript( script )

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
		if path == self.runningScript:
			self.restartPending=True
			self.restartScript(path)

	def restartScript(self,src):
		runtime = self.getRuntime()
		if self.runningScript: runtime.reset()
		
		relpath = src #AssetLibrary.get().getRelPath(src)
		# src = os.path.abspath(src)
		self.runningScript=src

		runtime.changeRenderContext('game')	
		
		logging.info( 'running script:%s' % src )
		runtime.runScript( src )
		self.mainWindow.setWindowTitle( 'Game<%s>' % relpath )

		self.restartPending=False

	def onMoaiReset( self ):
		runtime = self.getRuntime()
		runtime.createRenderContext( 'game' )
		getAKU().setFuncOpenWindow(self.onOpenWindow)

		inputDevice = runtime.addDefaultInputDevice()
		self.canvas.setInputDevice(	inputDevice )
		jhook = self.getModule( 'joystick_hook' )
		if jhook:
			jhook.refreshJoysticks()
			jhook.setInputDevice( inputDevice )
		
	def onAppCommand(self, cmd, data=None, *args):
		if cmd=='exec':
			src = app.getProjectPath(data)
			if app.isDebugging():
				self.pendingScript=src
				self.restartPending=True #will load when debug ends
			else:
				signals.callAfter( self.restartScript, src )

	def onUnload(self):
		self.mainWindow.destroy()

	def onDebugEnter(self):
		self.paused=True
		self.getRuntime().pause()
		self.mainWindow.setFocusPolicy(Qt.NoFocus)

	def onDebugExit(self, cmd=None):
		self.paused=False
		self.getRuntime().resume()
		self.mainWindow.setFocusPolicy(Qt.StrongFocus)
		if self.pendingScript:
			script=self.pendingScript
			self.pendingScript=False
			self.restartScript(script)
		self.setFocus()
		
	def onDebugStop(self):
		self.paused=True

	def setFocus(self):
		# getModule('main').setFocus()
		self.mainWindow.show()
		self.mainWindow.raise_()
		self.mainWindow.setFocus()
		self.canvas.setFocus()
		self.canvas.activateWindow()
		self.setActiveWindow(self.mainWindow)

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
			self.setConfig( 'pause_on_leave', node.getValue())

		elif name=='reset_moai':
			#TODO: dont simply reset in debug
			# self.restartScript( self.runningScript )
			self.getRuntime().reset()

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
##----------------------------------------------------------------##


##----------------------------------------------------------------##
class QtMainWindow( MainWindow ):
	"""docstring for QtMainWindow"""
	def __init__(self, parent,*args):
		super(QtMainWindow, self).__init__(parent, *args)
	
	def closeEvent(self,event):
		if self.module.alive:
			self.hide()
			event.ignore()
		else:
			pass
