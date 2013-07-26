import os.path
import logging
import gii

def main( argv ):
	#start qt app
	import gii.moai.MOAIRuntime
	import gii.moai.MOAIGameView
	#startup
	if len(argv) > 1:
		scriptPath = argv[1]
	else:
		scriptPath = 'main.lua'
	gii.app.setConfig( 'start_script', scriptPath )
	gii.app.run()
