import os
import logging
import argparse
from gii.core import Project, app
from gii.core.tools import Build


cli = argparse.ArgumentParser(
	prog = 'gii build',
	description = 'Build GII Host(s) for current project'
)

cli.add_argument( 'targets', 
	type = str, 
	nargs = '*',
	default = 'native'
	)

cli.add_argument( '-c, --configure', 
	dest   = 'configure',
	help   = 'Configure waf buildtool',
	action = 'store_true',
	default = False
	)

cli.add_argument( '-p, --profile', 
	dest   = 'profile',
	help   = 'release/debug ',
	default = 'debug'
	)

cli.add_argument( '--clean-bin', 
	dest   = 'clean-bin',
	help   = 'Clean built binary files',
	action = 'store_true',
	default = False
	)

cli.add_argument( '--clean', 
	dest   = 'clean',
	help   = 'Clean build files',
	action = 'store_true',
	default = False
	)

cli.add_argument( '-v','--verbose', 
	dest   = 'verbose',
	help   = 'Verbosal building log',
	action = 'store_true',
	default = False
	)

def main( argv ):
	app.openProject()
	args = cli.parse_args( argv[1:] )		
	code = Build.run( 
		**vars( args )
		)
	exit( code )
	