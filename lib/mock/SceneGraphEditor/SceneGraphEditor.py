import random
##----------------------------------------------------------------##
from gii.core        import app, signals ,printTraceBack
from gii.core.model  import *

from gii.qt          import QtEditorModule

from gii.qt.IconCache                  import getIcon
from gii.qt.dialogs                    import alertMessage, requestConfirm
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget, GenericTreeFilter
from gii.qt.helpers                    import makeBrush, makeFont

from gii.moai.MOAIRuntime import MOAILuaDelegate
from gii.SceneEditor      import SceneEditorModule

from gii.SearchView       import requestSearchView, registerSearchEnumerator

##----------------------------------------------------------------##
from PyQt4           import QtCore, QtGui, uic
from PyQt4.QtCore    import Qt, QObject
from PyQt4.QtGui     import QApplication, QStyle, QBrush, QColor, QPen, QIcon, QPalette

##----------------------------------------------------------------##
from mock import _MOCK, isMockInstance
##----------------------------------------------------------------##

GII_MIME_ENTITY_DATA = 'application/gii.entity-data'

def getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path


_brushAnimatable = makeBrush( color = '#5f3d26' )
_fontAnimatable  = makeFont( bold = True, italic = True )
##----------------------------------------------------------------##
class SceneGraphEditor( SceneEditorModule ):
	def __init__(self):
		super( SceneGraphEditor, self ).__init__()
		self.sceneDirty = False
		self.activeSceneNode  = None
		self.refreshScheduled = False
		self.previewing       = False
		self.workspaceState   = None
		
	def getName( self ):
		return 'scenegraph_editor'

	def getDependency( self ):
		return [ 'scene_editor' ]

	def onLoad( self ):
		#UI
		self.windowTitle = 'Scenegraph'
		self.container = self.requestDockWindow( 'SceneGraphEditor',
			title     = 'Scenegraph',
			size      = (200,200),
			minSize   = (200,200),
			dock      = 'left'
			)

		#Components
		self.treeFilter = self.container.addWidget(
			GenericTreeFilter(
				self.container
			),
			expanding = False
		)
		self.tree = self.container.addWidget( 
				SceneGraphTreeWidget( 
					self.container,
					sorting  = True,
					editable = True,
					multiple_selection = True,
					drag_mode = 'internal'
				)
			)
		self.tree.module = self
		self.tool = self.addToolBar( 'scene_graph', self.container.addToolBar() )
		self.delegate = MOAILuaDelegate( self )
		self.delegate.load( getModulePath( 'SceneGraphEditor.lua' ) )

		self.entityCreatorMenu=self.addMenu(
			'main/scene/entity_create',
			{ 'label':'Create Entity' }
			)

		self.componentCreatorMenu=self.addMenu(
			'main/scene/component_create',
			{ 'label':'Create Component' }
			)

		#menu
		self.addMenuItem(
			'main/file/open_scene', 
			dict( label = 'Open Scene', shortcut = 'ctrl+shift+o' )
			)

		self.addMenuItem( 'main/file/close_scene', 
			dict( label = 'Close Scene', shortcut = 'Ctrl+W' )
			)
		self.addMenuItem( 'main/scene/save_scene',
			dict( label = 'Save', shortcut = 'Ctrl+S' )
			)

		self.addMenu( 'main/scene/----' )
		self.addMenu( 'component_context', dict( label = 'Selected Component' ) )
		self.addMenuItem( 'component_context/remove_component', 
			dict( label = 'Remove' )
			)
		self.addMenuItem( 'component_context/copy_component', 
			dict( label = 'Copy' )
			)

		self.addMenu( 'main/entity', dict( label = 'Entity' ) )
		self.addMenuItem( 'main/entity/add_empty_entity',    dict( label = 'Create Empty', shortcut = 'ctrl+alt+N' ) )
		self.addMenuItem( 'main/entity/add_entity',          dict( label = 'Create', shortcut = 'ctrl+shift+N' ) )
		self.addMenuItem( 'main/entity/----' )
		self.addMenuItem( 'main/entity/load_prefab',         dict( label = 'Load Prefab', shortcut = 'ctrl+alt+shift+N' ) )
		self.addMenuItem( 'main/entity/load_prefab_in_container', dict( label = 'Load Prefab In Container', shortcut = 'ctrl+shift+=' ) )
		self.addMenuItem( 'main/entity/----' )
		self.addMenuItem( 'main/entity/remove_entity',       dict( label = 'Remove'  ) )
		self.addMenuItem( 'main/entity/clone_entity',        dict( label = 'Clone',  shortcut = 'ctrl+d' ) )
		self.addMenuItem( 'main/entity/----' )
		self.addMenuItem( 'main/entity/add_component',       dict( label = 'Add Component', shortcut = 'ctrl+alt+=' ) )
		self.addMenuItem( 'main/entity/assign_layer',        dict( label = 'Assign Layer', shortcut = 'ctrl+alt+L' ) )
		self.addMenuItem( 'main/entity/toggle_visibility',   dict( label = 'Toggle Visibility', shortcut = 'ctrl+/' ) )
		self.addMenuItem( 'main/entity/freeze_entity_pivot', dict( label = 'Freeze Pivot' ) )

		self.addMenuItem( 'main/entity/----' )
		self.addMenuItem( 'main/find/find_entity', dict( label = 'Find In Scene', shortcut = 'ctrl+f' ) )

		#Toolbars
		self.addTool( 'scene_graph/create_group',    label ='+ Group', icon = 'add_folder' )
		self.addTool( 'scene_graph/----'  )
		self.addTool( 'scene_graph/make_proto',    label = 'Convert To Proto', icon = 'proto_make' )
		self.addTool( 'scene_graph/create_proto_instance',    label = 'Create Proto Instance', icon = 'proto_instantiate' )
		self.addTool( 'scene_graph/----'  )
		self.addTool( 'scene_graph/fold_all',    label = 'F' )
		self.addTool( 'scene_graph/unfold_all',  label = 'U' )
		# self.addTool( 'scene_graph/load_prefab', label = '+ P' )
		# self.addTool( 'scene_graph/save_prefab', label = '>>P' )

		self.addTool( 'scene/refresh', label = 'refresh', icon='refresh' )

		#SIGNALS
		signals.connect( 'moai.clean',        self.onMoaiClean        )

		signals.connect( 'scene.clear',       self.onSceneClear      )
		signals.connect( 'scene.change',      self.onSceneChange     )

		signals.connect( 'selection.changed', self.onSelectionChanged )
		signals.connect( 'selection.hint',    self.onSelectionHint    )

		signals.connect( 'preview.start',     self.onPreviewStart     )
		signals.connect( 'preview.stop' ,     self.onPreviewStop      )

		# signals.connect( 'animator.start',     self.onAnimatorStart     )
		# signals.connect( 'animator.stop' ,     self.onAnimatorStop      )

		signals.connect( 'entity.added',      self.onEntityAdded      )
		signals.connect( 'entity.removed',    self.onEntityRemoved    )
		signals.connect( 'entity.renamed',    self.onEntityRenamed    )
		signals.connect( 'entity.modified',    self.onEntityModified    )
		signals.connect( 'entity.visible_changed',    self.onEntityVisibleChanged )
		signals.connect( 'entity.pickable_changed',   self.onEntityPickableChanged )


		signals.connect( 'prefab.unlink',     self.onPrefabUnlink    )
		signals.connect( 'prefab.relink',     self.onPrefabRelink    )
		signals.connect( 'proto.unlink',      self.onPrefabUnlink    )
		signals.connect( 'proto.relink',      self.onPrefabRelink    )


		signals.connect( 'component.added',   self.onComponentAdded   )
		signals.connect( 'component.removed', self.onComponentRemoved )

		signals.connect( 'app.post_start',    self.postStart          )
		signals.connect( 'project.presave',   self.preProjectSave )

		#editor
		if self.getModule('introspector'):
			import EntityEditor

		registerSearchEnumerator( sceneObjectSearchEnumerator )
		registerSearchEnumerator( entityNameSearchEnumerator )
		registerSearchEnumerator( componentNameSearchEnumerator )
		registerSearchEnumerator( layerNameSearchEnumerator )

	def onStart( self ):
		self.refreshCreatorMenu()

	def postStart( self ):
		previousScene = self.getConfig( 'previous_scene', None )
		if previousScene:
			node = self.getAssetLibrary().getAssetNode( previousScene )
			if node:
				node.edit()

	def onStop( self ):
		if self.activeSceneNode:
			self.setConfig( 'previous_scene', self.activeSceneNode.getNodePath() )
		else:
			self.setConfig( 'previous_scene', False )

	def onSetFocus( self ):
		self.container.show()
		self.container.raise_()
		self.container.setFocus()

	def getActiveScene( self ):
		return self.delegate.safeCallMethod( 'editor', 'getScene' )

	def getActiveSceneRootGroup( self ):
		scene = self.delegate.safeCallMethod( 'editor', 'getScene' )
		if scene:
			return scene.rootGroup
		else:
			return None

	def openScene( self, node, protoNode = None ):
		if self.activeSceneNode == node:			
			if self.getModule('scene_view'):
				self.getModule('scene_view').setFocus()

			if protoNode:
				self.delegate.safeCallMethod( 'editor', 'locateProto', protoNode.getPath() )
				if self.getModule('scene_view'):
					self.getModule('scene_view').focusSelection()
				
		else:
			if not self.closeScene(): return
			self.activeSceneNode = node
			signals.emitNow( 'scene.pre_open', node )
			scene = self.delegate.safeCallMethod( 'editor', 'openScene', node.getPath() )
			if not scene:
				#todo: raise something
				alertMessage( 'error', 
					'%s\n\nfailed to open scene, see console for detailed information.' % node.getPath() )
				return False
			signals.emitNow( 'scene.open', self.activeSceneNode, scene )
			self.setFocus()
			self.editingProtoNode = protoNode		
			self.loadWorkspaceState( False )
		
	def closeScene( self ):
		if self.sceneDirty:
			res = requestConfirm( 'scene modified!', 'save scene before close?' )
			if res == True:   #save
				self.saveScene()
			elif res == None: #cancel
				return
			elif res == False: #no save
				pass

		self.markSceneDirty( False )
		self.tree.clear()
		self.getApp().clearCommandStack( 'scene_editor' )
		signals.emitNow( 'scene.close', self.activeSceneNode )
		self.delegate.safeCallMethod( 'editor', 'closeScene' )		
		self.activeSceneNode = None
		return True

	def onSceneClear( self ):
		# self.tree.clear()
		pass

	def markSceneDirty( self, dirty = True ):
		if not self.previewing:
			self.sceneDirty = dirty

	def saveWorkspaceState( self ):
		self.retainWorkspaceState()
		treeFoldState      = self.workspaceState['tree_state']
		containerFoldState = self.workspaceState['container_state']
		self.activeSceneNode.setMetaData( 'tree_state', treeFoldState )
		self.activeSceneNode.setMetaData( 'container_state', containerFoldState )

	def loadWorkspaceState( self, restoreState = True ):
		treeFoldState = self.activeSceneNode.getMetaData( 'tree_state', None )		
		containerFoldState = self.activeSceneNode.getMetaData( 'container_state', None )		
		self.workspaceState = {
			'tree_state' : treeFoldState,
			'container_state' : containerFoldState
		}		
		if restoreState: self.restoreWorkspaceState()

	def retainWorkspaceState( self ):
		#tree node foldstate
		treeFoldState =  self.tree.saveFoldState()
		#save introspector foldstate
		introspectorFoldState = self.delegate.safeCallMethod( 'editor', 'saveIntrospectorFoldState' )
		self.workspaceState = {
			'tree_state': treeFoldState,
			'container_state' : introspectorFoldState
		}

	def restoreWorkspaceState( self ):
		if not self.workspaceState: return
		treeState = self.workspaceState.get( 'tree_state', None )
		if treeState:
			self.tree.loadFoldState( treeState )	
		containerState = self.workspaceState.get( 'container_state', None )
		if containerState:
			self.delegate.safeCallMethod( 'editor', 'loadIntrospectorFoldState', containerState )


	def onSceneChange( self ):
		self.tree.rebuild()
		self.restoreWorkspaceState()
		if self.editingProtoNode:
			self.delegate.safeCallMethod( 'editor', 'locateProto', self.editingProtoNode.getPath() )
			self.editingProtoNode = None
			if self.getModule('scene_view'):
					self.getModule('scene_view').focusSelection()
		
	def saveScene( self ):
		if not self.activeSceneNode: return
		self.markSceneDirty( False )
		signals.emitNow( 'scene.save' )
		self.delegate.safeCallMethod( 'editor', 'saveScene', self.activeSceneNode.getAbsFilePath() )
		signals.emitNow( 'scene.saved' )
		self.saveWorkspaceState()

	def refreshScene( self ):
		if not self.activeSceneNode: return
		if self.previewing: return
		self.refreshScheduled = False
		node = self.activeSceneNode
		self.retainWorkspaceState()
		if self.delegate.safeCallMethod( 'editor', 'refreshScene' ):
			self.restoreWorkspaceState()
		self.refreshCreatorMenu()

	def scheduleRefreshScene( self ):
		if not self.activeSceneNode: return
		self.refreshScheduled = True

	def refreshCreatorMenu( self ):
		def addEntityMenuItem( name ):
			if name == '----': 
				self.entityCreatorMenu.addChild( '----' )
				return
			self.entityCreatorMenu.addChild({
					'name'     : 'create_entity_'+name,
					'label'    : name,
					'command'  : 'scene_editor/create_entity',
					'command_args' : dict( name = name )
				})

		def addComponentMenuItem( name ):
			if name == '----': 
				self.componentCreatorMenu.addChild( '----' )
				return
			self.componentCreatorMenu.addChild({
					'name'     : 'create_component_'+name,
					'label'    : name,
					'command'  : 'scene_editor/create_component',
					'command_args' : dict( name = name )
				})

		self.entityCreatorMenu.clear()
		self.componentCreatorMenu.clear()

		registry = _MOCK.getEntityRegistry()
		#entity
		keys = sorted( registry.keys() )
		addEntityMenuItem( 'Entity' )
		addEntityMenuItem( '----' )
		for entityName in sorted( registry.keys() ):
			if entityName!='Entity': addEntityMenuItem( entityName )

		#component
		registry = _MOCK.getComponentRegistry()
		for comName in sorted( registry.keys() ):
			addComponentMenuItem( comName )

	def onUpdate( self ):
		if self.refreshScheduled:
			self.refreshScene()

	def preProjectSave( self, prj ):
		if self.activeSceneNode:
			_MOCK.game.previewingScene = self.activeSceneNode.getNodePath()

	def onMoaiClean( self ):
		self.tree.clear()

	def onTool( self, tool ):
		name = tool.name
		
		if name == 'fold_all':
			self.tree.foldAllItems()

		elif name == 'unfold_all':
			self.tree.expandAllItems()

		elif name == 'refresh':
			self.scheduleRefreshScene()

		elif name == 'make_proto':
			self.makeProto()

		elif name == 'create_proto_instance':
			requestSearchView( 
				info    = 'select a perfab node to instantiate',
				context = 'asset',
				type    = 'proto',
				on_selection = 
					lambda obj: 
						self.doCommand( 'scene_editor/create_proto_instance', proto = obj.getNodePath() )
				)

		elif name == 'create_group':
			self.doCommand( 'scene_editor/entity_group_create' )
			

	def onMenu( self, menu ):
		name = menu.name
		if name == 'close_scene':
			if self.previewing:
				alertMessage( 'Warning', 'Stop previewing before closing scene' )
				return
			self.closeScene()

		elif name == 'open_scene':
			if self.previewing:
				alertMessage( 'Warning', 'Stop previewing before opening scene' )
				return
			requestSearchView( 
				info    = 'select scene to open',
				context = 'asset',
				type    = 'scene',
				on_selection = self.openScene
				)
			
		elif name == 'save_scene':
			if self.previewing:
				alertMessage( 'Warning', 'Stop previewing before saving' )
				return
			self.saveScene()

		elif name == 'add_entity':
			requestSearchView( 
				info    = 'select entity type to create',
				context = 'entity_creation',
				on_selection = lambda obj: 
					self.doCommand( 'scene_editor/create_entity', name = obj )
				)

		elif name == 'add_component':
			requestSearchView( 
				info    = 'select component type to create',
				context = 'component_creation',
				on_selection = lambda obj: 
					self.doCommand( 'scene_editor/create_component', name = obj )
				)

		elif name == 'add_empty_entity':
			self.doCommand( 'scene_editor/create_entity', name = 'Entity' )

		elif name == 'load_prefab':
			requestSearchView( 
				info    = 'select a perfab node to instantiate',
				context = 'asset',
				type    = 'prefab',
				on_selection = 
					lambda obj: 
						self.doCommand( 'scene_editor/create_prefab_entity', prefab = obj.getNodePath() )
				)

		elif name == 'load_prefab_in_container':
			requestSearchView( 
				info    = 'select a perfab node to instantiate( PefabContainer )',
				context = 'asset',
				type    = 'prefab',
				on_selection = 
					lambda obj: 
						self.doCommand( 'scene_editor/create_prefab_container', prefab = obj.getNodePath() )
				)

		elif name == 'remove_entity':
			self.doCommand( 'scene_editor/remove_entity' )

		elif name == 'clone_entity':
			self.doCommand( 'scene_editor/clone_entity' )

		elif name == 'find_entity':
			requestSearchView( 
				info    = 'search for entity in current scene',
				context = 'scene',
				type    = _MOCK.Entity,
				on_selection = lambda x: self.selectEntity( x, focus_tree = True ) ,
				on_test      = self.selectEntity
				)

		elif name == 'remove_component':
			context = menu.getContext()
			if context:
				self.doCommand( 'scene_editor/remove_component', target = context )

		elif name == 'copy_component':
			context = menu.getContext()
			if context:
				self.doCommand( 'scene_editor/copy_component', target = context )

		elif name == 'assign_layer':
			if not self.tree.getSelection(): return
			requestSearchView( 
				info    = 'select layer to assign',
				context = 'scene_layer',
				type    = _MOCK.Entity,
				on_selection = self.assignEntityLayer
				)

		elif name == 'toggle_visibility':
			self.doCommand( 'scene_editor/toggle_entity_visibility' )

		elif name == 'freeze_entity_pivot':
			self.doCommand( 'scene_editor/freeze_entity_pivot' )


	def onSelectionChanged( self, selection, key ):
		if key != 'scene': return
		if self.tree.syncSelection:
			self.tree.blockSignals( True )
			self.tree.selectNode( None )
			for e in selection:
				self.tree.selectNode( e, add = True)
			self.tree.blockSignals( False )

	def selectEntity( self, target, **option ):
		if option.get( 'focus_tree', False ):
			self.tree.setFocus()
		self.changeSelection( target )

	##----------------------------------------------------------------##
	def renameEntity( self, target, name ):
		#TODO:command pattern
		target.setName( target, name )
		signals.emit( 'entity.modified', target )

	def addEntityNode( self, entity ):
		self.tree.addNode( entity, expanded = False )
		self.tree.setNodeExpanded( entity, False )

	def removeEntityNode( self, entity ):
		self.tree.removeNode( entity )

	def assignEntityLayer( self, layerName ):
		#TODO:command pattern
		if not layerName: return
		self.doCommand( 'scene_editor/assign_layer', target = layerName )

	def onSelectionHint( self, selection ):
		if selection._entity:
			self.changeSelection( selection._entity )			
		else:
			self.changeSelection( selection )

	def onPreviewStart( self ):
		if not self.activeSceneNode: return
		self.retainWorkspaceState()
		self.delegate.safeCallMethod( 'editor', 'retainScene' )
		self.delegate.safeCallMethod( 'editor', 'startScenePreview' )
		self.previewing = True

	def onPreviewStop( self ):
		if not self.activeSceneNode: return
		self.changeSelection( None )
		self.tree.clear()
		self.delegate.safeCallMethod( 'editor', 'stopScenePreview' )
		self.previewing = False
		if self.delegate.safeCallMethod( 'editor', 'restoreScene' ):
			self.restoreWorkspaceState()

	def onAnimatorStart( self ):
		self.retainWorkspaceState()
		self.delegate.safeCallMethod( 'editor', 'retainScene' )

	def onAnimatorStop( self ):
		self.tree.clear()
		self.delegate.safeCallMethod( 'editor', 'clearScene' )
		if self.delegate.safeCallMethod( 'editor', 'restoreScene' ):
			self.restoreWorkspaceState()

	##----------------------------------------------------------------##
	def updateEntityPriority( self ):
		if not self.activeSceneNode: return
		self.markSceneDirty()

	def onEntityRenamed( self, entity, newname ):
		self.tree.refreshNodeContent( entity )
		self.markSceneDirty()

	def onEntityVisibleChanged( self, entity ):
		self.tree.refreshNodeContent( entity )

	def onEntityPickableChanged( self, entity ):
		self.tree.refreshNodeContent( entity )

	def onEntityAdded( self, entity, context = None ):
		if context == 'new':
			self.setFocus()
			pnode = entity.parent
			if pnode:
				self.tree.setNodeExpanded( pnode, True )
			self.tree.setFocus()
			self.tree.editNode( entity )
			self.tree.selectNode( entity )
		signals.emit( 'scene.update' )
		self.markSceneDirty()

	def onEntityRemoved( self, entity ):
		signals.emit( 'scene.update' )
		self.markSceneDirty()

	def onEntityModified( self, entity, context = None ):
		self.markSceneDirty()

	##----------------------------------------------------------------##
	def onComponentAdded( self, com, entity ):
		signals.emit( 'scene.update' )
		self.markSceneDirty()


	def onComponentRemoved( self, com, entity ):
		signals.emit( 'scene.update' )
		self.markSceneDirty()


	##----------------------------------------------------------------##
	def onPrefabUnlink( self, entity ):
		self.tree.refreshNodeContent( entity, updateChildren = True )

	def onPrefabRelink( self, entity ):
		self.tree.refreshNodeContent( entity, updateChildren = True )

	def createPrefab( self, targetPrefab ):
		selection = self.getSelection()
		if not selection: return
		if len( selection ) > 1:
			return alertMessage( 'multiple entities cannot be converted into prefab' )
		target = selection[0]
		self.doCommand( 'scene_editor/create_prefab', 
			entity = target, 
			prefab = targetPrefab.getNodePath(),
			file   = targetPrefab.getAbsFilePath()
		)

	def makeProto( self ):
		selection = self.getSelection()
		if not selection: return
		if len( selection ) > 1:
			return alertMessage( 'multiple entities cannot be converted into Proto' )
		target = selection[0]
		if not target: return
		if requestConfirm( 'convert proto', 'Convert this Entity into Proto?' ):
			self.doCommand( 'scene_editor/make_proto', 
				entity = target
			)
			self.tree.refreshNodeContent( target )

	def createProtoInstance( self ):
		pass


	##----------------------------------------------------------------##
	def onCopyEntity( self ):
		entityGroupData = self.delegate.callMethod( 'editor', 'makeSceneSelectionCopyData' )
		if not entityGroupData: return False
		clip = QtGui.QApplication.clipboard()
		mime = QtCore.QMimeData()
		text = ''
		for s in self.getSelection():
			if text == '':
				text = text + s.name
			else:
				text = text + '\n' + s.name
		mime.setText( text )
		mime.setData( GII_MIME_ENTITY_DATA, entityGroupData.encode('utf-8') )
		clip.setMimeData( mime )
		return True

	def onPasteEntity( self ):
		clip = QtGui.QApplication.clipboard()
		mime = clip.mimeData()
		if mime.hasFormat( GII_MIME_ENTITY_DATA ):
			data = mime.data( GII_MIME_ENTITY_DATA )
			self.doCommand( 'scene_editor/paste_entity',
				data = str(data).decode('utf-8')
			)

	##----------------------------------------------------------------##
	def onCopyComponent( self ):
		entityGroupData = self.delegate.callMethod( 'editor', 'makeEntityCopyData' )
		if not entityGroupData: return False
		clip = QtGui.QApplication.clipboard()
		mime = QtCore.QMimeData()
		text = ''
		for s in self.getSelection():
			if text == '':
				text = text + s.name
			else:
				text = text + '\n' + s.name
		mime.setText( text )
		mime.setData( GII_MIME_ENTITY_DATA, str(entityGroupData) )
		clip.setMimeData( mime )
		return True

	def onPasteComponent( self ):
		clip = QtGui.QApplication.clipboard()
		mime = clip.mimeData()
		if mime.hasFormat( GII_MIME_ENTITY_DATA ):
			data = mime.data( GII_MIME_ENTITY_DATA )
			self.doCommand( 'scene_editor/paste_entity',
				data = str(data)
			)

