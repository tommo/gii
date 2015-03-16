import os
import logging
import argparse
from gii.core import Project, app

cli = argparse.ArgumentParser(
	prog = 'gii run',
	description = 'Run GII desktop Host'
)

cli.add_argument( 'target', 
	type = str, 
	nargs = '?',
	default = 'main'
	)

cli.add_argument( '-b', 
	dest   = 'build',
	help   = 'Build host before running',
	action = 'store_true',
	default = False
)


def main( argv ):
	app.openProject()
	args = cli.parse_args( argv[1:] )	
	if args.build:
		from gii.core.tools import Build
		code = Build.run()
		if code and code != 0:
			exit( code )

	from gii.core.tools import RunHost
	code = RunHost.run( args.target )
	exit( code )
