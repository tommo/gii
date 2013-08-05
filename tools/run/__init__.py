import os
import logging
from gii.core import Project, app

def main( argv ):
	app.openProject()
	project = app.getProject()
	os.chdir( project.getBasePath() )
	import subprocess
	arglist = [
		'bin/osx/moai',
		'game/startup.lua',
		'osx'
	]
	try:
		subprocess.call( arglist )
	except Exception, e:
		logging.error( 'cannot start host: %s ' % e)