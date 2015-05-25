import os
import os.path
import argparse
import logging
import subprocess
import sys
import gii
from gii.core import Project, app

cli = argparse.ArgumentParser(
	prog = 'gii python',
	description = 'run python script with GII module environment'
)

def main( argv ):
	interpreter = sys.executable
	args = argv[1:]
	# if len( args ) < 1:
	# 	print 'no script specified'
	# 	return 0
	
	l = [ interpreter ] + args
	if not os.path.exists( interpreter ):
		print 'python interperter not found'
		return -1

	PYTHONPATH0 = os.getenv( 'PYTHONPATH' )
	PYTHONPATH1 = (PYTHONPATH0 and PYTHONPATH0 + ':' or '') + ( ':'.join( gii.MODULEPATH ) )
	env = {
		'PYTHONPATH' : PYTHONPATH1
	}
	try:
		code = subprocess.call( l, env = env )
	except Exception, ex:
		print ex
		return -1

	return code
