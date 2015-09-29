import random
##----------------------------------------------------------------##
from gii.core        import app, signals
from gii.SceneEditor import SceneEditorModule, getSceneSelectionManager, SceneTool, SceneToolButton

from mock import SceneViewTool

def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

##----------------------------------------------------------------##
class PathTool( SceneViewTool ):
	name = 'path_tool'
	tool = 'path_tool'

##----------------------------------------------------------------##
class PathGraphEditor( SceneEditorModule ):
	name = 'path_editor'
	dependency = [ 'scene_view' ]

	def onLoad( self ):
		self.mainToolBar = self.addToolBar( 'path_editor', 
			self.getMainWindow().requestToolBar( 'path_editor' )
			)
		
		toolManager = self.getModule( 'scene_tool_manager' )
		
		self.addTool( 'path_editor/path_tool',
			widget = SceneToolButton(
				'path_tool',
				label = 'Path Editor',
				icon = 'tools/path'
			)
		)

	def onStart( self ):
		pass
