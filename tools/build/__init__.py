import os
import logging
from gii.core import Project, app

def main( argv ):
	app.openProject()
	project = app.getProject()
	
	import subprocess

	os.chdir( project.getHostPath() )

	waf = app.getPath( 'support/waf/waf' )

	arglist = [
		waf,
		'build',
		'install'
	]
	try:
		subprocess.call( arglist )
	except Exception, e:
		logging.error( 'cannot start host: %s ' % e)