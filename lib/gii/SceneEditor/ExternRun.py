from gii.core import *
from gii.core.tools import RunHost
import subprocess

def runScene( scnPath ):
	app.getProject().save()
	RunHost.run( 'main_preview_scene' )

def runGame():
	app.getProject().save()
	RunHost.run( 'main' )
