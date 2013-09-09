import os.path
import time
import logging

from gii.core                import signals, app, RemoteCommand

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
		logging.info('opening MOAI window: %s @ (%d,%d)' % ( str(title), w, h ) )
		#no argument accepted here, just use full window
		# self.getRuntime().initGLContext()
		from gii.qt.controls.GLWidget import GLWidget
		GLWidget.getSharedWidget().makeCurrent()

		self.originalSize = (w,h)
		self.tryResizeContainer( *self.originalSize )

		size=self.canvas.size()
		w,h = size.width(),size.height()

		getAKU().setScreenSize(w,h)
		getAKU().setViewSize(w,h)


	def onLoad(self):
		self.window = self.requestDockWindow(
			'GamePreview',
			title = 'Game Preview',
			dock  = 'right'
			)

		# self.window.setStayOnTop( True )

		self.canvas = self.window.addWidget( GamePreviewCanvas( self.window )  )
		self.canvas.startRefreshTimer()
		self.paused = None
		
		tool = self.window.addWidget( QtGui.QToolBar( self.window ), expanding = False )
		self.qtool = tool
		self.toolbar = self.addToolBar( 'game_preview', tool )

		self.canvas.module = self

		self.updateTimer = None
		self.window.setFocusPolicy(Qt.StrongFocus)
		
		signals.connect( 'app.activate',   self.onAppActivate )
		signals.connect( 'app.deactivate', self.onAppDeactivate )
		
		signals.connect( 'debug.enter',    self.onDebugEnter )
		signals.connect( 'debug.exit',     self.onDebugExit )
		signals.connect( 'debug.stop',     self.onDebugStop )
		
		# signals.connect( 'game.pause',     self.onGamePause )
		# signals.connect( 'game.resume',    self.onGameResume )
		signals.connect( 'moai.reset',     self.onMoaiReset )
		
		self.menu = self.addMenu( 'main/preview', dict( label = 'Game' ) )

		self.menu.addChild([
				{'name':'start_game',    'label':'Resume Game','shortcut':'meta+]' },
				{'name':'pause_game',  'label':'Pause Game', 'shortcut':'meta+shit+]' },
				{'name':'stop_game',   'label':'Stop Game',  'shortcut':'meta+[' },
				'----',
				{'name':'pause_on_leave','label':'Pause On Leave', 'type':'check', 'checked':self.getConfig('pause_on_leave')},
				'----',
				{'name':'reset_moai','label':'RESET MOAI', 'shortcut':'Ctrl+Shift+R'}
			], self)

		self.addTool( 'game_preview/stay_on_top', label = 'Stay Top' )
		self.onMoaiReset()

		self.enableMenu( 'main/preview/pause_game',  False )
		self.enableMenu( 'main/preview/stop_game',   False )

	def onStart( self ):
		pass

	def onStop( self ):
		if self.updateTimer:
			self.updateTimer.stop()

	def show( self ):
		self.window.show()

	def hide( self ):
		self.window.hide()

	def refresh( self ):
		self.canvas.updateGL()

	def updateView(self):
		if self.paused: return
		runtime = self.getRuntime()

		runtime.setBufferSize( self.viewWidth, self.viewHeight )
		runtime.changeRenderContext( 'game', self.viewWidth, self.viewHeight )
		
		if runtime.updateAKU():
			self.canvas.forceUpdateGL()

	def resizeView(self, w,h):
		self.viewWidth  = w
		self.viewHeight = h
		getAKU().setScreenSize(w,h)
		getAKU().setViewSize(w,h)		

	def renderView(self):
		runtime = self.getRuntime()
		runtime.setBufferSize( self.viewWidth, self.viewHeight )
		runtime.changeRenderContext( 'game', self.viewWidth, self.viewHeight )
		runtime.renderAKU()		

	def onMoaiReset( self ):
		runtime = self.getRuntime()
		runtime.createRenderContext( 'game' )
		runtime.addDefaultInputDevice( 'device' )
		# getAKU().setFuncOpenWindow( self.onOpenWindow )
	
	def onDebugEnter(self):
		self.paused = True
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

	def onSetFocus(self):
		self.window.show()
		self.window.raise_()
		self.window.setFocus()
		self.canvas.setFocus()
		self.canvas.activateWindow()
		self.setActiveWindow( self.window )

	def startPreview( self ):
		if self.paused == False: return
		runtime = self.getRuntime()
		self.canvas.setInputDevice( runtime.getInputDevice('device') )

		self.enableMenu( 'main/preview/pause_game', True )
		self.enableMenu( 'main/preview/stop_game',  True )
		self.enableMenu( 'main/preview/start_game', False )

		if self.paused: #resume
			logging.info('resume game preview')
			signals.emitNow( 'preview.resume' )

		elif self.paused is None: #start
			logging.info('start game preview')
			signals.emitNow( 'preview.start' )
			signals.emitNow( 'preview.resume' )
			self.updateTimer = self.window.startTimer( 60, self.updateView )

		self.window.setWindowTitle( 'Game Preview [ RUNNING ]')
		self.qtool.setStyleSheet('QToolBar{ border-top: 1px solid rgb(0, 255, 0); }')
		self.paused = False
		runtime.resume()
		self.setFocus()

	def stopPreview( self ):
		if self.paused is None: return
		logging.info('stop game preview')
		self.canvas.setInputDevice( None )

		signals.emitNow( 'preview.stop' )
		self.updateTimer.stop()
		self.enableMenu( 'main/preview/stop_game',  False )
		self.enableMenu( 'main/preview/pause_game', False )
		self.enableMenu( 'main/preview/start_game', True )
		
		self.window.setWindowTitle( 'Game Preview' )
		self.qtool.setStyleSheet('QToolBar{ border-top: none; }')

		self.paused = None
		self.updateTimer = None

	# def onUpdate( self ):
	# 	if self.paused != False: return
	# 	self.updateView()

	def pausePreview( self ):
		if self.paused: return
		self.canvas.setInputDevice( None )
		signals.emitNow( 'preview.pause' )
		logging.info('pause game preview')
		self.enableMenu( 'main/preview/start_game', True )
		self.enableMenu( 'main/preview/pause_game',  False )
		
		self.window.setWindowTitle( 'Game Preview[ Paused ]')
		self.qtool.setStyleSheet('QToolBar{ border-top: 1px solid rgb(255, 0, 0); }')

		self.paused = True
		self.getRuntime().pause()

	def onAppActivate(self):
		if self.waitActivate:
			self.waitActivate=False
			self.getRuntime().resume()

	def onAppDeactivate(self):
		if self.getConfig('pause_on_leave',False):
			self.waitActivate=True
			self.getRuntime().pause()

	def onMenu(self, node):
		name = node.name
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

		elif name == 'start_game':
			self.startPreview()

		elif name == 'stop_game':
			self.stopPreview()

		elif name == 'pause_game':
			self.pausePreview()

			

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

class RemoteCommandPreviewStart( RemoteCommand ):
	name = 'preview_start'
	def run( self, *args ):
		preview = app.getModule('scene_preview')
		preview.startPreview()
		
class RemoteCommandPreviewStart( RemoteCommand ):
	name = 'preview_stop'
	def run( self, *args ):
		preview = app.getModule('scene_preview')
		preview.stopPreview()
		