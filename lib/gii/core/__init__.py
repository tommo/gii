import logging

# loggingLevel = logging.WARNING
# loggingLevel = logging.INFO
# loggingLevel = logging.DEBUG


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
from cache          import CacheManager
from target         import Target, DeployManager

from MainModulePath import getMainModulePath

##----------------------------------------------------------------##
from EditorModule   import EditorModule
from EditorApp      import app
##----------------------------------------------------------------##

def getProjectPath( path ):
	return Project.get().getBasePath( path )
