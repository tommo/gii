import random
##----------------------------------------------------------------##
from gii.core        import app, signals
from gii.qt          import QtEditorModule

from gii.qt.IconCache                  import getIcon
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget
from gii.moai.MOAIRuntime import MOAILuaDelegate
from gii.SceneEditor      import SceneEditorModule, getSceneSelectionManager
from gii.qt.helpers   import addWidgetWithLayout, QColorF, unpackQColor

##----------------------------------------------------------------##
from PyQt4           import QtCore, QtGui, uic
from PyQt4.QtCore    import Qt

##----------------------------------------------------------------##
from mock import _MOCK, isMockInstance
##----------------------------------------------------------------##


signals.register ( 'global_object.added' )
signals.register ( 'global_object.removed' )

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
class GlobalObjectManager( SceneEditorModule ):
	def __init__(self):
		super( GlobalObjectManager, self ).__init__()

	def getName( self ):
		return 'global_object_manager'

	def getDependency( self ):
		return [ 'scene_editor' ]

	def onLoad( self ):
		#UI
		self.window = self.requestDockWindow( 'GlobalObjectManager',
			title     = 'Global Objects',
			size      = (120,120),
			minSize   = (120,120),
			dock      = 'left'
			)

		#Components
		self.tree = self.window.addWidget( 
				GlobalObjectTreeWidget( multiple_selection = False, editable = True )
			)

		self.tool = self.addToolBar( 'global_object_manager', self.window.addToolBar() )
		self.delegate = MOAILuaDelegate( self )
		self.delegate.load( _getModulePath( 'GlobalObjectManager.lua' ) )

		self.creatorMenu=self.addMenu(
			'global_object_create',
			{ 'label':'Create Global Object' }
			)

		self.addTool( 'global_object_manager/add',    label = '+')
		self.addTool( 'global_object_manager/remove', label = '-')
		self.addTool( 'global_object_manager/add_group',    label = '+group')
		
		#SIGNALS
		signals.connect( 'moai.clean', self.onMoaiClean )
		signals.connect( 'script.reload', self.refreshCreatorMenu )
		signals.connect( 'mock.init', self.refreshCreatorMenu )

		signals.connect( 'global_object.added', self.onObjectAdded )
		signals.connect( 'global_object.removed', self.onObjectRemoved )

		if self.getModule('introspector'):
			import GlobalObjectNodeEditor

	def onStart( self ):
		self.tree.rebuild()

	def onMoaiClean( self ):
		self.tree.clear()

	def refreshCreatorMenu( self ):
		self.creatorMenu.clear()
		registry = _MOCK.getGlobalObjectClassRegistry()
		for objName in sorted( registry.keys() ):
			self.creatorMenu.addChild({
					'name'     : 'create_global_object_'+objName,
					'label'    : objName,
					'command'  : 'scene_editor/create_global_object',
					'command_args' : dict( name = objName )
				})

	def onTool( self, tool ):
		name = tool.name
		if name == 'add':
			self.creatorMenu.popUp()
			# obj = self.delegate.safeCall( 'addObject' )
			# self.tree.addNode( obj )
			# self.tree.editNode( obj )
			# self.tree.selectNode( obj )

		if name == 'add_group':
			group = self.delegate.safeCall( 'addGroup' )
			self.tree.addNode( group )
			self.tree.editNode( group )
			self.tree.selectNode( group )

		elif name == 'remove':
			for node in self.tree.getSelection():
				self.delegate.safeCall( 'remove', node )
				self.tree.removeNode( node )

	def renameObject( self, obj, name ):
		obj.setName( obj, name )

	def onObjectAdded( self, node ):
		self.tree.addNode( obj )
		self.tree.editNode( obj )
		self.tree.selectNode( obj )

	def onObjectRemoved( self, node ):
		self.tree.removeNode( node )

##----------------------------------------------------------------##
class GlobalObjectTreeWidget( GenericTreeWidget ):
	def getHeaderInfo( self ):
		return [ ('Name',150), ('Type', 30) ]

	def getRootNode( self ):
		return _MOCK.game.globalObjectLibrary.root

	def saveTreeStates( self ):
		pass

	def loadTreeStates( self ):
		pass

	def getNodeParent( self, node ): # reimplemnt for target node	
		return node.parent

	def getNodeChildren( self, node ):
		if node.type == 'group':
			return [ k for k in node.children.values() ]
		else:
			return []

	def updateItemContent( self, item, node, **option ):
		name = None
		if node.type == 'group':
			item.setIcon( 0, getIcon('folder') )
			item.setText( 0, node.name )
		else:
			item.setIcon( 0, getIcon('text') )
			item.setText( 0, node.name )
			item.setText( 1, node.objectType or '???' )
			#TODO: type
		
	def onItemSelectionChanged(self):
		selections = self.getSelection()
		getSceneSelectionManager().changeSelection( selections )

	def onItemChanged( self, item, col ):
		obj = self.getNodeByItem( item )
		app.getModule('global_object_manager').renameObject( obj, item.text(0) )

##----------------------------------------------------------------##
GlobalObjectManager().register()
