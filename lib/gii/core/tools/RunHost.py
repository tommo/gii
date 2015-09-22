import logging
import os
import sarge
import time

from gii.core import Project, app

_terminating = False

def terminate():
	global _terminating
	_terminating = True

def run( target, *args, **options ):
	global _terminating
	_terminating = False
	project = app.getProject()
	assert project.isLoaded()

	os.chdir( project.getBasePath() )
	bin = project.getBinaryPath( app.getPlatformName() + '/moai' )

	script = 'game/%s.lua' % target
	
	arglist = [
		bin,
		script
	]
	arglist += args
	returncode = 0
	try:
		pipeline = sarge.run( arglist, async = True )
		command = pipeline.commands[0]
		while True:
			time.sleep( 0.1 )
			returncode = command.poll()
			if returncode != None:
				break
			if _terminating:
				command.kill()
				returncode = -1
				break
		# pipeline.close()
		# returncode = command.poll()
	except Exception, e:
		logging.error( 'cannot start host: %s ' % e)
		return 1
	return returncode
