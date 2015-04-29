import random
##----------------------------------------------------------------##
from gii.core        import app, signals
from gii.qt          import QtEditorModule

from gii.qt.IconCache                   import getIcon
from gii.qt.controls.GenericTreeWidget  import GenericTreeWidget
from gii.qt.dialogs                     import alertMessage
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
		self.addTool( 'animator_clips/add_clip',    label = 'add',    icon = 'add' )
		self.addTool( 'animator_clips/remove_clip', label = 'remove', icon = 'remove' )


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
		signals.connect( 'selection.changed', self.onSceneSelectionChanged )

		self.delegate = MOAILuaDelegate( self )
		self.delegate.load( _getModulePath( 'AnimatorView.lua' ) )

		self.widget.setOwner( self )

		#playback
		self.previewing = False
		self.widget.setEnabled( False )

		self.targetAnimator     = None
		self.targetClip         = None
		self.targetAnimatorData = None
		self.currentTrack       = None


	def onStart( self ):
		pass

	def setTargetAnimator( self, target ):
		if target == self.targetAnimator: return
		self.targetAnimator = target
		self.targetClip     = None
		self.delegate.callMethod( 'view', 'setTargetAnimator', target )
		self.targetAnimatorData = self.delegate.callMethod( 'view', 'getTargetAnimatorData' )
		self.widget.rebuild()
		if self.targetAnimator:
			self.widget.setEnabled( True )
		else:
			self.widget.setEnabled( False )
		clip = self.delegate.callMethod( 'view', 'getPreviousTargeClip', target )
		if clip:
			self.widget.treeClips.selectNode( clip )
		else:
			self.widget.treeClips.selectFirstItem()


	def setTargetClip( self, clip ):
		self.targetClip = clip
		self.delegate.callMethod( 'view', 'setTargetClip', clip )
		self.widget.rebuildTimeline()

	def setCurrentTrack( self, track ):
		self.currentTrack = track
		self.delegate.callMethod( 'view', 'setCurrentTrack', track )
		#TODO:update track toolbar
		
	def getClipList( self ):
		if self.targetAnimatorData:
			clipList = self.targetAnimatorData.clips
			return [ clip for clip in clipList.values()  ]
		else:
			return []

	def getTrackList( self ):
		if self.targetClip:
			trackList = self.targetClip.getTrackList( self.targetClip )
			return [ track for track in trackList.values()  ]
		else:
			return []

	def getClipRoot( self ):
		if self.targetClip:
			return self.targetClip.getRoot( self.targetClip )
		else:
			return None

	def onSelectionChanged( self, selection, context = None ):
		if context == 'clip':
			if selection:
				clip = selection[0]
			else:
				clip = None
			self.setTargetClip( clip )
		elif context == 'track':
			if selection:
				track = selection[0]
			else:
				track = None
			self.setCurrentTrack( track )

	def onSceneSelectionChanged( self, selection, key ):
		if key != 'scene': return
		#find animator component
		target = self.delegate.callMethod( 'view', 'findTargetAnimator' )
		self.setTargetAnimator( target )
		
	def clearPreviewState( self ):
		if self.previewing: return
		self.delegate.callMethod( 'view', 'clearStateData' )
	
	def addKeyForField( self, target, fieldId ):
		if not self.targetAnimator:
			alertMessage( 'No Animator', 'No Animator found in current entity scope', 'question' )
			return False

		if not self.targetClip:
			alertMessage( 'No Clip', 'You need to select a Clip first', 'question' )
			return False

		key = self.delegate.callMethod( 'view', 'addKeyForField', target, fieldId )
		if key:
			self.widget.addKey( key, True )

	def addKeyForEvent( self, target, eventId ):
		pass

	#preview
	# def startPreview( self ):
	# 	self.delegate.makeCurrent()
	# 	if self.delegate.callMethod( 'view', 'startPreview' ):
	# 		self.timeline.setCursorDraggable( False )
	# 		self.previewing = True
	# 		self.delegate.startUpdateTimer( 60 )
	# 		self.delegate.setStyleSheet('border-bottom: 1px solid rgb(0, 255, 0);')

	# def stopPreview( self ):		
	# 	self.delegate.makeCurrent()
	# 	self.delegate.callMethod( 'view', 'stopPreview' )
	# 	self.previewing = False
	# 	self.delegate.stopUpdateTimer()
	# 	self.delegate.setStyleSheet('border-bottom: none ')
	# 	self.timeline.setCursorDraggable( True )

	# def togglePreview( self ):
	# 	if self.previewing:
	# 		self.stopPreview()
	# 	else:
	# 		self.startPreview()

	def onKeyRemoving( self, key ):
		if self.delegate.callMethod( 'view', 'removeKey', key ) != False:
			return True

	def onTimelineKeyChanged( self, key, pos, length ):
		self.delegate.callMethod( 'view', 'updateTimelineKey', key, pos, length )

	def onCurveKeyChanged( self, key ):
		pass

	def onTool( self, tool ):
		name = tool.name
		if name == 'add_clip':
			clip = self.delegate.callMethod( 'view', 'addClip' )
			if clip:
				self.widget.addClip( clip, True )
			
		elif name == 'remove_clip':
			for clip in self.widget.treeClips.getSelection():
				self.delegate.callMethod( 'view', 'removeClip', clip )
				self.widget.removeClip( clip )

		elif name == 'add_group':
			group = self.delegate.callMethod( 'view', 'addTrackGroup' )
			if group:
				self.widget.addTrack( group )

		elif name == 'remove_track':
			for track in self.widget.treeTracks.getSelection():
				self.delegate.callMethod( 'view', 'removeTrack', track )
				self.widget.removeTrack( track )
