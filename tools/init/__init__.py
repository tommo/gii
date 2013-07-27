import os.path
import logging

import gii

def main( argv ):
	project = gii.Project.get()
	# try:
	project.init( os.path.abspath('') )
	# except Exception, e:
	# 	logging.error('initialization failed: %s' % str( e ) )
	# 	return False
	print 'done!'
	return True
