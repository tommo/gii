from core import *

##----------------------------------------------------------------##
def startup():
	path, internalPath, metaPath = Project.findProject()
	startupTool( internalPath )