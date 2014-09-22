# import os
# import logging
# import subprocess

# from gii.core import Project, app

# def run( target, *args ):
# 	project = app.getProject()
# 	assert project.isLoaded()

# 	os.chdir( project.getBasePath() )

# 	import subprocess

# 	bin = project.getBinaryPath( app.getPlatformName() + '/moai' )

# 	script = 'game/%s.lua' % target
	
# 	arglist = [
# 		bin,
# 		script
# 	]
# 	arglist += args
# 	try:
# 		code = subprocess.call( arglist )
# 	except Exception, e:
# 		logging.error( 'cannot start host: %s ' % e)
# 		return 1
# 	return code

import logging
import os
import sarge

from gii.core import Project, app

def run( target, *args ):
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
	code = 0
	try:
		pipeline = sarge.run( arglist, async = True )
		command = pipeline.commands[0]
		pipeline.close()
		code = command.poll()
	except Exception, e:
		logging.error( 'cannot start host: %s ' % e)
		return 1
	return code
