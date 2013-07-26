import os.path
import logging
from base import Project

def main( argv ):
	project = Project.get()
	# try:
	project.init( os.path.abspath('') )
	# except Exception, e:
		# logging.error('initialization failed:  %s' % str( e ) )
		# return False
	print 'done!'
	return True
