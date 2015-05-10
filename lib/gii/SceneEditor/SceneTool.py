import os
##----------------------------------------------------------------##
from gii.core     import *
from gii.qt.controls.PropertyEditor import PropertyEditor
from gii.qt.controls.Menu import MenuManager

##----------------------------------------------------------------##
class SceneTool():
	def __init__( self ):
		self.active = False

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

	def onLoad( self ):
		pass

	def onStart( self ):
		for id, tool in self.tools.items():
			tool.onLoad()

	def registerSceneTool( self, id, tool ):
		if self.tools.has_key( id ):
			raise Exception( 'Duplicated Scene Tool: %s ' % id )
		self.tools[ id ]


