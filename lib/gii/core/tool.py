from abc import ABCMeta, abstractmethod

import logging
import json
import os
import os.path
import sys
import imp

import signals
import globalSignals
import jsonHelper

from MainModulePath import getMainModulePath

##----------------------------------------------------------------##
class ToolBase(object):
	@abstractmethod
	def getName( self ):
		return 'APP'

	@abstractmethod
	def getVersion( self ):
		return '0.1'

	def setupCLI( self, parser ):
		pass

	def start( self, argv ):
		pass
	
##----------------------------------------------------------------##
#STUB

_DEFAULT_TOOL_PATH = 'tools'
_INFO_FILE_NAME    = '__gii__.json'
_TOOLS = []

_libTools = []
_prjTools = []

def loadToolSetting( path ):
	infoFilePath = path + '/' + _INFO_FILE_NAME
	if not os.path.exists( infoFilePath ): return False
	logging.debug( 'try loading tool: %s ' % path )
	try:
		data = json.load( file( infoFilePath, 'r' ) )
		if not data.get( 'active', True ): return False
		data[ 'module_path' ] = path
	except Exception, e:
		return False
	return data	

def scanToolsInPath( path ):
	toolList = []
	path = os.path.abspath( path )
	for currentDir, dirs, files in os.walk( unicode(path) ):
		for dirname in dirs:
			fullpath = currentDir + '/' + dirname
			data = loadToolSetting( fullpath )
			if data: toolList.append( data )
	return toolList

def scanTools( path ):
	global _libTools, _prjTools
	mainPath  = getMainModulePath()
	_libTools = scanToolsInPath( mainPath + '/' + _DEFAULT_TOOL_PATH )
	if path:
		_prjTools = scanToolsInPath( path + '/' + _DEFAULT_TOOL_PATH )
	return ( _libTools, _prjTools )

def startTool( toolInfo ):
	path = toolInfo[ 'module_path' ]
	toolModuleName = 'gii_tool_' + toolInfo['name']
	logging.info( 'start tool: %s <%s>' % ( toolInfo['name'], path ) )
	sys.path.insert( 0, path )
	m = imp.load_source( toolModuleName, path + '/__init__.py' )
	if hasattr( m, 'main' ):
		m.main( sys.argv[ 1: ] )

##----------------------------------------------------------------##
def printHeader():
	print '---------------------------'
	print 'GII development environment'
	print '---------------------------'

def printProjectInfo( info ):
	if not info: return
	print '  current project: ' + info.get('path')
	print ''
	print '    - NAME   : \t%s' % ( info.get('name', 'N/A') )
	print '    - AUTHOR : \t%s' % ( info.get('author', 'N/A') )
	print '    - VERSION: \t%s' % ( info.get('version', 'N/A') )
	print ''

def printToolInfo( info ):
	output = '    %s \t %s' % ( info.get('name', '???') , info.get('help','') )
	output = output.expandtabs( 16 )
	print output

def printAvailTools():	
	print '  available tool(s):'
	print ''
	print '    + BUILTIN TOOLS'
	print ''
	for info in _libTools:
		printToolInfo( info )	
	if _prjTools:
		print ''
		print '    + PROJECT TOOLS'
		print ''
		for info in _prjTools:
			printToolInfo( info )	
	print ''

def printUsage():
	print 'Usage:  gii <tool-name> ...'
	print ''
	printAvailTools()

def printMissingCommand( cmd ):
	printAvailTools( )
	print '  [ERROR] TOOL NOT FOUND: ' + cmd
	print ''
	
##----------------------------------------------------------------##
def startupTool( info ):	
	scanTools( info and info['path'] or None )
	argv = sys.argv
	if len( argv ) < 2:
		printHeader()
		printUsage()
		printProjectInfo( info )
		return False
	cmd = argv[1]
	for toolInfo in _prjTools + _libTools:
		if toolInfo.get('name') == cmd:
			return startTool( toolInfo )
	printHeader()
	printProjectInfo( info )
	printMissingCommand( cmd )