##----------------------------------------------------------------##
def _sortEntity( a, b ):
	return b._priority - a._priority

# _BrushEntityNormal = QtGui.QBrush()
# _BrushEntityLocked = QtGui.QBrush( QColorF( 0.6,0.6,0.6 ) )
# _BrushEntityHidden = QtGui.QBrush( QColorF( 1,1,0 ) )
# _BrushEntityPrefab = QtGui.QBrush( QColorF( .5,.5,1 ) )


class SceneGraphTreeItemDelegate(QtGui.QStyledItemDelegate):
	_textBrush      = QBrush( QColor( '#dd5200' ) )
	_textPen        = QPen( QColor( '#dddddd' ) )
	_textPenGroup   = QPen( QColor( '#ada993' ) )
	_backgroundBrushHovered  = QBrush( QColor( '#454768' ) )
	_backgroundBrushSelected = QBrush( QColor( '#515c84' ) )
	
	def paint(self, painter, option, index):
		painter.save()
		index0 = index.sibling( index.row(), 0 )
		utype = index0.data( Qt.UserRole )

		# # set background color
		if option.state & QStyle.State_Selected:
			painter.setPen  ( Qt.NoPen )
			painter.setBrush( SceneGraphTreeItemDelegate._backgroundBrushSelected )
			painter.drawRect(option.rect)
		elif option.state & QStyle.State_MouseOver:
			painter.setPen  ( Qt.NoPen )
			painter.setBrush( SceneGraphTreeItemDelegate._backgroundBrushHovered )
			painter.drawRect(option.rect)

		rect = option.rect
		icon = QIcon( index.data( Qt.DecorationRole) )
		rect.adjust( 5, 0, 0, 0 )
		if icon and not icon.isNull():
			icon.paint( painter, rect, Qt.AlignLeft )
			rect.adjust( 22, 0, 0, 0 )
		text = index.data(Qt.DisplayRole)
		if utype == 1: #GROUP
			painter.setPen( SceneGraphTreeItemDelegate._textPenGroup )
		else:
			painter.setPen( SceneGraphTreeItemDelegate._textPen )
		painter.drawText( rect, Qt.AlignLeft | Qt.AlignVCenter, text )
		painter.restore()


