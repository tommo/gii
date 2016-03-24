import random
import time

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
PREVIEW_SPEED_OPTIONS = [
		( '1/10', 0.1 ),
		( '1/5',  0.2 ),
		( '1/3',  0.33 ),
		( '1/2',  0.5 ),
		( '1x',   1.0 ),
		( '1.5x', 1.5 ),
		( '2x',   2.0 ),
		( '4x',   4.0 ),
		( '10x',  10.0 ),
]

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
		self.toolbarTarget = self.addToolBar( 'animator_target', self.widget.toolbarTarget )
		self.toolbarClips  = self.addToolBar( 'animator_clips', self.widget.toolbarClips )
		self.toolbarPlay   = self.addToolBar( 'animator_play',  self.widget.toolbarPlay )
		self.toolbarTrack  = self.addToolBar( 'animator_track', self.widget.toolbarTrack )
		# self.toolbarEdit  = self.addToolBar( 'animator_play',  self.widget.toolbarEdit )

		signals.connect( 'scene.close', self.onSceneClose )
		signals.connect( 'scene.save', self.preSceneSave )
		signals.connect( 'scene.saved', self.postSceneSave )

		# addWidgetWithLaytut( toolbar,
		# 	self.widget.containerEditTool )
		self.addTool( 'animator_target/change_context', label = 'Change Context', icon = 'in' )
		self.addTool( 'animator_target/save_data', label = 'Save Data', icon = 'save' )

		self.addTool( 'animator_clips/add_clip_group',   label = 'add group',    icon = 'add_folder' )
		self.addTool( 'animator_clips/add_clip',    label = 'add',    icon = 'add' )
		self.addTool( 'animator_clips/remove_clip', label = 'remove', icon = 'remove' )
		self.addTool( 'animator_clips/clone_clip', label = 'clone', icon = 'clone' )


		self.addTool( 'animator_play/goto_start', label = 'to start',  icon = 'rewind' )
		# self.addTool( 'animator_play/prev_key',   label = 'prev key',      icon = 'previous' )
		self.addTool( 'animator_play/stop',       label = 'stop',      icon = 'stop' )
		self.addTool( 'animator_play/play',       label = 'play',      icon = 'play',  type = 'check' )
		# self.addTool( 'animator_play/next_key',   label = 'next key',      icon = 'next' )
		self.addTool( 'animator_play/goto_end',   label = 'to end',    icon = 'fast_forward' )
		self.addTool( 'animator_play/toggle_repeat',  label = 'toggle repeat',  icon = 'repeat', type = 'check' )
		self.comboPreviewSpeed = QtGui.QComboBox()
		self.comboPreviewSpeed.addItems([ e[0] for e in PREVIEW_SPEED_OPTIONS ] )			
		self.comboPreviewSpeed.setCurrentIndex( 4 ) #1x
		self.comboPreviewSpeed.currentIndexChanged.connect( self.onPreviewSpeedChange )
		self.addTool( 'animator_play/preview_speed', widget = self.comboPreviewSpeed )
		
		#SIGNALS
		self.addTool( 'animator_track/locate_target', label = 'locate', icon = 'find' )
		self.addTool( 'animator_track/----' )
		self.addTool( 'animator_track/add_track_group',    label = 'add group',    icon = 'add_folder' )
		self.addTool( 'animator_track/add_track',    label = 'add',    icon = 'add' )
		self.addTool( 'animator_track/remove_track', label = 'remove', icon = 'remove' )

		#
		signals.connect( 'selection.changed', self.onSceneSelectionChanged )

		self.delegate = MOAILuaDelegate( self )
		self.delegate.load( _getModulePath( 'AnimatorView.lua' ) )

		self.widget.setOwner( self )

		#playback
		self.previewing = False
		self.setEditing( False )

		self.targetAnimator     = None
		self.targetClip         = None
		self.targetAnimatorData = None
		self.currentTrack       = None

		self.previewing  = False
		self.previewLoop = False
		self.previewTime = 0.0
		self.previewStep = 1.0/60.0

		self.previewTimer  = QtCore.QTimer( self.widget )
		self.previewTimer.setInterval( 1000.0/65 )
		self.previewTimer.stop()

		self.previewTimer.timeout.connect( self.onPreviewTimer )

	def onStart( self ):
		pass

	def setEditing( self, editing ):
		self.widget.timeline.setEnabled( editing )
		self.widget.treeTracks.setEnabled( editing )
		self.findTool( 'animator_play'  ).setEnabled( editing )
		self.findTool( 'animator_track' ).setEnabled( editing )
		self.findTool( 'animator_clips/add_clip_group').setEnabled( editing )
		self.findTool( 'animator_clips/add_clip'      ).setEnabled( editing )
		self.findTool( 'animator_clips/remove_clip'   ).setEnabled( editing )
		self.findTool( 'animator_clips/clone_clip'    ).setEnabled( editing )

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
			self.setEditing( True )
			signals.emit( 'animator.start' )
		else:
			self.setEditing( False )
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

	def setCurrentTrack( self, track ):
		self.currentTrack = track
		self.delegate.callMethod( 'view', 'setCurrentTrack', track )

	def getTargetClipLength( self ):
		return self.delegate.callMethod( 'view', 'getTargetClipLength' )

	def getClipList( self ):
		if self.targetAnimatorData:
			clipList = self.targetAnimatorData.clips
			return [ clip for clip in clipList.values()  ]
		else:
			return []

	def getRootClipGroup( self ):
		if self.targetAnimatorData:
			return self.targetAnimatorData.getRootGroup( self.targetAnimatorData )

	def getTrackList( self ):
		if self.targetClip:
			trackList = self.targetClip.getTrackList( self.targetClip )
			return [ track for track in trackList.values()  ]
		else:
			return []

	def getMarkerList( self ):
		if self.targetClip:
			markerList = self.targetClip.getMarkerList( self.targetClip )
			return [ track for track in markerList.values()  ]
		else:
			return []

	def getClipRoot( self ):
		if self.targetClip:
			return self.targetClip.getRoot( self.targetClip )
		else:
			return None

	def addClip( self ):
		if not self.targetAnimatorData: return
		targetGroup = self.widget.getCurrentClipGroup()
		cmd = self.doCommand( 'scene_editor/animator_add_clip',
			animator_data = self.targetAnimatorData,
			parent_group  = targetGroup
		  )
		clip = cmd.getResult()
		if clip:
			self.widget.addClip( clip, True )
		return clip

	def addClipGroup( self ):
		if not self.targetAnimatorData: return
		targetGroup = self.widget.getCurrentClipGroup()
		cmd = self.doCommand( 'scene_editor/animator_add_clip_group',
			animator_data = self.targetAnimatorData,
			parent_group  = targetGroup
		  )
		group = cmd.getResult()
		if group:
			self.widget.addClip( group, True )
		return group

	def removeClipNode( self ):
		for clip in self.widget.treeClips.getSelection():
			if self.doCommand( 'scene_editor/animator_remove_clip_node',
				animator_data = self.targetAnimatorData,
				target_node   = clip
			):
				self.widget.removeClip( clip )

	def cloneClipNode( self ):
		if not self.targetClip: return
		result = []
		for clip in self.widget.treeClips.getSelection():
			cmd = self.doCommand( 'scene_editor/animator_clone_clip_node',
				animator_data = self.targetAnimatorData,
				target_node   = clip
			)
			if cmd:
				cloned = cmd.getResult()
				self.widget.addClip( cloned )
				result.append( cloned )
		return result

	def onObjectEdited( self, obj ):
		if self.targetClip:
			self.delegate.callMethod( 'view', 'clearPreviewState' )
			self.delegate.callMethod( 'view', 'markClipDirty' )

	def onSceneSelectionChanged( self, selection, key ):
		if key != 'scene': return
		#find animator component
		# self.findTargetAnimator()

	def findTargetAnimator( self ):
		target = self.delegate.callMethod( 'view', 'findTargetAnimator' )
		self.setTargetAnimator( target )
		return target

	def checkTargetAnimator( self ):
		if not self.targetAnimator:
			alertMessage( 'No Animator', 'No Animator Selected', 'question' )
			return False
		return True

	def addMarker( self ):
		if not self.targetClip: return
		cmd = self.doCommand( 'scene_editor/animator_add_marker' ,
				target_clip = self.targetClip,
				target_pos  = self.widget.getCursorPos()
			)
		if cmd:
			marker = cmd.getResult()
			self.widget.addMarker( marker )

	def addKeyForField( self, target, fieldId ):
		if not self.checkTargetAnimator(): return 

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
		if not self.checkTargetAnimator(): return
			
		track = self.delegate.callMethod( 'view', 'addCustomAnimatorTrack', target, trackClasId )
		if track:
			self.widget.addTrack( track )

	def addKeyForSelectedTracks( self ):
		#TODO: command
		selectedTracks = self.widget.getTrackSelection()
		for track in selectedTracks:
			keys = self.delegate.callMethod( 'view', 'addKeyForSelectedTrack', track )
			if keys:
				for key in keys.values():
					self.widget.addKey( key, True )

	def removeSelectedKeys( self ):
		#TODO: command
		selectedKeys = self.widget.getKeySelection()
		for key in selectedKeys:
			self.widget.removeKey( key )

	def cloneSelectedKeys( self ):
		#TODO: command
		selectedKeys = self.widget.getKeySelection()
		cloned = []
		for key in selectedKeys:
			clonedKey = self.delegate.callMethod( 'view', 'cloneKey', key )
			if clonedKey:
				cloned.append( clonedKey )

		for clonedKey in cloned:
			self.widget.addKey( clonedKey, False )

	def onKeyRemoving( self, key ):
		if self.delegate.callMethod( 'view', 'removeKey', key ) != False:
			return True

	def onMarkerRemoving( self, marker ):
		if self.delegate.callMethod( 'view', 'removeMarker', marker ) != False:
			return True

	def onClipLengthChanging( self, t1 ):
		if self.delegate.callMethod( 'view', 'setTargetClipLength', t1 ) != False:
			return True

	def onTimelineKeyChanged( self, key, pos, length ):
		self.delegate.callMethod( 'view', 'updateTimelineKey', key, pos, length )

	def onTimelineKeyCurveValueChanged( self, key, value ):
		self.delegate.callMethod( 'view', 'updateTimelineKeyCurveValue', key, value )

	def onTimelineKeyTweenModeChanged( self, key, mode ):
		self.delegate.callMethod( 'view', 'updateTimelineKeyTweenMode', key, mode )

	def onTimelineKeyBezierPointChanged( self, key, bpx0, bpy0, bpx1, bpy1 ):
		self.delegate.callMethod( 'view', 'updateTimelineKeyBezierPoint', key, bpx0, bpy0, bpx1, bpy1 )

	def onTimelineMarkerChanged( self, marker, pos ):
		self.delegate.callMethod( 'view', 'updateTimelineMarker', marker, pos )

	def toggleTrackActive( self, track ):
		#TODO: command
		# self.module.doCommand( 'scene_editor/toggle_entity_visibility', target = node )
		self.delegate.callMethod( 'view', 'toggleTrackActive', track )


	def renameTrack( self, track, name ):
		self.delegate.callMethod( 'view', 'renameTrack', track, name )

	def renameClip( self, clip, name ):
		self.delegate.callMethod( 'view', 'renameClip', clip, name )

	def onTool( self, tool ):
		name = tool.name
		if name == 'change_context':
			target0 = self.targetAnimator
			target1 = self.findTargetAnimator()
			if ( not target0 ) and ( not target1 ):
				alertMessage( 'No Animator', 'No Animator found in selected entity scope', 'question' )
				
		elif name == 'save_data':
			self.saveAnimatorData()

		elif name == 'add_clip':
			if self.checkTargetAnimator():
				self.addClip()

		elif name == 'add_clip_group':
			if self.checkTargetAnimator():
				self.addClipGroup()

		elif name == 'remove_clip':
			if self.checkTargetAnimator():
				self.removeClipNode()			

		elif name == 'clone_clip':
			if self.checkTargetAnimator():
				self.cloneClipNode()			

		elif name == 'add_track_group':
			group = self.delegate.callMethod( 'view', 'addTrackGroup' )
			if group:
				self.widget.addTrack( group, True )

		elif name == 'remove_track':
			for track in self.widget.treeTracks.getSelection():
				self.delegate.callMethod( 'view', 'removeTrack', track )
				self.widget.removeTrack( track )
		elif name == 'locate_target':
			for track in self.widget.treeTracks.getSelection():
				sceneGraphEditor = self.getModule( 'scenegraph_editor')
				if sceneGraphEditor:
					targetEntity = self.delegate.callMethod( 'view', 'findTrackEntity', track )
					if targetEntity:
						sceneGraphEditor.selectEntity( targetEntity, focus_tree = True )
				#pass
				return

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
			self.getApp().setMinimalMainLoopBudget()
			
	def stopPreview( self, rewind = False ):		
		if self.previewing:
			self.delegate.callMethod( 'view', 'stopPreview' )
			self.getApp().resetMainLoopBudget()
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

	def onSceneClose( self, scene ):
		self.setTargetAnimator( None )

	def onPreviewSpeedChange( self, index ):
		label, throttle = PREVIEW_SPEED_OPTIONS[ index ]
		self.delegate.callMethod( 'view', 'setPreviewThrottle', throttle )

	def refreshTimeline( self ):
		self.widget.rebuildTimeline()

	def refreshClipList( self ):
		self.widget.rebuildClipList()

	def refreshAll( self ):
		self.widget.rebuild()
