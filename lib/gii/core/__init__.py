import logging

# loggingLevel = logging.WARNING
# loggingLevel = logging.INFO
# loggingLevel = logging.DEBUG


##----------------------------------------------------------------##
import signals
import globalSignals

from mime import *
##----------------------------------------------------------------##

from helpers        import *
from model          import *
from res            import ResGuard
from cli            import CLICommand, parseCLI
from tool           import ToolBase, startupTool
from project        import Project
from asset          import AssetLibrary, AssetException, AssetNode, AssetManager, AssetCreator
from cache          import CacheManager
# from target         import Target, DeployManager

from MainModulePath import getMainModulePath

##----------------------------------------------------------------##
from Command        import EditorCommand, EditorCommandStack, EditorCommandRegistry
from RemoteCommand  import RemoteCommand, RemoteCommandRegistry
from EditorModule   import EditorModule
from EditorApp      import app

##----------------------------------------------------------------##
import CoreModule

##----------------------------------------------------------------##
import CommonAsset

def getProjectPath( path = None ):
	return Project.get().getBasePath( path )

def getAppPath( path = None ):
	return app.getPath( path )
