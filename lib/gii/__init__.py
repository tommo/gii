from core import *

##----------------------------------------------------------------##
def startup():
	info = Project.findProject()
	startupTool( info )
