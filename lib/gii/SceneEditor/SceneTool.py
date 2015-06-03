import os
##----------------------------------------------------------------##
from gii.core     import *
from gii.qt.controls.PropertyEditor import PropertyEditor
from gii.qt.controls.Menu import MenuManager

##----------------------------------------------------------------##
class SceneToolCategory():
	def __init__(self):
		self.children = []
		self.parent = None
		self.tools = {}
		self.icon  = 'folder'
		self.name  = 'category'

	def getName( self ):
		return self.name

	def getChildren( self ):
		return self.children

	def getParent( self ):
		return self.parent

	def addChildCategory( self, category ):
		self.children.append( category )
		category.parent = self

	def addTool( self, tool ):
		toolId = tool.getId()
		if self.tools.has_key( toolId ):
			raise Exception( 'Duplicated Scene Tool: %s ( %s ) ' % ( toolId, self.getName() ) )
		tool.category = self
		self.tools[ toolId ] = tool

	def getToolList( self ):
		return [ tool for tool in self.tools.values() ]

	def __repr__( self ):
		return self.getName()

	def getIcon( self ):
		return self.icon


##----------------------------------------------------------------##
class SceneTool():
	def __init__( self ):
		self.active = False
		self.category = None

	def getId( self ):
		return 'unknown'

	def getName( self ):
		return 'Tool'

	def getIcon( self ):
		return 'null_thumbnail'

	def getCategory( self ):
		return self.category

	def __repr__( self ):
		return '%s::%s' % ( repr(self.category), self.getId() )

	def start( self ):
		self.active = True
		self.onStart()

	def finish( self ):
		self.active = False
		self.onFinish()

	def onLoad( self ):
		pass

	def onStart( self ):
		pass

	def onFinish( self ):
		pass

##----------------------------------------------------------------##
class SceneToolManager( EditorModule ):
	name = 'scene_tool_manager'
	dependency = [ 'scene_editor' ]
	def __init__( self ):		
		self.tools = {}
		self.defaultTool = None
		self.activeTool = None
		self.rootCategory = SceneToolCategory()
		
		self.favoriteCategory = SceneToolCategory()
		self.favoriteCategory.icon = 'star'
		self.rootCategory.addChildCategory( self.favoriteCategory )

		testTool = SceneTool()
		self.favoriteCategory.addTool( testTool)

	def onLoad( self ):
		pass

	def onStart( self ):
		for id, tool in self.tools.items():
			tool.onLoad()

	def getRootCategory( self ):
		return self.rootCategory