class ReadonlySceneGraphTreeItemDelegate( SceneGraphTreeItemDelegate ):
	def createEditor( *args ):
		return None

##----------------------------------------------------------------##
class SceneGraphTreeWidget( GenericTreeWidget ):
	def __init__( self, *args, **kwargs ):
		super( SceneGraphTreeWidget, self ).__init__( *args, **kwargs )
		self.syncSelection = True
		self.adjustingRange = False
		self.verticalScrollBar().rangeChanged.connect( self.onScrollRangeChanged )
		self.setIndentation( 13 )

	def getHeaderInfo( self ):
		return [('Name',240), ( 'Layer', 50 ), ('V',27 ), ('L',27 ), ('', -1) ]

	def getReadonlyItemDelegate( self ):
		return ReadonlySceneGraphTreeItemDelegate( self )

	def getDefaultItemDelegate( self ):
		return SceneGraphTreeItemDelegate( self )

	def getRootNode( self ):
		return self.module.getActiveSceneRootGroup()

	def saveFoldState( self ):
		#TODO: other state?
		result = {}
		for node, item in self.nodeDict.items():
			if not isMockInstance( node, 'Entity' ): continue
			if not item: continue
			guid     = node['__guid']
			expanded = item.isExpanded()
			result[ guid ] = { 'expanded': expanded }
		return result

	def loadFoldState( self, data ):
		for node, item in self.nodeDict.items():
			if not isMockInstance( node, 'Entity' ): continue
			if not item: continue
			guid  = node['__guid']
			state = data.get( guid )
			if state:
				item.setExpanded( state['expanded'] )

	def saveTreeStates( self ):
		pass

	def loadTreeStates( self ):
		pass

	def getNodeParent( self, node ): # reimplemnt for target node	
		p = node.getParentOrGroup( node )
		if p and not p.FLAG_EDITOR_OBJECT :
			return p
		return None

	def getNodeChildren( self, node ):
		if isMockInstance( node, 'EntityGroup' ):
			output = []
			#groups
			for group in node.childGroups:
				output.append( group )
			#entities
			for ent in node.entities:
				if ( not ent.parent ) and ( not ( ent.FLAG_EDITOR_OBJECT or ent.FLAG_INTERNAL ) ):
					output.append( ent )
			# output = sorted( output, cmp = _sortEntity )
			return output

		else: #entity
			output = []
			for ent in node.children:
				if not ( ent.FLAG_EDITOR_OBJECT or ent.FLAG_INTERNAL ):
					output.append( ent )
			# output = sorted( output, cmp = _sortEntity )
			return output

	def compareNodes( self, node1, node2 ):
		return node1._priority >= node2._priority

	def createItem( self, node ):
		return SceneGraphTreeItem()

	def updateHeaderItem( self, item, col, info ):
		if info[0] == 'V':
			item.setText( col, '')
			item.setIcon( col, getIcon( 'entity_vis' ) )
		elif info[0] == 'L':
			item.setText( col, '')
			item.setIcon( col, getIcon( 'entity_lock' ) )

	def updateItemContent( self, item, node, **option ):
		name = None
		item.setData( 0, Qt.UserRole, 0 )

		if isMockInstance( node, 'EntityGroup' ):
			item.setText( 0, node.name or '<unnamed>' )
			item.setIcon( 0, getIcon('entity_group') )
			if node.isLocalVisible( node ):
				item.setIcon( 2, getIcon( 'entity_vis' ) )
			else:
				item.setIcon( 2, getIcon( 'entity_invis' ) )
			item.setData( 0, Qt.UserRole, 1 )

		elif isMockInstance( node, 'Entity' ):
			if node['FLAG_PROTO_SOURCE']:
				item.setIcon( 0, getIcon('proto') )
			elif node['PROTO_INSTANCE_STATE']:
				item.setIcon( 0, getIcon('instance') )
			elif node['__proto_history']:
				item.setIcon( 0, getIcon('instance-sub') )
			else:
				item.setIcon( 0, getIcon('obj') )
			item.setText( 0, node.name or '<unnamed>' )
			layerName = node.getLayer( node )
			if isinstance( layerName, tuple ):
				item.setText( 1, '????' )
			else:
				item.setText( 1, layerName )
			# item.setText( 2, node.getClassName( node ) )
			# item.setFont( 0, _fontAnimatable )
			if node.isLocalVisible( node ):
				item.setIcon( 2, getIcon( 'entity_vis' ) )
			else:
				item.setIcon( 2, getIcon( 'entity_invis' ) )
		
		
	def onItemSelectionChanged(self):
		if not self.syncSelection: return
		items = self.selectedItems()
		if items:
			selections=[item.node for item in items]
			self.module.changeSelection(selections)
		else:
			self.module.changeSelection(None)

	def dropEvent( self, ev ):		
		p = self.dropIndicatorPosition()
		pos = False
		if p == QtGui.QAbstractItemView.OnItem: #reparent
			pos = 'on'
		elif p == QtGui.QAbstractItemView.AboveItem:
			pos = 'above'
		elif p == QtGui.QAbstractItemView.BelowItem:
			pos = 'below'
		else:
			pos = 'viewport'

		target = self.itemAt( ev.pos() )
		ok = False
		if pos == 'on':
			ok = self.module.doCommand( 'scene_editor/reparent_entity', target = target.node )
		elif pos == 'viewport':
			ok = self.module.doCommand( 'scene_editor/reparent_entity', target = 'root' )
		if ok:
			super( GenericTreeWidget, self ).dropEvent( ev )
		else:
			ev.setDropAction( Qt.IgnoreAction )

	def onDeletePressed( self ):
		self.syncSelection = False
		self.module.doCommand( 'scene_editor/remove_entity' )
		self.syncSelection = True
		self.onItemSelectionChanged()

	def onItemChanged( self, item, col ):
		self.module.renameEntity( item.node, item.text(0) )

	def onClipboardCopy( self ):
		self.module.onCopyEntity()
		return True

	def onClipboardPaste( self ):
		self.module.onPasteEntity()
		return True

	def onScrollRangeChanged( self, min, max ):
		if self.adjustingRange: return
		self.adjustingRange = True
		self.verticalScrollBar().setRange( min, max + 2 )
		self.adjustingRange = False

	def onClicked(self, item, col):
		if col == 2: #editor view toggle
			self.module.doCommand( 'scene_editor/toggle_entity_visibility' )
		elif col == 3: #lock toggle
			pass
			# app.getModule('layer_manager').toggleLock( self.getNodeByItem(item) )


