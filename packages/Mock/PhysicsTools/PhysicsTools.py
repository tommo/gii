import random
##----------------------------------------------------------------##
from gii.core        import app, signals
from gii.SceneEditor import SceneEditorModule, getSceneSelectionManager, SceneTool, SceneToolButton

from mock import SceneViewTool

def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

##----------------------------------------------------------------##
class PhyscsShapeTool( SceneViewTool ):
	name = 'physics_shape_editor'
	tool = 'physics_shape_editor'

##----------------------------------------------------------------##
class PhysicTools( SceneEditorModule ):
	name = 'physics_tools'
	dependency = [ 'scene_view' ]

	def onLoad( self ):
		self.mainToolBar = self.addToolBar( 'physics_tools', 
			self.getMainWindow().requestToolBar( 'physics_tools' )
			)
		
		toolManager = self.getModule( 'scene_tool_manager' )
		
		self.addTool( 'physics_tools/shape_editor',
			widget = SceneToolButton(
				'physics_shape_editor',
				label = 'Physics Shape Editor',
				icon = 'tools/box2d'
			)
		)

	def onStart( self ):
		pass
