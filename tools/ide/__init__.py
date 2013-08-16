import os.path
import logging

from gii.core import Project, app

def main( argv ):
	app.openProject()
	import gii.AssetEditor
	import gii.SceneEditor
	import gii.ScriptView
	app.run()
