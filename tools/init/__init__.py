import os.path
import logging

import gii
from gii.core.project import ProjectException

def main( argv ):
	project = gii.Project.get()
	try:
		project.init( os.path.abspath('') )
	except ProjectException, e:
		print( 'initialization failed: %s' % str( e ) )
		return False
	print 'done!'
	return True
