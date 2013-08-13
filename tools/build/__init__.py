import os
import logging
from gii.core import Project, app
from gii.core.tools import Build

def main( argv ):
	app.openProject()
	code = Build.run()
	exit( code )
	