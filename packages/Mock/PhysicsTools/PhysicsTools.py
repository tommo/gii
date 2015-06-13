import random
##----------------------------------------------------------------##
from gii.core        import app, signals
from gii.SceneEditor      import SceneEditorModule, getSceneSelectionManager, SceneTool, SceneToolCategory

def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

##----------------------------------------------------------------##
class PhysicTools( SceneEditorModule ):
	name = 'physics_tools'
	dependency = [ 'scene_view' ]

	def onLoad( self ):
		self.mainToolBar = self.addToolBar( 'physics_tools', 
			self.getMainWindow().requestToolBar( 'physics_tools' )
			)
		
		toolManager = self.getModule( 'scene_tool_manager' )
		self.toolCategory = toolManager.createCategory( 'ew', name = 'PhysicTools' )
		self.tilemapCategory = self.toolCategory.createChildCategory( 'tilemap', name = 'TileMap' )
		
		self.addTool( 'physics_tools/shape_editor',
			label = 'Physics Shape Editor',
			icon = 'tools/box2d',
			type = 'check'
		)

	def onStart( self ):
		pass

	def onTool( self, tool ):
		name = tool.name
		if name == 'shape_editor':
			sceneView = app.getModule( 'scene_view' ).getCurrentSceneView()
			sceneView.changeEditTool( 'physics_shape_editor')

				