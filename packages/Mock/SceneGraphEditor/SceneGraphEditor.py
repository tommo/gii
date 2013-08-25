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
		self.tree = self.container.addWidget( SceneGraphTreeWidget() )
		self.tree.module = self
		self.tool = self.addToolBar( 'scene_graph', self.container.addToolBar() )
		self.delegate = MOAILuaDelegate( self )
		self.delegate.load( getModulePath( 'SceneGraphEditor.lua' ) )

		#menu
		self.addMenuItem( 'main/scene/close_scene', dict( label = 'Close' ) )
		self.addMenuItem( 'main/scene/save_scene',  dict( label = 'Save' ) )

		#Toolbars
		self.addTool( 'scene_graph/add_sibling', label = '+obj' )
		self.addTool( 'scene_graph/add_child', label = '+child' )

		#SIGNALS
		signals.connect( 'moai.clean', self.onMoaiClean )
		signals.connect( 'selection.changed', self.onSelectionChanged)
		signals.connect( 'selection.hint', self.onSelectionHint )
		#editor
		if self.getModule('introspector'):
			import EntityEditor

	def onStart( self ):
		pass

	def openScene( self, node ):
		if self.activeSceneNode == node:			
			if self.getModule('scene_view'):
				self.getModule('scene_view').setFocus()
			return
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

	def saveScene( self ):
		if not self.activeSceneNode: return
		self.delegate.safeCallMethod( 'editor', 'saveScene', self.activeSceneNode.getAbsFilePath() )

	def refreshScene( self ):
		if not self.activeScene: return
		self.refreshScheduled = False
		node = self.activeSceneNode
		# self.delegate.safeCallMethod( 'editor', 'refreshScene' )
		#TODO:remove this
		self.closeScene()
		self.openScene( node )

	def scheduleRefreshScene( self ):
		if not self.activeScene: return
		self.refreshScheduled = True

	def onUpdate( self ):
		if self.refreshScheduled:
			self.refreshScene()

	def onMoaiClean( self ):
		self.tree.clear()

	def onTool( self, tool ):
		name = tool.name
		if name == 'add_sibling':
			self.doCommand( 'scene_editor/create_entity' )
		elif name == 'add_child':
			pass

	def onMenu( self, menu ):
		name = menu.name
		if name == 'close_scene':
			self.closeScene()
		elif name == 'save_scene':
			self.saveScene()


	def onSelectionChanged(self, selection):
		self.tree.blockSignals( True )
		self.tree.selectNode( None )
		for e in selection:
			self.tree.selectNode( e, add = True)
		self.tree.blockSignals( False )

	def onSelectionHint( self, selection ):
		self.getSelectionManager().changeSelection( selection )

	
##----------------------------------------------------------------##
class SceneGraphTreeWidget( GenericTreeWidget ):
	def getHeaderInfo( self ):
		return [('Name',-1)]

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

			return output

		output = []
		for ent in node.children:
			if not ent.FLAG_EDITOR_OBJECT:
				output.append( ent )
		return output

	def createItem( self, node ):
		return SceneGraphTreeItem()

	def updateItemContent( self, item, node, **option ):
		name = None
		if isMockInstance( node,'Scene' ):
			item.setText( 0, '%s <%s>' % ( node.name or '', node.getClassName( node ) ) )
			item.setIcon( 0, getIcon('scene') )
		else:
			item.setText( 0, '%s <%s>' % ( node.name or '', node.getClassName( node ) ) )
			item.setIcon( 0, getIcon('obj') )
		
	def onItemSelectionChanged(self):
		items=self.selectedItems()
		if items:
			selections=[item.node for item in items]
			app.getModule( 'scene_editor' ).getSelectionManager().changeSelection(selections)
		else:
			app.getModule( 'scene_editor' ).getSelectionManager().changeSelection(None)

##----------------------------------------------------------------##
class SceneGraphTreeItem( QtGui.QTreeWidgetItem ):
	pass
	# def __lt__(self, other):
	# 	node0 = self.node
	# 	node1 = hasattr(other, 'node') and other.node or None
	# 	if not node1:
	# 		return True	
	# 	return node0.getName().lower() < node1.getName().lower()

##----------------------------------------------------------------##
SceneGraphEditor().register()
