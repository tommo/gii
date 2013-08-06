import random
##----------------------------------------------------------------##
from gii.core        import app, signals
from gii.qt          import QtEditorModule

from gii.qt.IconCache                  import getIcon
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget
from gii.moai.MOAIRuntime import MOAILuaDelegate
from gii.SceneEditor      import SceneEditorModule
from gii.qt.helpers   import addWidgetWithLayout, QColorF, unpackQColor

##----------------------------------------------------------------##
from PyQt4           import QtCore, QtGui, uic
from PyQt4.QtCore    import Qt

##----------------------------------------------------------------##
from mock import _MOCK, isMockInstance
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
class LayerManager( SceneEditorModule ):
	def __init__(self):
		super( LayerManager, self ).__init__()

	def getName( self ):
		return 'layer_manager'

	def getDependency( self ):
		return [ 'scene_editor' ]

	def onLoad( self ):
		#UI
		self.windowTitle = 'Scenegraph'
		self.window = self.requestDockWindow( 'LayerManager',
			title     = 'Layers',
			size      = (120,120),
			minSize   = (120,120),
			dock      = 'left'
			)

		#Components
		self.tree = self.window.addWidget( LayerTreeWidget() )
		self.tool = self.addToolBar( 'layer_manager', self.window.addToolBar() )
		self.delegate = MOAILuaDelegate( self )
		self.delegate.load( _getModulePath( 'LayerManager.lua' ) )

		self.tool.addTool( 'add', label = '+')
		self.tool.addTool( 'remove', label = '-')
		self.tool.addTool( 'up', label = 'up')
		self.tool.addTool( 'down', label = 'down')
		#SIGNALS
		signals.connect( 'moai.clean', self.onMoaiClean )

	def onStart( self ):
		self.tree.rebuild()

	def addEntity( self, entity, scene ):
		self.tree.addNode( entity )

	def removeEntity( self, entity, scene ):
		self.tree.removeNode( entity )

	def addScene( self, scn ):
		self.tree.addNode( scn )

	def removeScene( self, scene ):
		self.tree.removeNode( scene )

	def onMoaiClean( self ):
		self.tree.clear()



	
##----------------------------------------------------------------##
class LayerTreeWidget( GenericTreeWidget ):
	def getHeaderInfo( self ):
		return [ ('Name',-1) ]

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

		#Entity
		p = node.parent
		if p: return p
		return node.scene

	def getNodeChildren( self, node ):
		if isMockInstance( node, 'Game' ):
			return node.layers
		return []

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
LayerManager().register()
