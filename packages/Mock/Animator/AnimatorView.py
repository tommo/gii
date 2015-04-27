import random
##----------------------------------------------------------------##
from gii.core        import app, signals
from gii.qt          import QtEditorModule

from gii.qt.IconCache                   import getIcon
from gii.qt.controls.GenericTreeWidget  import GenericTreeWidget
from gii.moai.MOAIRuntime import MOAILuaDelegate
from gii.SceneEditor      import SceneEditorModule, getSceneSelectionManager
from gii.qt.helpers       import addWidgetWithLayout, QColorF, unpackQColor

##----------------------------------------------------------------##
from PyQt4           import QtCore, QtGui, uic
from PyQt4.QtCore    import Qt

##----------------------------------------------------------------##
from mock import _MOCK, isMockInstance
##----------------------------------------------------------------##
from AnimatorWidget import AnimatorWidget
##----------------------------------------------------------------##

def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

def _fixDuplicatedName( names, name, id = None ):
	if id:
		testName = name + '_%d' % id
	else:
		id = 0
		testName = name
	#find duplicated name
	if testName in names:
		return _fixDuplicatedName( names, name, id + 1)
	else:
		return testName


##----------------------------------------------------------------##
class AnimatorView( SceneEditorModule ):
	name = 'animator'
	dependency = [ 'scene_editor' ]

	def onLoad( self ):
		#UI
		self.windowTitle = 'Animator'
		self.window = self.requestDockWindow( 'AnimatorView',
			title     = 'Animator',
			size      = (120,120),
			minSize   = (120,120),
			dock      = 'bottom'
			)
		
		self.widget = AnimatorWidget()
		self.window.addWidget( self.widget )
		self.toolbarClips = self.addToolBar( 'animator_clips', self.widget.toolbarClips )
		self.toolbarPlay  = self.addToolBar( 'animator_play',  self.widget.toolbarPlay )
		self.toolbarTrack = self.addToolBar( 'animator_track', self.widget.toolbarTrack )
		# self.toolbarEdit  = self.addToolBar( 'animator_play',  self.widget.toolbarEdit )

		# addWidgetWithLaytut( toolbar,
		# 	self.widget.containerEditTool )
		self.addTool( 'animator_clips/add',    label = 'add',    icon = 'add' )
		self.addTool( 'animator_clips/remove', label = 'remove', icon = 'remove' )


		self.addTool( 'animator_play/to_start',    label = 'to start',  icon = 'previous' )
		self.addTool( 'animator_play/play',    label = 'play',    icon = 'play',  type = 'check' )
		self.addTool( 'animator_play/stop',    label = 'stop',    icon = 'stop' )
		self.addTool( 'animator_play/to_end',    label = 'to end',    icon = 'next' )
		self.addTool( 'animator_play/----' )
		self.addTool( 'animator_play/toggle_repeat',  label = 'toggle repeat',  icon = 'repeat', type = 'check' )
		
		#SIGNALS
		self.addTool( 'animator_track/add_track',    label = 'add',    icon = 'add' )
		self.addTool( 'animator_track/remove_track', label = 'remove', icon = 'remove' )
		self.addTool( 'animator_track/add_group',    label = 'add group',    icon = 'add_folder' )

		#
		self.delegate = MOAILuaDelegate( self )
		self.delegate.load( _getModulePath( 'AnimatorView.lua' ) )

		self.editTarget = None
		self.widget.setOwner( self )

		#playback
		self.previewing = False


	def onStart( self ):
		target = self.delegate.callMethod( 'view', 'setupTestData' )
		self.setEditTarget( target )

	def setEditTarget( self, target ):
		self.editTarget = target
		self.delegate.callMethod( 'view', 'setEditTarget', target )
		self.widget.rebuild()

	def onSelectionChanged( self, selection, context = None ):
		pass

	def getClipList( self ):
		return []

	def getTrackList( self ):
		if self.editTarget:
			trackList = self.editTarget.getTrackList( self.editTarget )
			return [ track for track in trackList.values()  ]
		else:
			return []

	def getClipRoot( self ):
		if self.editTarget:
			return self.editTarget.getRoot( self.editTarget )
		else:
			return None

	def clearPreviewState( self ):
		if self.previewing: return
		self.canvas.callMethod( 'view', 'clearStateData' )
	
	#preview
	def startPreview( self ):
		self.canvas.makeCurrent()
		if self.canvas.callMethod( 'view', 'startPreview' ):
			self.timeline.setCursorDraggable( False )
			self.previewing = True
			self.canvas.startUpdateTimer( 60 )
			self.canvas.setStyleSheet('border-bottom: 1px solid rgb(0, 255, 0);')

	def stopPreview( self ):		
		self.canvas.makeCurrent()
		self.canvas.callMethod( 'view', 'stopPreview' )
		self.previewing = False
		self.canvas.stopUpdateTimer()
		self.canvas.setStyleSheet('border-bottom: none ')
		self.timeline.setCursorDraggable( True )

	def togglePreview( self ):
		if self.previewing:
			self.stopPreview()
		else:
			self.startPreview()

	def onKeyRemoving( self, key ):
		if self.delegate.callMethod( 'view', 'removeKey', key ) != False:
			return True

	def onTimelineKeyChanged( self, key, pos, length ):
		self.delegate.callMethod( 'view', 'updateTimelineKey', key, pos, length )

	def onCurveKeyChanged( self, key ):
		pass

	def onTool( self, tool ):
		name = tool.name
		if name == 'add':
			layer = self.delegate.callMethod( 'view', 'addLayer' )
			
		elif name == 'remove':
			for l in self.tree.getSelection():
				self.delegate.callMethod( 'view', 'removeLayer', l )
	
