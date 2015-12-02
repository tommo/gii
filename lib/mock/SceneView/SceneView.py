import subprocess
import os.path
import shutil
import time
import json

from gii.core         import *
from gii.qt           import *
from gii.qt.helpers   import addWidgetWithLayout, QColorF, unpackQColor
from gii.qt.dialogs   import requestString, alertMessage, requestColor

from gii.SceneEditor  import SceneEditorModule, SceneTool, SceneToolMeta, SceneToolButton

from gii.moai.MOAIEditCanvas import  MOAIEditCanvas

from PyQt4  import QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import Qt


##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

##----------------------------------------------------------------##
class SceneViewTool( SceneTool ):
	def getSceneViewToolId( self ):
		toolId = getattr( self.__class__, 'tool' )
		if not toolId:
			raise Exception( 'no scene view tool Id specified' )
		return toolId

	def onStart( self, **context ):
		canvasToolId = self.getSceneViewToolId()
		app.getModule( 'scene_view' ).changeEditTool( canvasToolId )


##----------------------------------------------------------------##
class SceneViewToolSelection( SceneViewTool ):
	name     = 'scene_view_selection'
	shortcut = 'Q'
	tool     = 'selection'

##----------------------------------------------------------------##
class SceneViewToolTranslation( SceneViewTool ):
	name     = 'scene_view_translation'
	shortcut = 'W'
	tool     = 'translation'

##----------------------------------------------------------------##
class SceneViewToolRotation( SceneViewTool ):
	name     = 'scene_view_rotation'
	shortcut = 'E'
	tool     = 'rotation'

##----------------------------------------------------------------##
class SceneViewToolScale( SceneViewTool ):
	name     = 'scene_view_scale'
	shortcut = 'R'
	tool     = 'scale'

# ##----------------------------------------------------------------##
# class SceneViewToolFocusSelection( SceneViewTool ):
# 	name     = 'scene_view_scale'
# 	shortcut = 'R'
# 	tool     = 'scale'

