import os
import logging
import subprocess

from gii.core import Project, app

def run():
	project = app.getProject()
	assert project.isLoaded()
	os.chdir( project.getHostPath() )

	waf = app.getPath( 'support/waf/waf' )

	arglist = [
		waf,
		'build',
		'install'
	]
	try:
		code = subprocess.call( arglist )
	except Exception, e:
		logging.error( 'cannot build host: %s ' % e)
		return 1
	return code
