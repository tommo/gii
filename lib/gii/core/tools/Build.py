import os
import logging
import subprocess

from gii.core import Project, app

def run( **option ):
	project = app.getProject()
	assert project.isLoaded()
	os.chdir( project.getHostPath() )

	waf = app.getPath( 'support/waf/waf' )
	arglist = [	waf	]

	if option.get( 'verbose', False ):
		arglist.append( '-v' )
	
	if option.get( 'configure', False ):
		arglist.append( 'configure' )

	elif option.get( 'clean', False ):
		arglist.append( 'clean' )
	
	else:
		arglist.append( 'build' )
		arglist.append( 'install' )

	targets = option.get( 'targets', [] )
	#todo, targets
	print arglist
	try:
		code = subprocess.call( arglist )
	except Exception, e:
		logging.error( 'cannot build host: %s ' % e)
		return 1
	return code
