import os
import sys
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
	
	# if option.get( 'configure', False ):
	# 	arglist.append( 'configure' )

	elif option.get( 'clean', False ):
		arglist.append( 'clean' )
	
	else:
		targets = option.get( 'targets', [ 'osx' ] )
		if targets == 'native':
			if sys.platform == 'darwin':
				targets = [ 'osx', 'python' ]
			else:
				targets = [ 'win', 'python' ]
		config = option.get( 'profile', 'debug' )
		for target in targets:
			suffix = '-%s-%s' % ( target, config )
			arglist.append( 'build' + suffix )
			arglist.append( 'install' + suffix )
			try:
				code = subprocess.call( arglist )
				if code!=0: return code
			except Exception, e:
				logging.error( 'cannot build host: %s ' % e)
				return -1
	