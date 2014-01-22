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
from gii.SearchView       import requestSearchView, registerSearchEnumerator

##----------------------------------------------------------------##
from mock import _MOCK, isMockInstance
##----------------------------------------------------------------##


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
				GlobalObjectTreeWidget( 
					multiple_selection = True,
					editable           = True,
					drag_mode          = 'internal'
				)
			)

		self.tool = self.addToolBar( 'global_object_manager', self.window.addToolBar() )
		self.delegate = MOAILuaDelegate( self )
		self.delegate.load( _getModulePath( 'GlobalObjectManager.lua' ) )

		# self.creatorMenu=self.addMenu(
		# 	'global_object_create',
		# 	{ 'label':'Create Global Object' }
		# 	)

		self.addTool( 'global_object_manager/add',    label = 'Add', icon = 'add' )
		self.addTool( 'global_object_manager/remove', label = 'Remove', icon = 'remove' )
		self.addTool( 'global_object_manager/clone',  label = 'Clone', icon = 'clone' )
		self.addTool( 'global_object_manager/add_group',    label = 'Add Group', icon = 'add_folder' )
		
		#SIGNALS
		signals.connect( 'moai.clean', self.onMoaiClean )

		signals.connect( 'global_object.added',   self.onObjectAdded )
		signals.connect( 'global_object.removed', self.onObjectRemoved )
		signals.connect( 'global_object.renamed', self.onObjectRenamed )

		if self.getModule('introspector'):
			import GlobalObjectNodeEditor

		registerSearchEnumerator( globalObjectNameSearchEnumerator )

	def onStart( self ):
		self.tree.rebuild()

	def onMoaiClean( self ):
		self.tree.clear()

	def onTool( self, tool ):
		name = tool.name
		if name == 'add':
			requestSearchView( 
				info    = 'select global object class to create',
				context = 'global_object_class',
				on_selection = lambda objName: self.createGlobalObject( objName )				
				)

		if name == 'add_group':
			group = self.delegate.safeCall( 'addGroup' )
			self.tree.addNode( group )
			self.tree.editNode( group )
			self.tree.selectNode( group )

		elif name == 'remove':
			for node in self.tree.getSelection():
				self.doCommand( 'scene_editor/remove_global_object', target = node )
				self.tree.removeNode( node )

	def renameObject( self, obj, name ):
		obj.setName( obj, name )

	def createGlobalObject( self, objName ):
		self.doCommand( 'scene_editor/create_global_object', name = objName )

	def onObjectAdded( self, node, reason = 'new' ):
		self.tree.addNode( node )
		if reason == 'new':
			self.tree.editNode( node )
			self.tree.selectNode( node )

	def onObjectRemoved( self, node ):
		self.tree.removeNode( node )

	def onObjectRenamed( self, node, name ):
		self.tree.refreshNodeContent( node )

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

##----------------------------------------------------------------##
		
def globalObjectNameSearchEnumerator( typeId, context ):
	if not context in [ 'global_object_class' ] : return None
	registry = _MOCK.getGlobalObjectClassRegistry()
	result = []
	for name in registry.keys():
		entry = ( name, name, 'GlobalObject', None )
		result.append( entry )
	return result
