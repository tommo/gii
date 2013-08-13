import os
import logging
import subprocess

from gii.core import Project, app

def run( target ):
	project = app.getProject()
	assert project.isLoaded()

	os.chdir( project.getBasePath() )

	import subprocess

	bin = project.getBinaryPath( app.getPlatformName() + '/moai' )

	script = 'game/%s.lua' % target
	
	arglist = [
		bin,
		script
	]
	try:
		code = subprocess.call( arglist )
	except Exception, e:
		logging.error( 'cannot start host: %s ' % e)
		return 1
	return code