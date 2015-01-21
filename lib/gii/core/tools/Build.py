import os
import sys
import logging
import subprocess

from gii.core import Project, app

def run( **option ):
	FNULL = open(os.devnull, 'wb')
	project = app.getProject()
	assert project.isLoaded()
	os.chdir( project.getHostPath() )

	waf = app.getPath( 'support/waf/waf' )
	#check configure
	code = subprocess.call( [waf, 'list'], stdout = FNULL, stderr = FNULL )
	if code != 0:
		code = subprocess.call( [waf, 'configure'] )
		if code != 0:
			logging.error( 'cannot configure building ' )
			return -1

	arglist = [	waf	]

	if option.get( 'verbose', False ):
		arglist.append( '-v' )
	
	if option.get( 'configure', False ):
		subprocess.call( [waf, 'configure'] )

	elif option.get( 'clean', False ):
		arglist.append( 'clean' )
		code = subprocess.call( arglist )

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
				if code!=0:
					logging.error( 'abnormal return code: %d ' % code)
					return code
				else:
					print '%s building completed' % target
					return 0
			except Exception, e:
				logging.error( 'cannot build host: %s ' % e)
				return -1
	