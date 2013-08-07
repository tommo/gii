import os.path
import time
import logging

from gii.core                import signals, app

from gii.moai.MOAIRuntime    import getAKU
from gii.moai.MOAICanvasBase import MOAICanvasBase

from PyQt4                   import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore            import Qt

from SceneEditor             import SceneEditorModule

##----------------------------------------------------------------##
class GamePreview( SceneEditorModule ):
	"""docstring for GamePreview"""
	def __init__(self):
		super(GamePreview, self).__init__()
		self.paused         = False
		self.waitActivate   = False
		self.viewWidth      = 0
		self.viewHeight     = 0
		self.pendingScript  = None

	def getName(self):
		return 'scene_preview'

	def getDependency(self):
		return [ 'qt', 'moai', 'scene_editor' ]

	def getRuntime(self):
		return self.getManager().affirmModule('moai')

	def tryResizeContainer(self, w,h):
		#TODO:client area
		return True		

	def setOrientationPortrait( self ):
		if self.window.isFloating():
			pass #TODO
		getAKU().setOrientationPortrait()

	def setOrientationLandscape( self ):
		if self.window.isFloating():
			pass #TODO
		getAKU().setOrientationLandscape()

	def onOpenWindow(self, title, w,h):
		#no argument accepted here, just use full window
		self.getRuntime().initGLContext()
		self.originalSize = (w,h)
		self.tryResizeContainer( *self.originalSize )

		size=self.canvas.size()
		w,h = size.width(),size.height()

		getAKU().setScreenSize(w,h)
		getAKU().setViewSize(w,h)

		self.setFocus()

	def onLoad(self):
		self.window = self.requestDocumentWindow(
			'GamePreview',
			title = 'Game Preview',
			)
		fps = 60
		self.canvas = GamePreviewCanvas( self.window ) 
		self.canvas.startRefreshTimer(fps)
		self.paused = True
		self.window.setCentralWidget( self.canvas )
		
		self.canvas.module = self

		self.updateTimer = None
		self.window.setFocusPolicy(Qt.StrongFocus)
		
		signals.connect( 'app.activate',   self.onAppActivate )
		signals.connect( 'app.deactivate', self.onAppDeactivate )
		
		signals.connect( 'debug.enter',    self.onDebugEnter )
		signals.connect( 'debug.exit',     self.onDebugExit )
		signals.connect( 'debug.stop',     self.onDebugStop )
		
		signals.connect( 'game.pause',     self.onGamePause )
		signals.connect( 'game.resume',    self.onGameResume )
		signals.connect( 'moai.reset',     self.onMoaiReset )
		
		self.menu = self.addMenu( 'main/preview', dict( label = 'Game' ) )

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
		self.restoreWindowState(self.window)

	def onStop( self ):
		if self.updateTimer:
			self.updateTimer.stop()
		self.saveWindowState( self.window )

	def show( self ):
		self.window.show()

	def hide( self ):
		self.window.hide()

	def refresh( self ):
		self.canvas.updateGL()

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
		before  = time.clock()
		runtime = self.getRuntime()
		runtime.setBufferSize(self.viewWidth,self.viewHeight)
		runtime.changeRenderContext('game')

		if runtime.renderAKU():
			used=time.clock()-before

	def onMoaiReset( self ):
		runtime = self.getRuntime()
		runtime.createRenderContext( 'game' )
		self.canvas.setInputDevice(
			runtime.addDefaultInputDevice()
			)
		getAKU().setFuncOpenWindow(self.onOpenWindow)
	
	def onUnload(self):
		self.window.destroy()

	def onDebugEnter(self):
		self.paused=True
		self.getRuntime().pause()
		self.window.setFocusPolicy(Qt.NoFocus)

	def onDebugExit(self, cmd=None):
		self.paused=False
		self.getRuntime().resume()
		self.window.setFocusPolicy(Qt.StrongFocus)
		if self.pendingScript:
			script = self.pendingScript
			self.pendingScript=False
			self.restartScript(script)
		self.setFocus()
		
	def onDebugStop(self):
		self.paused=True

	def setFocus(self):
		# getModule('main').setFocus()
		self.window.show()
		self.window.raise_()
		self.window.setFocus()
		self.canvas.setFocus()
		self.canvas.activateWindow()
		self.setActiveWindow(self.window)

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
class GamePreviewCanvas(MOAICanvasBase):
	def resizeGL(self, width, height):
		self.module.resizeView(width,height)
		self.updateGL()

	def onDraw(self):
		self.module.renderView()
		
##----------------------------------------------------------------##
GamePreview().register()
##----------------------------------------------------------------##
