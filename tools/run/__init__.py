import os
import logging
from gii.core import Project, app

def main( argv ):
	app.openProject()
	project = app.getProject()
	os.chdir( project.getBasePath() )
	
	import subprocess

	bin = project.getBinaryPath( app.getPlatformName() + '/moai' )
	
	script = 'game/main.lua'
	if len(argv) > 1:
		script = 'game/' + argv[1] + '.lua'

	arglist = [
		bin,
		script
	]
	try:
		subprocess.call( arglist )
	except Exception, e:
		logging.error( 'cannot start host: %s ' % e)