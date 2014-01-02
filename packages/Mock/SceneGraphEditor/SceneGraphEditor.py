import random
##----------------------------------------------------------------##
from gii.core        import app, signals
from gii.core.model  import *

from gii.qt          import QtEditorModule

from gii.qt.IconCache                  import getIcon
from gii.qt.dialogs                    import alertMessage
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget

from gii.moai.MOAIRuntime import MOAILuaDelegate
from gii.SceneEditor      import SceneEditorModule

from gii.SearchView       import requestSearchView, registerSearchEnumerator

##----------------------------------------------------------------##
from PyQt4           import QtCore, QtGui, uic
from PyQt4.QtCore    import Qt, QObject

##----------------------------------------------------------------##
from mock import _MOCK, isMockInstance
##----------------------------------------------------------------##

def getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path


##----------------------------------------------------------------##
class SceneGraphEditor( SceneEditorModule ):
	def __init__(self):
		super( SceneGraphEditor, self ).__init__()
		self.activeSceneNode  = None
		self.refreshScheduled = False
		self.previewing       = False
		
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
			dict( label = 'Open Scene', shortcut = 'ctrl+o' )
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
				dict( 
					label = 'Remove'					
				 )
			)

		self.addMenu( 'main/entity', dict( label = 'Entity' ) )
		self.addMenuItem( 'main/entity/add_empty_entity', dict( label = 'Create Empty', shortcut = 'ctrl+alt+N' ) )
		self.addMenuItem( 'main/entity/add_entity',       dict( label = 'Create', shortcut = 'ctrl+shift+N' ) )
		self.addMenuItem( 'main/entity/----' )
		self.addMenuItem( 'main/entity/load_prefab',        dict( label = 'Load Prefab', shortcut = 'ctrl+alt+shift+N' ) )
		self.addMenuItem( 'main/entity/----' )
		self.addMenuItem( 'main/entity/remove_entity',    dict( label = 'Remove'  ) )
		self.addMenuItem( 'main/entity/clone_entity',     dict( label = 'Clone',  shortcut = 'ctrl+d' ) )
		self.addMenuItem( 'main/entity/----' )
		self.addMenuItem( 'main/entity/add_component',    dict( label = 'Add Component', shortcut = 'ctrl+alt+=' ) )
		self.addMenuItem( 'main/entity/assign_layer',        dict( label = 'Assign Layer', shortcut = 'ctrl+alt+L' ) )

		self.addMenuItem( 'main/entity/----' )
		self.addMenuItem( 'main/find/find_entity', dict( label = 'Find In Scene', shortcut = 'ctrl+g' ) )

		#Toolbars
		self.addTool( 'scene_graph/fold_all',    label = 'fold' )
		self.addTool( 'scene_graph/unfold_all',  label = 'unfold' )
		self.addTool( 'scene_graph/load_prefab', label = 'prefab' )
		self.addTool( 'scene_graph/save_prefab', label = '->prefab' )

		self.addTool( 'scene/refresh', label = 'refresh', icon='refresh' )

		#SIGNALS
		signals.connect( 'moai.clean',        self.onMoaiClean        )

		signals.connect( 'scene.change',      self.onSceneChanged     )

		signals.connect( 'selection.changed', self.onSelectionChanged )
		signals.connect( 'selection.hint',    self.onSelectionHint    )

		signals.connect( 'preview.start',     self.onPreviewStart     )
		signals.connect( 'preview.stop' ,     self.onPreviewStop      )

		signals.connect( 'entity.added',      self.onEntityAdded      )
		signals.connect( 'entity.removed',    self.onEntityRemoved    )
		signals.connect( 'entity.renamed',    self.onEntityRenamed    )

		signals.connect( 'component.added',   self.onComponentAdded   )
		signals.connect( 'component.removed', self.onComponentRemoved )

		signals.connect( 'app.post_start',    self.postStart          )

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

	def openScene( self, node ):
		if self.activeSceneNode == node:			
			if self.getModule('scene_view'):
				self.getModule('scene_view').setFocus()
			return
		if not self.closeScene(): return
		self.activeSceneNode = node
		signals.emitNow( 'scene.pre_open', node )
		scene = self.delegate.safeCallMethod( 'editor', 'openScene', node.getPath() )
		signals.emitNow( 'scene.open', self.activeSceneNode, scene )
		self.setFocus()
		self.tree.rebuild()
		retainedState = self.activeSceneNode.getMetaData( 'tree_state', None )
		if retainedState:
			self.tree.loadFoldState( retainedState )

	def closeScene( self ):
		self.tree.clear()
		self.getApp().clearCommandStack( 'scene_editor' )
		signals.emitNow( 'scene.close', self.activeSceneNode )
		self.delegate.safeCallMethod( 'editor', 'closeScene' )		
		self.activeSceneNode = None
		#TODO: save confirmation
		return True

	def onSceneChanged( self, scene ):
		print('scene changed!!')
		self.tree.rebuild()
		
	def saveScene( self ):
		if not self.activeSceneNode: return
		self.delegate.safeCallMethod( 'editor', 'saveScene', self.activeSceneNode.getAbsFilePath() )
		self.retainedState = None
		retainedState = self.tree.saveFoldState()
		self.activeSceneNode.setMetaData( 'tree_state', retainedState )

	def refreshScene( self ):
		if not self.activeSceneNode: return
		if self.previewing: return
		self.refreshScheduled = False
		node = self.activeSceneNode
		self.retainedState = self.tree.saveFoldState()
		if self.delegate.safeCallMethod( 'editor', 'refreshScene' ):
			self.tree.loadFoldState( self.retainedState )
		#TODO:remove this
		# self.closeScene()
		# self.openScene( node )
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
		
		elif name == 'save_prefab':
			requestSearchView( 
				info    = 'select a perfab node to store',
				context = 'asset',
				type    = 'prefab',
				on_selection = lambda obj: self.createPrefab( obj )				
				)
		
		elif name == 'load_prefab':
			requestSearchView( 
				info    = 'select a perfab node to instantiate',
				context = 'asset',
				type    = 'prefab',
				on_selection = 
					lambda obj: 
						self.doCommand( 'scene_editor/create_prefab_entity', prefab = obj.getNodePath() )
				)

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

		elif name == 'remove_entity':
			self.doCommand( 'scene_editor/remove_entity' )

		elif name == 'clone_entity':
			self.doCommand( 'scene_editor/clone_entity' )

		elif name == 'find_entity':
			requestSearchView( 
				info    = 'search for entity in current scene',
				context = 'scene',
				type    = _MOCK.Entity,
				on_selection = self.selectEntity
				)

		elif name == 'remove_component':
			context = menu.getContext()
			if context:
				self.doCommand( 'scene_editor/remove_component', target = context )

		elif name == 'assign_layer':
			if not self.tree.getSelection(): return
			requestSearchView( 
				info    = 'select layer to assign',
				context = 'scene_layer',
				type    = _MOCK.Entity,
				on_selection = self.assignEntityLayer
				)

	def onSelectionChanged( self, selection, key ):
		if key != 'scene': return
		self.tree.blockSignals( True )
		self.tree.selectNode( None )
		for e in selection:
			self.tree.selectNode( e, add = True)
		self.tree.blockSignals( False )

	def selectEntity( self, target ):
		self.changeSelection( target )

	def renameEntity( self, target, name ):
		#TODO:command pattern
		target.setName( target, name )
		signals.emit( 'entity.modified', target )

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
		self.retainedState = self.tree.saveFoldState()
		self.delegate.safeCallMethod( 'editor', 'retainScene' )
		self.delegate.safeCallMethod( 'editor', 'startScenePreview' )
		self.previewing = True

	def onPreviewStop( self ):
		if not self.activeSceneNode: return
		self.delegate.safeCallMethod( 'editor', 'stopScenePreview' )
		self.previewing = False
		if self.delegate.safeCallMethod( 'editor', 'restoreScene' ):
			self.tree.loadFoldState( self.retainedState )

	def updateEntityPriority( self ):
		if not self.activeSceneNode: return

	def onEntityRenamed( self, entity, newname ):
		self.tree.refreshNodeContent( entity )

	def onEntityAdded( self, entity, context = None ):
		if context == 'new':
			self.setFocus()
			self.tree.setFocus()
			self.tree.editNode( entity )
			self.tree.selectNode( entity )
		signals.emit( 'scene.update' )

	def onEntityRemoved( self, entity ):
		signals.emit( 'scene.update' )

	def onComponentAdded( self, com, entity ):
		signals.emit( 'scene.update' )

	def onComponentRemoved( self, com, entity ):
		signals.emit( 'scene.update' )

	def createPrefab( self, targetPrefab ):
		selection = self.getSelection()
		if not selection: return
		if len( selection ) > 1:
			return alertMessage( 'multiple entities cannot be converted into prefab' )
		target = selection[0]
		self.doCommand( 'scene_editor/create_prefab', 
			entity = target, 
			prefab = targetPrefab.getAbsFilePath()
		)


