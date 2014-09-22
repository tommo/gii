import os.path
import logging

from gii.core import Project, app

def main( argv ):
	app.openProject()
	import gii.SceneEditor
	import gii.AssetEditor
	import gii.DeviceManager
	import gii.DebugView
	app.run()