##----------------------------------------------------------------##
class SceneView( SceneEditorModule ):
	name       = 'scene_view'
	dependency = [ 'mock', 'scene_editor', 'scenegraph_editor' ]

	def onLoad( self ):
		self.previousDragData = None

		self.window = self.requestDocumentWindow(
				title = 'Scene'
			)

		self.toolbar = self.window.addToolBar()
		self.addToolBar( 'scene_view_config', self.toolbar )

		self.canvas = self.window.addWidget( SceneViewCanvas() )
		self.canvas.loadScript( _getModulePath('SceneView.lua') )
		self.canvas.parentView = self
		
		self.canvas.setDelegateEnv( '_giiSceneView', self )

		self.updateTimer        = None
		self.updatePending      = False
		self.previewing         = False
		self.previewUpdateTimer = False

		signals.connect( 'entity.modified',       self.onEntityModified   )
		signals.connect( 'asset.post_import_all', self.onAssetReimport    )
		signals.connect( 'scene.open',            self.onSceneOpen        )
		signals.connect( 'scene.close',           self.onSceneClose       )
		signals.connect( 'scene.change',          self.onSceneUpdate      )
		signals.connect( 'scene.update',          self.onSceneUpdate      )
		signals.connect( 'selection.changed',     self.onSelectionChanged )

		signals.connect( 'animator.start', self.onAnimatorStart )
		signals.connect( 'animator.stop',  self.onAnimatorStop )

		signals.connect( 'preview.resume', self.onPreviewResume )
		signals.connect( 'preview.pause',  self.onPreviewStop   )
		signals.connect( 'preview.stop',   self.onPreviewStop   )

		signals.connect( 'external_player.start', self.onExternRun )

		##----------------------------------------------------------------##
		self.addShortcut( 'main', 'F',  'scene_editor/focus_selection' )
		self.addShortcut( 'main', '/',  self.toggleDebugLines )

		self.addShortcut( self.canvas, 'Delete', 'scene_editor/remove_entity' )

		##----------------------------------------------------------------##
		self.mainToolBar = self.addToolBar( 'scene_view_tools', 
			self.getMainWindow().requestToolBar( 'view_tools' )
			)

		self.addTool(	'scene_view_tools/tool_selection',
			widget = SceneToolButton( 'scene_view_selection',
				icon = 'tools/selection',
				label = 'Selection'
				)
			)

		self.addTool(	'scene_view_tools/tool_translation',
			widget = SceneToolButton( 'scene_view_translation',
				icon = 'tools/translation',
				label = 'Translation'
				)
			)

		self.addTool(	'scene_view_tools/tool_rotation',
			widget = SceneToolButton( 'scene_view_rotation',
				icon = 'tools/rotation',
				label = 'Rotation'
				)
			)

		self.addTool(	'scene_view_tools/tool_scale',
			widget = SceneToolButton( 'scene_view_scale',
				icon = 'tools/scale',
				label = 'Scale'
				)
			)

		##----------------------------------------------------------------##
		self.alignToolBar = self.addToolBar( 'scene_view_tools_align', 
			self.getMainWindow().requestToolBar( 'view_tools_align' )
			)

		self.addTool(	'scene_view_tools_align/align_bottom',
			label = 'Align Bottom',
			icon  = 'tools/align-bottom-edges',
			command   = 'align_entities',
			command_args = dict( mode = 'align_bottom' ),
		)

		self.addTool(	'scene_view_tools_align/align_top',
			label = 'Align Top',
			icon  = 'tools/align-top-edges',
			command   = 'align_entities',
			command_args = dict( mode = 'align_top' ),
		)

		self.addTool(	'scene_view_tools_align/align_vcenter',
			label = 'Align V Center',
			icon  = 'tools/align-vertical-centers',
			command   = 'align_entities',
			command_args = dict( mode = 'align_vcenter' ),
		)

		self.addTool(	'scene_view_tools_align/align_left',
			label = 'Align Left',
			icon  = 'tools/align-left-edges',
			command   = 'align_entities',
			command_args = dict( mode = 'align_left' ),
		)

		self.addTool(	'scene_view_tools_align/align_right',
			label = 'Align Right',
			icon  = 'tools/align-right-edges',
			command   = 'align_entities',
			command_args = dict( mode = 'align_right' ),
		)

		self.addTool(	'scene_view_tools_align/align_hcenter',
			label = 'Align H Center',
			icon  = 'tools/align-horizontal-centers',
			command   = 'align_entities',
			command_args = dict( mode = 'align_hcenter' ),
		)

		self.addTool(	'scene_view_tools_align/----' )

		self.addTool(	'scene_view_tools_align/push_together_left',
			label = 'Push Left',
			icon  = 'tools/push-together-left',
			command   = 'align_entities',
			command_args = dict( mode = 'push_together_left' ),
		)

		self.addTool(	'scene_view_tools_align/push_together_right',
			label = 'Push right',
			icon  = 'tools/push-together-right',
			command   = 'align_entities',
			command_args = dict( mode = 'push_together_right' ),
		)

		self.addTool(	'scene_view_tools_align/push_together_top',
			label = 'Push top',
			icon  = 'tools/push-together-top',
			command   = 'align_entities',
			command_args = dict( mode = 'push_together_top' ),
		)

		self.addTool(	'scene_view_tools_align/push_together_bottom',
			label = 'Push bottom',
			icon  = 'tools/push-together-bottom',
			command   = 'align_entities',
			command_args = dict( mode = 'push_together_bottom' ),
		)

		#config tool
		self.addTool(	'scene_view_config/toggle_gizmo_visible', 
			label = 'toggle gizmo',
			icon  = 'gizmo-all',
			type  = 'check'
			)

		self.addTool(	'scene_view_config/toggle_snap_grid', 
			label = 'snap',
			icon  = 'magnet',
			type  = 'check'
			)

		self.addTool(	'scene_view_config/toggle_grid', 
			label = 'grid',
			icon  = 'grid',
			type  = 'check'
			)

		self.gridWidthSpinBox = QtGui.QSpinBox()
		self.gridWidthSpinBox.setRange( 10, 1000 )
		self.gridWidthSpinBox.valueChanged.connect( self.onGridWidthChange )
		self.gridWidthSpinBox.setButtonSymbols( QtGui.QAbstractSpinBox.NoButtons )
		self.toolbar.addWidget( self.gridWidthSpinBox )

		self.gridHeightSpinBox = QtGui.QSpinBox()
		self.gridHeightSpinBox.setRange( 10, 1000 )
		self.gridHeightSpinBox.valueChanged.connect( self.onGridHeightChange )
		self.gridHeightSpinBox.setButtonSymbols( QtGui.QAbstractSpinBox.NoButtons )
		self.toolbar.addWidget( self.gridHeightSpinBox )

	def onStart( self ):
		self.scheduleUpdate()
		self.updateTimer = self.window.startTimer( 62, self.onUpdateTimer )
		self.updateTimer.stop()

	def changeEditTool( self, name ):
		self.canvas.makeCurrent()
		self.canvas.safeCallMethod( 'view', 'changeEditTool', name )

	def toggleDebugLines( self ):
		self.canvas.makeCurrent()
		self.canvas.safeCallMethod( 'view', 'toggleDebugLines' )

	def onUpdateTimer( self ):
		if self.updatePending == True:
			self.updatePending = False
			self.canvas.updateCanvas( no_sim = self.previewing, forced = True )
			if not self.previewing:
				self.getModule( 'game_preview' ).refresh()

	def onSetFocus( self ):
		self.getModule( 'scene_editor' ).setFocus()
		self.window.show()
		self.window.setFocus()

	def onEntityModified( self, entity, context = None ):
		self.scheduleUpdate()

	def onAssetReimport( self ):
		self.scheduleUpdate()

	def onSceneUpdate( self ):
		self.scheduleUpdate()

	def onSceneOpen( self, node, scene ):
		self.window.setDocumentName( node.getPath() )
		self.canvas.show()
		self.toolbar.show()
		self.canvas.safeCall( 'onSceneOpen', scene )		
		self.setFocus()
		self.changeEditTool( 'translation' )
		self.updateTimer.start()
		self.forceUpdate()
		self.scheduleUpdate()

		#sync toolbar
		gridWidth   = self.canvas.callMethod( 'view', 'getGridWidth'  )
		gridHeight  = self.canvas.callMethod( 'view', 'getGridHeight' )
		gridVisible = self.canvas.callMethod( 'view', 'isGridVisible' )
		gridSnapping = self.canvas.callMethod( 'view', 'isGridSnapping' )
		gizmoVisible = self.canvas.callMethod( 'view', 'isGizmoVisible' )
		self.gridWidthSpinBox.setValue(	gridWidth	)
		self.gridHeightSpinBox.setValue( gridHeight )
		self.findTool( 'scene_view_config/toggle_grid' ).setValue( gridVisible )
		self.findTool( 'scene_view_config/toggle_snap_grid' ).setValue( gridSnapping )
		self.findTool( 'scene_view_config/toggle_gizmo_visible' ).setValue( gizmoVisible )

	def makeCanvasCurrent( self ):
		self.canvas.makeCurrent()

	def onSceneClose( self, node ):
		self.window.setDocumentName( None )
		self.canvas.safeCall( 'onSceneClose' )
		self.canvas.hide()
		self.toolbar.hide()
		self.updateTimer.stop()

	def onSelectionChanged( self, selection, key ):
		if key != 'scene': return
		self.canvas.safeCallMethod( 'view', 'onSelectionChanged', selection )

	def updateInPreview( self ):
		self.scheduleUpdate()
		introspector = self.getModule('introspector')
		if introspector:
			introspector.refresh()

	def onPreviewResume( self ):
		self.previewing = True
		self.toolbar.setStyleSheet('QToolBar{ border-bottom: 1px solid rgb(0, 120, 0); }')
		self.previewUpdateTimer = self.window.startTimer( 5, self.updateInPreview )

	def onPreviewStop( self ):
		self.previewing = False
		self.toolbar.setStyleSheet('QToolBar{ border-bottom: none }')
		self.previewUpdateTimer.stop()

	def onExternRun( self, reason ):
		self.canvas.clearModifierKeyState()

	def onAnimatorStart( self ):
		self.toolbar.setStyleSheet('QToolBar{ border-bottom: 1px solid rgb(255, 0, 120); }')
		self.animating = True

	def onAnimatorStop( self ):
		self.toolbar.setStyleSheet('QToolBar{ border-bottom: none }')
		self.animating = True

	def scheduleUpdate( self ):
		self.updatePending = True

	def forceUpdate( self ):
		self.scheduleUpdate()
		self.onUpdateTimer()

	def focusSelection( self ):
		self.canvas.safeCallMethod( 'view', 'focusSelection' )

	def onTool( self, tool ):
		name = tool.name
		if name == 'tool_selection':
			self.changeEditTool( 'selection' )
		elif name == 'tool_translation':
			self.changeEditTool( 'translation' )
		elif name == 'tool_rotation':
			self.changeEditTool( 'rotation' )
		elif name == 'tool_scale':
			self.changeEditTool( 'scale' )

		elif name == 'toggle_grid':
			self.canvas.safeCallMethod( 'view', 'setGridVisible', tool.getValue() )
			self.scheduleUpdate()

		elif name == 'toggle_snap_grid':
			self.canvas.safeCallMethod( 'view', 'setGridSnapping', tool.getValue() )
			self.scheduleUpdate()

		elif name == 'toggle_gizmo_visible':
			self.canvas.safeCallMethod( 'view', 'setGizmoVisible', tool.getValue() )
			self.scheduleUpdate()

	def getCurrentSceneView( self ):
		#TODO
		return self

	def onDragStart( self, mimeType, data, x, y ):
		if self.previousDragData == data: return True
		accepted = self.canvas.callMethod( 'view', 'startDrag', mimeType, data, x, y )
		if accepted:
			self.previousDragData = data
			return True
		else:
			self.previousDragData = None
			return False

	def onDragMove( self, x, y ):
		self.canvas.callMethod( 'view', 'moveDrag', x, y )

	def onDragDrop( self, x, y ):
		self.canvas.callMethod( 'view', 'finishDrag', x, y )
		self.previousDragData = None

	def onDragLeave( self ):
		self.canvas.callMethod( 'view', 'stopDrag' )
		self.previousDragData = None

	def onGridWidthChange( self, v ):
		self.canvas.safeCallMethod( 'view', 'setGridWidth', v )
		self.scheduleUpdate()

	def onGridHeightChange( self, v ):
		self.canvas.safeCallMethod( 'view', 'setGridHeight', v )
		self.scheduleUpdate()


	def disableCamera( self ):
		self.canvas.callMethod( 'view', 'disableCamera' )

	def enableCamera( self ):
		self.canvas.callMethod( 'view', 'disableCamera' )

	def hideEditorLayer( self ):
		self.canvas.callMethod( 'view', 'hideEditorLayer' )

	def showEditorLayer( self ):
		self.canvas.callMethod( 'view', 'showEditorLayer' )

##----------------------------------------------------------------##
class SceneViewCanvas( MOAIEditCanvas ):
	def __init__( self, *args, **kwargs ):
		super( SceneViewCanvas, self ).__init__( *args, **kwargs )
		self.setAcceptDrops( True )

	def dragEnterEvent( self, ev ):
		mimeData = ev.mimeData()
		pos = ev.pos()
		accepted = False
		if mimeData.hasFormat( GII_MIME_ASSET_LIST ):
			if self.parentView.onDragStart(
				GII_MIME_ASSET_LIST, str(mimeData.data( GII_MIME_ASSET_LIST )), 
				pos.x(), pos.y()
				):
				accepted = True
		if accepted:
			ev.acceptProposedAction()

	def dragMoveEvent( self, ev ):
		pos = ev.pos()
		self.parentView.onDragMove( pos.x(), pos.y() )
		ev.acceptProposedAction()

	def dragLeaveEvent( self, ev ):
		self.parentView.onDragLeave()

	def dropEvent( self, ev ):
		pos = ev.pos()
		self.parentView.onDragDrop( pos.x(), pos.y() )
		ev.acceptProposedAction()

