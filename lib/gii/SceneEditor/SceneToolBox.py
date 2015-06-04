import random
##----------------------------------------------------------------##
from gii.core        import app, signals
from gii.qt          import QtEditorModule

from gii.qt.IconCache                  import getIcon
from gii.qt.controls.GenericTreeWidget import GenericTreeWidget
from gii.qt.controls.GenericListWidget import GenericListWidget
from gii.qt.controls.CategoryList      import CategoryList

from gii.moai.MOAIRuntime import MOAILuaDelegate
from gii.SceneEditor      import SceneEditorModule, getSceneSelectionManager
from gii.qt.helpers   import addWidgetWithLayout, QColorF, unpackQColor

##----------------------------------------------------------------##
from PyQt4           import QtCore, QtGui, uic
from PyQt4.QtCore    import Qt, pyqtSignal

##----------------------------------------------------------------##
from mock import _MOCK, isMockInstance
##----------------------------------------------------------------##

from SceneTool import *

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
class SceneToolBox( SceneEditorModule ):
	name = 'scene_tool_box'
	dependency = [ 'scene_tool_manager' ]
	
	def onLoad( self ):
		self.window = self.requestDockWindow( 'SceneToolBox',
			title     = 'Tools',
			size      = (120,120),
			minSize   = (120,120),
			dock      = 'bottom'
		)

		ui = self.window.addWidgetFromFile(
			_getModulePath('SceneToolBox.ui')
		)
		self.window.setStayOnTop( True )
		self.window.show()
		self.window.setObjectName( 'SceneToolBox' )

		self.treeCategory = SceneToolCategoryTreeWidget( 
					multiple_selection = False,
					editable           = False,
					drag_mode          = 'internal'
				)
		treeLayout = QtGui.QVBoxLayout( ui.containerTree )
		treeLayout.addWidget( self.treeCategory )
		treeLayout.setMargin( 0 )
		treeLayout.setSpacing( 0 )
		self.treeCategory.parentModule = self

		self.listTools = SceneToolListWidget()
		listLayout = QtGui.QVBoxLayout( ui.containerList )
		listLayout.addWidget( self.listTools )
		listLayout.setMargin( 0 )
		listLayout.setSpacing( 0 )
		self.listTools.parentModule = self
		self.listTools.setIconSize( QtCore.QSize( 64, 64 ) )
		# self.listTools.setGridSize( QtCore.QSize( 80, 6464 ) )

		self.currentCategory = None

	def onStart( self ):
		self.treeCategory.rebuild()

	def onCategorySelectionChanged( self ):
		for category in self.treeCategory.getSelection():
			self.currentCategory = category
			self.listTools.rebuild()
			return
		self.currentCategory = None
		self.listTools.rebuild()

	def getToolsInCurrentCategory( self ):
		category = self.currentCategory
		if category:
			return category.getToolList()
		else:
			return []

	def selectTool( self, tool ):
		print 'selecting Tool', tool
		if tool:
			pass
		else:
			pass

	def onSceneToolChanged( self, tool ):
		#TODO:locate and hilight tool item
		pass


##----------------------------------------------------------------##
class SceneToolCategoryTreeWidget( GenericTreeWidget ):
	def __init__( self, *arg, **kwargs ):
		super( SceneToolCategoryTreeWidget, self ).__init__( *arg, **kwargs )
		self.headerItem().setHidden( True )
		self.setAttribute(Qt.WA_MacShowFocusRect, False)

	def getHeaderInfo( self ):
		return [ ('Name',100) ]

	def getRootNode( self ):
		return app.getModule( 'scene_tool_manager' ).getRootCategory()

	# def saveTreeStates( self ):
	# 	for node, item in self.nodeDict.items():
	# 		node.__folded = item.isExpanded()

	# def loadTreeStates( self ):
	# 	for node, item in self.nodeDict.items():
	# 		folded = node.__folded or False
	# 		item.setExpanded( not folded )

	def getNodeParent( self, node ): # reimplemnt for target node	
		return node.getParent()

	def getNodeChildren( self, node ):
		return node.getChildren()
		
	def updateItemContent( self, item, node, **option ):
		iconName = node.getIcon()
		item.setIcon( 0, getIcon( iconName ) )
		item.setText( 0, node.getName() )
		
	def onItemSelectionChanged(self):
		selections = self.getSelection()
		self.parentModule.onCategorySelectionChanged()


##----------------------------------------------------------------##
class SceneToolListWidget( GenericListWidget ):
	def __init__( self, *args, **option ):
		super( SceneToolListWidget, self ).__init__( *args )		
		self.setAttribute(Qt.WA_MacShowFocusRect, False)

	def getItemFlags( self, node ):
		return {}

	def getDefaultOptions( self ):
		return None

	def getNodes( self ):
		return self.parentModule.getToolsInCurrentCategory()

	def updateItemContent( self, item, node, **option ):
		item.setText( node.getName() )
		item.setIcon( getIcon( node.getIcon() ) )

	def onItemSelectionChanged(self):
		node = self.getFirstSelection()
		self.parentModule.selectTool( node )
