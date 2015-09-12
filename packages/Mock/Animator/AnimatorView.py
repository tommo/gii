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
	dependency = [ 'scene_editor', 'mock' ]

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

		signals.connect( 'scene.save', self.preSceneSave )
		signals.connect( 'scene.saved', self.postSceneSave )

		# addWidgetWithLaytut( toolbar,
		# 	self.widget.containerEditTool )
		self.addTool( 'animator_clips/add_clip',    label = 'add',    icon = 'add' )
		self.addTool( 'animator_clips/remove_clip', label = 'remove', icon = 'remove' )
		self.addTool( 'animator_clips/clone_clip', label = 'clone', icon = 'clone' )


		self.addTool( 'animator_play/goto_start', label = 'to start',  icon = 'rewind' )
		# self.addTool( 'animator_play/prev_key',   label = 'prev key',      icon = 'previous' )
		self.addTool( 'animator_play/stop',       label = 'stop',      icon = 'stop' )
		self.addTool( 'animator_play/play',       label = 'play',      icon = 'play',  type = 'check' )
		# self.addTool( 'animator_play/next_key',   label = 'next key',      icon = 'next' )
		self.addTool( 'animator_play/goto_end',   label = 'to end',    icon = 'fast_forward' )
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

		self.previewing  = False
		self.previewLoop = False
		self.previewTime = 0.0
		self.previewStep = 1.0/60.0

		self.previewTimer  = QtCore.QTimer( self.widget )
		self.previewTimer.setInterval( 1000.0/60 )
		self.previewTimer.stop()

		self.previewTimer.timeout.connect( self.onPreviewTimer )


	def onStart( self ):
		pass

	def setTargetAnimator( self, target ):
		self.saveAnimatorData()
		if target == self.targetAnimator: return
		if self.previewing:
			self.stopPreview()
		self.targetAnimator = target
		self.targetClip     = None
		self.delegate.callMethod( 'view', 'setTargetAnimator', target )
		self.targetAnimatorData = self.delegate.callMethod( 'view', 'getTargetAnimatorData' )
		self.widget.rebuild()
		if self.targetAnimator:
			self.widget.setEnabled( True )
			signals.emit( 'animator.start' )
		else:
			self.widget.setEnabled( False )
			signals.emit( 'animator.stop' )
			
		path = self.delegate.callMethod( 'view', 'getTargetAnimatorDataPath' )
		if path:
			self.window.setWindowTitle( 'Animator - %s' % path )
		else:
			self.window.setWindowTitle( 'Animator' )
		clip = self.delegate.callMethod( 'view', 'getPreviousTargeClip', target )
		self.enableTool( 'animator_play' , False )
		self.enableTool( 'animator_track', False )
		if clip:
			self.widget.treeClips.selectNode( clip )
		else:
			self.widget.treeClips.selectFirstItem()
		self.applyTime( 0, True )


	def setTargetClip( self, clip ):
		wasPreviewing = self.previewing
		if self.previewing:
			self.stopPreview()

		self.targetClip = clip
		self.delegate.callMethod( 'view', 'setTargetClip', clip )
		self.widget.rebuildTimeline()
		self.enableTool( 'animator_play' , bool( clip ) )
		self.enableTool( 'animator_track', bool( clip ) )
		self.applyTime( 0, True )
		if wasPreviewing:
			self.startPreview()
	
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

	def addClip( self ):
		if not self.targetAnimator: return
		clip = self.delegate.callMethod( 'view', 'addClip' )
		if clip:
			self.widget.addClip( clip, True )
		return clip

	def cloneClip( self ):
		if not self.targetClip: return
		clip = self.delegate.callMethod( 'view', 'cloneClip', self.targetClip )
		if clip:
			self.widget.addClip( clip, True )
		return clip

	def onObjectEdited( self, obj ):
		if self.targetClip:
			self.delegate.callMethod( 'view', 'clearPreviewState' )
			self.delegate.callMethod( 'view', 'markClipDirty' )

	def onSceneSelectionChanged( self, selection, key ):
		if key != 'scene': return
		#find animator component
		target = self.delegate.callMethod( 'view', 'findTargetAnimator' )
		self.setTargetAnimator( target )

	def addKeyForField( self, target, fieldId ):
		if not self.targetAnimator:
			alertMessage( 'No Animator', 'No Animator found in current entity scope', 'question' )
			return False

		if not self.targetClip:
			self.addClip()
			# alertMessage( 'No Clip', 'You need to select a Clip first', 'question' )
			# return False
		keys = self.delegate.callMethod( 'view', 'addKeyForField', target, fieldId )
		if keys:
			for key in keys.values():
				self.widget.addKey( key, True )

	def addKeyForEvent( self, target, eventId ):
		pass

	def addCustomAnimatorTrack( self, target, trackClasId ):
		if not self.targetAnimator:
			alertMessage( 'No Animator', 'No Animator found in current entity scope', 'question' )
			return False
			
		track = self.delegate.callMethod( 'view', 'addCustomAnimatorTrack', target, trackClasId )
		if track:
			self.widget.addTrack( track )

	def addKeyForSelectedTracks( self ):
		selectedTracks = self.widget.getTrackSelection()
		for track in selectedTracks:
			keys = self.delegate.callMethod( 'view', 'addKeyForSelectedTrack', track )
			if keys:
				for key in keys.values():
					self.widget.addKey( key, True )

	def onKeyRemoving( self, key ):
		if self.delegate.callMethod( 'view', 'removeKey', key ) != False:
			return True

	def onTimelineKeyChanged( self, key, pos, length ):
		self.delegate.callMethod( 'view', 'updateTimelineKey', key, pos, length )

	def renameTrack( self, track, name ):
		self.delegate.callMethod( 'view', 'renameTrack', track, name )

	def renameClip( self, clip, name ):
		self.delegate.callMethod( 'view', 'renameClip', clip, name )

	def onCurveKeyChanged( self, key ):
		pass

	def onTool( self, tool ):
		name = tool.name
		if name == 'add_clip':
			self.addClip()			
			
		elif name == 'remove_clip':
			for clip in self.widget.treeClips.getSelection():
				self.delegate.callMethod( 'view', 'removeClip', clip )
				self.widget.removeClip( clip )

		if name == 'clone_clip':
			self.cloneClip()			

		elif name == 'add_group':
			group = self.delegate.callMethod( 'view', 'addTrackGroup' )
			if group:
				self.widget.addTrack( group, True )

		elif name == 'remove_track':
			for track in self.widget.treeTracks.getSelection():
				self.delegate.callMethod( 'view', 'removeTrack', track )
				self.widget.removeTrack( track )
		#preview
		elif name == 'goto_start':
			self.gotoStart()
		elif name == 'goto_end':
			self.gotoEnd()
		elif name == 'play':
			if tool.getValue():
				self.startPreview()
			else:
				self.stopPreview( False )
		elif name == 'stop':
			self.stopPreview( True )
		elif name == 'toggle_repeat':
			self.delegate.callMethod( 'view', 'togglePreviewRepeat', tool.getValue() )

	def onTimelineEditTool( self, toolName ):
		if toolName == 'add_key':
			self.addKeyForSelectedTracks()

		elif toolName == 'remove_key':
			pass

		elif toolName == 'clone_key':
			pass

		elif toolName == 'curve_mode_linear':
			pass

		elif toolName == 'curve_mode_constant':
			pass

		elif toolName == 'curve_mode_bezier':
			pass

		elif toolName == 'curve_mode_bezier_s':
			pass


	def getActiveSceneView( self ):
		return self.getModule( 'scene_view' )

	#preview
	def startPreview( self ):
		self.saveAnimatorData()
		if self.delegate.callMethod( 'view', 'startPreview', self.previewTime ):
			self.widget.setCursorMovable( False )
			self.previewing = True
			self.findTool( 'animator_play/play' ).setValue( True )
			self.previewTimer.start()
			
	def stopPreview( self, rewind = False ):		
		if self.previewing:
			self.delegate.callMethod( 'view', 'stopPreview' )
			self.widget.setCursorMovable( True )
			self.previewing = False
			self.findTool( 'animator_play/play' ).setValue( False )
			self.previewTimer.stop()
			signals.emit( 'entity.modified',  None , '' )
		if rewind:
			self.gotoStart()

	def onPreviewTimer( self ):
		playing, currentTime = self.delegate.callMethod( 'view', 'doPreviewStep' )
		self.previewTime = currentTime
		self.getActiveSceneView().forceUpdate()
		self.widget.setCursorPos( self.previewTime )
		if not playing:
			self.stopPreview()
		# signals.emit( 'entity.modified',  None , '' )

	def gotoStart( self ):
		if self.previewing:
			self.delegate.callMethod( 'view', 'applyTime', 0 )
		else:
			self.widget.setCursorPos( 0, True )

	def gotoEnd( self ):
		if self.previewing:
			self.delegate.callMethod( 'view', 'applyTime', 10 )
		else:
			self.widget.setCursorPos( 10, True )

	def applyTime( self, t, syncCursor = False ):
		self.previewTime = self.delegate.callMethod( 'view', 'applyTime', t )
		self.getActiveSceneView().forceUpdate()
		signals.emit( 'entity.modified',  None , '' )
		if syncCursor:
			self.widget.setCursorPos( t )

	def saveAnimatorData( self ):
		if not self.targetAnimator:
			return
		self.delegate.callMethod( 'view', 'saveData' )

	def preSceneSave( self ):
		if self.targetAnimator:
			self.delegate.callMethod( 'view', 'restoreEntityState' )

	def postSceneSave( self ):
		if self.targetAnimator:
			self.applyTime( self.previewTime )

