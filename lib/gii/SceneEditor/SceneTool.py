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

	def getManager( self ):
		return app.getModule( 'scene_tool_manager' )

##----------------------------------------------------------------##
class SceneTool():
	def __init__( self ):
		self.active = False
		self.category = None
		self.lastUseTime = -1

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
class RecentToolsCategory():
	def getToolList( self ):
		return self.getManager().getRecentToolList()

##----------------------------------------------------------------##
class SceneToolManager( EditorModule ):
	name = 'scene_tool_manager'
	dependency = [ 'scene_editor' ]
	def __init__( self ):		
		#
		self.defaultTool = None
		self.activeTool  = None
		self.recentTools = []

		self.toolStack = []

		self.recentLimit = 20
		self.useTime     = 0
		#
		self.rootCategory = SceneToolCategory()
		
		self.favoriteCategory = SceneToolCategory()
		self.favoriteCategory.name = '<Favorites>'
		self.favoriteCategory.icon = 'star-2'
		self.rootCategory.addChildCategory( self.favoriteCategory )

		self.recentCategory = SceneToolCategory()
		self.recentCategory.name = '<Recent>'
		self.recentCategory.icon = 'clock'
		self.rootCategory.addChildCategory( self.recentCategory )

		testTool = SceneTool()
		self.favoriteCategory.addTool( testTool)

	def onLoad( self ):
		pass

	def onStart( self ):
		pass

	def getRootCategory( self ):
		return self.rootCategory

	def addCategory( self, category ):
		self.rootCategory.addChildCategory( category )
		return category

	def createCategory( self, id, **option ):
		category = SceneToolCategory()
		category.name = option.get( 'name', 'Category' )
		category.icon = option.get( 'icon', 'folder' )
		return self.addCategory( category )

	def setActiveTool( self, tool ):
		self.useTime += 1
		self.activeTool = tool
		tool.lastUseTime = self.useTime
		if not ( tool in self.recentTools ):
			if len( self.recentTools ) >= self.recentLimit:
				self.recentTools = self.recentTools[ 1: ]
			self.recentTools.append( tool )
		else:
			self.recentTools.remove( tool )
			self.recentTools.append( tool )

	def getActiveTool( self ):
		return self.activeTool

	def getRecentToolList( self ):
		return self.recentTools

