import random
##----------------------------------------------------------------##
from gii.core        import app, signals
from gii.qt          import QtEditorModule

from gii.qt.IconCache                  import getIcon
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget
from gii.moai.MOAIRuntime import MOAILuaDelegate
from gii.SceneEditor      import SceneEditorModule

##----------------------------------------------------------------##
from PyQt4           import QtCore, QtGui, uic
from PyQt4.QtCore    import Qt

##----------------------------------------------------------------##
from mock import _MOCK, isMockInstance
##----------------------------------------------------------------##

def getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

class SceneGraphEditor( SceneEditorModule ):
	def __init__(self):
		super( SceneGraphEditor, self ).__init__()
		self.activeScene      = None
		self.activeSceneNode  = None
		self.refreshScheduled = False

	def getName( self ):
		return 'scenegraph_editor'

	def getDependency( self ):
		return [ 'scene_editor' ]

	def onLoad( self ):
		#UI
		sceneEditor = self.getModule( 'scene_editor' )
		self.windowTitle = 'Scenegraph'
		self.container = sceneEditor.requestDockWindow( 'SceneGraphEditor',
			title     = 'Scenegraph',
			size      = (200,200),
			minSize   = (200,200),
			dock      = 'left'
			)

		#Components
		self.tree = self.container.addWidget( 
				SceneGraphTreeWidget( sorting = False )
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
		self.addMenuItem( 'main/scene/close_scene', dict( label = 'Close' ) )
		self.addMenuItem( 'main/scene/save_scene',  dict( label = 'Save' ) )
		self.addMenu( 'main/scene/----' )
		self.addMenu( 'main/scene/component_context', dict( label = 'Selected Component' ) )

		self.addMenu( 'main/scene/component_context/remove', 
				dict( 
					label = 'Remove'					
				 )
			)

		#Toolbars
		self.addTool( 'scene_graph/add_sibling', label = '+obj' )
		self.addTool( 'scene_graph/add_child', label = '+child' )
		self.addTool( 'scene_graph/add_component', label = '+com' )
		self.addTool( 'scene_graph/clone_entity', label = 'clone' )
		self.addTool( 'scene_graph/remove_entity', label = '-obj' )

		self.addTool( 'scene/refresh', label = 'REFRESH')

		#SIGNALS
		signals.connect( 'moai.clean', self.onMoaiClean )
		signals.connect( 'selection.changed', self.onSelectionChanged)
		signals.connect( 'selection.hint', self.onSelectionHint )

		signals.connect( 'preview.start', self.onPreviewStart )
		signals.connect( 'preview.stop' , self.onPreviewStop )

		signals.connect( 'entity.renamed', self.onEntityRenamed )


		#editor
		if self.getModule('introspector'):
			import EntityEditor

	def onStart( self ):
		self.refreshCreatorMenu()

	def openScene( self, node ):
		if self.activeSceneNode == node:			
			if self.getModule('scene_view'):
				self.getModule('scene_view').setFocus()
			return
		if not self.closeScene(): return

		signals.emitNow( 'scene.pre_open', node )
		scene = self.delegate.safeCallMethod( 'editor', 'openScene', node.getPath() )
		signals.emitNow( 'scene.open', node, scene )
		self.activeScene     = scene
		self.activeSceneNode = node
		self.tree.rebuild()

	def closeScene( self ):
		signals.emitNow( 'scene.close', self.activeSceneNode )
		scene = self.delegate.safeCallMethod( 'editor', 'closeScene' )
		self.activeScene     = None
		self.activeSceneNode = None
		#TODO: save confirmation
		return True

	def saveScene( self ):
		if not self.activeSceneNode: return
		self.delegate.safeCallMethod( 'editor', 'saveScene', self.activeSceneNode.getAbsFilePath() )

	def refreshScene( self ):
		if not self.activeScene: return
		self.refreshScheduled = False
		node = self.activeSceneNode
		self.delegate.safeCallMethod( 'editor', 'refreshScene' )
		#TODO:remove this
		# self.closeScene()
		# self.openScene( node )
		self.refreshCreatorMenu()

	def scheduleRefreshScene( self ):
		if not self.activeScene: return
		self.refreshScheduled = True

	def refreshCreatorMenu( self ):
		self.entityCreatorMenu.clear()
		self.componentCreatorMenu.clear()
		registry = _MOCK.getEntityRegistry()

		for entityName in registry.keys():
			self.entityCreatorMenu.addChild({
					'name'     : 'create_entity_'+entityName,
					'label'    : entityName,
					'command'  : 'scene_editor/create_entity',
					'command_args' : dict( name = entityName )
				})

		registry = _MOCK.getComponentRegistry()
		for comName in registry.keys():			
			self.componentCreatorMenu.addChild({
					'name'     : 'create_component_'+comName,
					'label'    : comName,
					'command'  : 'scene_editor/create_component',
					'command_args' : dict( name = comName )
				})

	def onUpdate( self ):
		if self.refreshScheduled:
			self.refreshScene()

	def onMoaiClean( self ):
		self.tree.clear()

	def onTool( self, tool ):
		name = tool.name
		if name == 'add_sibling':
			self.entityCreatorMenu.popUp()
		elif name == 'add_child':
			self.entityCreatorMenu.popUp()
		elif name == 'add_component':
			self.componentCreatorMenu.popUp()
		elif name == 'remove_entity':
			self.doCommand( 'scene_editor/remove_entity' )
		elif name == 'clone_entity':
			self.doCommand( 'scene_editor/clone_entity' )
		elif name == 'refresh':
			self.scheduleRefreshScene()

	def onMenu( self, menu ):
		name = menu.name
		if name == 'close_scene':
			self.closeScene()
		elif name == 'save_scene':
			self.saveScene()


	def onSelectionChanged( self, selection, key ):
		if key != 'scene': return
		self.tree.blockSignals( True )
		self.tree.selectNode( None )
		for e in selection:
			self.tree.selectNode( e, add = True)
		self.tree.blockSignals( False )

	def onSelectionHint( self, selection ):
		self.changeSelection( selection )

	def onPreviewStart( self ):
		if not self.activeScene: return
		self.delegate.safeCallMethod( 'editor', 'retainScene' )

	def onPreviewStop( self ):
		if not self.activeScene: return
		self.delegate.safeCallMethod( 'editor', 'restoreScene' )

	def updateEntityPriority( self ):
		if not self.activeScene: return

	def onEntityRenamed( self, entity, newname ):
		self.tree.refreshNodeContent( entity )

##----------------------------------------------------------------##
def _sortEntity( a, b ):
	return b._priority - a._priority
	
##----------------------------------------------------------------##
class SceneGraphTreeWidget( GenericTreeWidget ):
	def getHeaderInfo( self ):
		return [('Name',200), ( 'Layer', 50 ), ('Type', 50)]

	def getRootNode( self ):
		return self.module.activeScene

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
				if ( not ent.parent ) and ( not ent.FLAG_EDITOR_OBJECT ):
					output.append( ent )
			output = sorted( output, cmp = _sortEntity )
			return output

		output = []
		for ent in node.children:
			if not ent.FLAG_EDITOR_OBJECT:
				output.append( ent )
		return output

	def compareNodes( self, node1, node2 ):
		return node1._priority >= node2._priority

	def createItem( self, node ):
		return SceneGraphTreeItem()

	def updateItemContent( self, item, node, **option ):
		name = None
		if isMockInstance( node,'Scene' ):
			item.setText( 0, node.name or '<unnamed>' )
			item.setIcon( 0, getIcon('scene') )
		else:
			item.setText( 0, node.name or '<unnamed>' )
			item.setIcon( 0, getIcon('obj') )
			item.setText( 2, node.getClassName( node ) )
		
	def onItemSelectionChanged(self):
		items=self.selectedItems()
		if items:
			selections=[item.node for item in items]
			self.module.changeSelection(selections)
		else:
			self.module.changeSelection(None)

##----------------------------------------------------------------##
class SceneGraphTreeItem( QtGui.QTreeWidgetItem ):
	def __lt__(self, other):
		node0 = self.node
		node1 = hasattr(other, 'node') and other.node or None
		if not node1:
			return True	
		return node0._priority <= node1._priority

##----------------------------------------------------------------##
SceneGraphEditor().register()
