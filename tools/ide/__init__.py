import os.path
import logging
import click

from gii.core import Project, app

@click.command( help = 'start gii IDE' )
@click.option( '--stop-other-instance', flag_value = True, default = False,
	help = 'whether stop other running instance' )
def run( 
		stop_other_instance
	):
	app.openProject()
	import gii.SceneEditor
	import gii.AssetEditor
	import gii.DeviceManager
	import gii.DebugView

	import gii.ScriptView
	
	options = {}
	options[ 'stop_other_instance' ] = stop_other_instance

	print 'starting gii IDE...'
	app.run( **options )		

def main( argv ):
	return run( argv[1:], 'gii ide' )
	