##----------------------------------------------------------------##
def _sortEntity( a, b ):
	return b._priority - a._priority
	
##----------------------------------------------------------------##
class SceneGraphTreeWidget( GenericTreeWidget ):
	def getHeaderInfo( self ):
		return [('Name',200), ( 'Layer', 50 ), ('Type', 50)]

	def getRootNode( self ):
		return self.module.getActiveScene()

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
		if isMockInstance( node, 'Scene' ):
			return None

		if not isMockInstance( node, 'Entity' ):
			return None
		#Entity
		p = node.parent
		if p and not p.FLAG_EDITOR_OBJECT : return p
		return node.scene

	def getNodeChildren( self, node ):
		if isMockInstance( node, 'Scene' ):
			output = []
			for ent in node.entities:
				if ( not ent.parent ) and ( not ( ent.FLAG_EDITOR_OBJECT or ent.FLAG_INTERNAL ) ):
					output.append( ent )
			output = sorted( output, cmp = _sortEntity )
			return output

		output = []
		for ent in node.children:
			if not ( ent.FLAG_EDITOR_OBJECT or ent.FLAG_INTERNAL ):
				output.append( ent )
		return output

	def compareNodes( self, node1, node2 ):
		return node1._priority >= node2._priority

	def updateItemContent( self, item, node, **option ):
		name = None
		if isMockInstance( node,'Scene' ):
			item.setText( 0, node.name or '<unnamed>' )
			item.setIcon( 0, getIcon('scene') )
		else:
			item.setText( 0, node.name or '<unnamed>' )
			item.setIcon( 0, getIcon('obj') )
			item.setText( 1, node.getLayer( node ) )
			item.setText( 2, node.getClassName( node ) )
		
	def onItemSelectionChanged(self):
		items=self.selectedItems()
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
		if pos == 'on':
			self.module.doCommand( 'scene_editor/reparent_entity', target = target.node )
		elif pos == 'viewport':
			self.module.doCommand( 'scene_editor/reparent_entity', target = 'root' )

		super( GenericTreeWidget, self ).dropEvent( ev )

	def onDeletePressed( self ):
		self.module.doCommand( 'scene_editor/remove_entity' )

	def onItemChanged( self, item, col ):
		self.module.renameEntity( item.node, item.text(0) )


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