##----------------------------------------------------------------##
#TODO: allow sort by other column
class SceneGraphTreeItem(QtGui.QTreeWidgetItem):
	def __lt__(self, other):
		node0 = self.node
		node1 = hasattr(other, 'node') and other.node or None
		if not node1:
			return True
		if not node0:
			return False
		tree = self.treeWidget()
		group0 = isMockInstance( node0, 'EntityGroup' )
		group1 = isMockInstance( node1, 'EntityGroup' )
		if group0 != group1:
			if tree.sortOrder() == 0:
				if group0: return True
				if group1: return False
			else:
				if group0: return False
				if group1: return True
		proto0 = node0[ 'FLAG_PROTO_SOURCE' ]
		proto1 = node1[ 'FLAG_PROTO_SOURCE' ]
		if proto0 != proto1:
			if tree.sortOrder() == 0:
				if proto0: return True
				if proto1: return False
			else:
				if proto0: return False
				if proto1: return True
		return super( SceneGraphTreeItem, self ).__lt__( other )

##----------------------------------------------------------------##
SceneGraphEditor().register()

##----------------------------------------------------------------##
def sceneObjectSearchEnumerator( typeId, context ):
	if not context in ['scene', 'all']: return None
	modelMgr = ModelManager.get()
	objects = modelMgr.enumerateObjects( typeId, context )
	if not objects: return None
	result = []
	for obj in objects:
		name     = modelMgr.getObjectRepr( obj )
		typeName = modelMgr.getObjectTypeRepr( obj )
		entry = ( obj, name, typeName, None )
		result.append( entry )
	return result

def entityNameSearchEnumerator( typeId, context ):
	if not context in [ 'entity_creation' ] : return None
	registry = _MOCK.getEntityRegistry()
	result = []
	for name in sorted( registry.keys() ):
		entry = ( name, name, 'Entity', None )
		result.append( entry )
	return result

def componentNameSearchEnumerator( typeId, context ):
	if not context in [ 'component_creation' ] : return None
	registry = _MOCK.getComponentRegistry()
	result = []
	for name in sorted( registry.keys() ):
		entry = ( name, name, 'Entity', None )
		result.append( entry )
	return result
		
def layerNameSearchEnumerator( typeId, context ):
	if not context in [ 'scene_layer' ] : return None
	layers = _MOCK.game.layers
	result = []
	for l in sorted( layers.values() ):
		name = l.name
		if name == '_GII_EDITOR_LAYER': continue
		entry = ( name, name, 'Layer', None )
		result.append( entry )
	return result
