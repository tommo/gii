import random
##----------------------------------------------------------------##
from gii.core        import app, signals
from gii.SceneEditor import SceneEditorModule, getSceneSelectionManager, SceneTool, SceneToolButton

from mock import SceneViewTool

def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

##----------------------------------------------------------------##
class WaypointTool( SceneViewTool ):
	name = 'waypoint_tool'
	tool = 'waypoint_tool'

##----------------------------------------------------------------##
class WaypointForceLinkTool( SceneViewTool ):
	name = 'waypoint_forcelink'
	tool = 'waypoint_forcelink'

##----------------------------------------------------------------##
class WaypointNoLinkTool( SceneViewTool ):
	name = 'waypoint_nolink'
	tool = 'waypoint_nolink'


##----------------------------------------------------------------##
class WaypointGraphEditor( SceneEditorModule ):
	name = 'waypoint_graph_tools'
	dependency = [ 'scene_view' ]

	def onLoad( self ):
		self.mainToolBar = self.addToolBar( 'waypoint_graph_editor', 
			self.getMainWindow().requestToolBar( 'waypoint_graph_editor' )
			)
		
		toolManager = self.getModule( 'scene_tool_manager' )
		
		self.addTool( 'waypoint_graph_editor/waypoint_tool',
			widget = SceneToolButton(
				'waypoint_tool',
				label = 'Waypoint Editor',
				icon = 'tools/waypoint'
			)
		)

		self.addTool( 'waypoint_graph_editor/waypoint_forcelink',
			widget = SceneToolButton(
				'waypoint_forcelink',
				label = 'Link Waypoint',
				icon = 'tools/waypoint_forcelink'
			)
		)

		self.addTool( 'waypoint_graph_editor/waypoint_nolink',
			widget = SceneToolButton(
				'waypoint_nolink',
				label = 'Forbid Waypoint Link',
				icon = 'tools/waypoint_nolink'
			)
		)

	def onStart( self ):
		pass
