import os
import logging
from gii.core import Project, app

def main( argv ):
	app.openProject()
	project = app.getProject()
	os.chdir( project.getBasePath() )
	
	import subprocess

	bin = project.getBinaryPath( app.getPlatformName() + '/moai' )

	arglist = [
		bin,
		'game/main.lua'
	]
	try:
		subprocess.call( arglist )
	except Exception, e:
		logging.error( 'cannot start host: %s ' % e)