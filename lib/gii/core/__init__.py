import logging

import signals
import globalSignals

from model          import *
from cli            import CLICommand, parseCLI
from tool           import ToolBase, startupTool
from project        import Project
# from asset          import AssetException, AssetNode, AssetLibrary, AssetManager, registerAssetManager
from MainModulePath import getMainModulePath

##----------------------------------------------------------------##
from EditorModule   import EditorModule
from EditorApp      import app
##----------------------------------------------------------------##
# loggingLevel = logging.INFO
loggingLevel = logging.WARNING
logging.basicConfig(
	format = '[%(levelname)s]\t%(message)s',
	level  = loggingLevel
	)
