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

class SceneGraphEdito( SceneEditorModule ):
	def __init__(self):
		super( SceneGraphEdito, self ).__init__()

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
		self.tool = self.addToolBar( 'scene_graph', self.container.addToolBar() )
		self.delegate = MOAILuaDelegate( self )
		self.delegate.load( getModulePath( 'SceneGraphEditor.lua' ) )

		self.addTool( 'scene_graph/add_sibling', label = '+obj' )
		self.addTool( 'scene_graph/add_child', label = '+child' )

		#SIGNALS
		signals.connect( 'moai.clean', self.onMoaiClean )
		signals.connect( 'selection.changed', self.onSelectionChanged)

	def onStart( self ):
		pass

	def addEntity( self, entity, scene ):
		if entity['__editor_entity']: return
		self.tree.addNode( entity )

	def removeEntity( self, entity, scene ):
		if entity['__editor_entity']: return
		self.tree.removeNode( entity )

	def addScene( self, scn ):
		self.tree.addNode( scn )

	def removeScene( self, scene ):
		self.tree.removeNode( scene )

	def onMoaiClean( self ):
		self.tree.clear()

	def onTool( self, tool ):
		name = tool.name
		if name == 'add_sibling':
			self.doCommand( 'scene_editor/create_entity' )
			
		elif name == 'add_child':
			pass

	def onSelectionChanged(self, selection):
		self.tree.blockSignals( True )
		self.tree.selectNode( None )
		for e in selection:
			self.tree.selectNode( e, add = True)
		self.tree.blockSignals( False )

	
##----------------------------------------------------------------##
class SceneGraphTreeWidget( GenericTreeWidget ):
	def getHeaderInfo( self ):
		return [('Name',-1)]

	def getRootNode( self ):
		return _MOCK.game

	def saveTreeStates( self ):
		pass

	def loadTreeStates( self ):
		pass

	def getNodeParent( self, node ): # reimplemnt for target node	
		if isMockInstance( node, 'Game' ):
			return None

		if isMockInstance( node, 'Scene' ):
			return _MOCK.game

		if not isMockInstance( node, 'Entity' ):
			return None
		#Entity
		p = node.parent
		if p: return p
		return node.scene

	def getNodeChildren( self, node ):
		if isMockInstance( node, 'Game' ):
			output = []
			for scene in node.scenes.values():
				if not scene['__editor_scene']:
					output.append( scene )
			return output

		if isMockInstance( node, 'Scene' ):
			output = []
			for ent in node.entities:
				if not ent['__editor_entity'] and not ent.parent:
					output.append( ent )
			return output

		output = []
		for ent in node.children:
			if not ent['__editor_entity']:
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
SceneGraphEdito().register()
