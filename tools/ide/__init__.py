import os.path
import logging

from gii.core import Project, app

def main( argv ):
	app.openProject()
	# import gii.moai.MOAIGameView
	import gii.AssetEditor
	import gii.ScriptView
	app.run()
