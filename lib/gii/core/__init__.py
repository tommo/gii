import logging

loggingLevel = logging.WARNING
loggingLevel = logging.INFO

logging.basicConfig(
	format = '[%(levelname)s]\t%(message)s',
	level  = loggingLevel
	)

##----------------------------------------------------------------##
import sip
sip.setapi("QString", 2)
sip.setapi('QVariant', 2)

##----------------------------------------------------------------##
import signals
import globalSignals
##----------------------------------------------------------------##
from model          import *
from cli            import CLICommand, parseCLI
from tool           import ToolBase, startupTool
from project        import Project
from asset          import AssetLibrary, AssetException, AssetNode, AssetManager
from target         import Target, DeployManager

from MainModulePath import getMainModulePath

##----------------------------------------------------------------##
from EditorModule   import EditorModule
from EditorApp      import app
##----------------------------------------------------------------##

def getProjectPath( path ):
	return Project.get().getBasePath( path )
