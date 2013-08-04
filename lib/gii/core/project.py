import logging
import sys
import imp
import os
import os.path

import signals
import jsonHelper
##----------------------------------------------------------------##
from cache   import CacheManager
from asset   import AssetLibrary
##----------------------------------------------------------------##
_GII_ENV_DIR            = 'env'
_GII_GAME_DIR           = 'game'
_GII_HOST_DIR           = 'host'
_GII_BINARY_DIR         = 'bin'

_GII_ASSET_DIR          = _GII_GAME_DIR + '/asset'
_GII_SCRIPT_DIR         = _GII_GAME_DIR + '/script'
_GII_SCRIPT_LIB_DIR     = _GII_GAME_DIR + '/lib'

_GII_HOST_EXTENSION_DIR = _GII_HOST_DIR  + '/extension'

_GII_ENV_PACKAGE_DIR    = _GII_ENV_DIR  + '/packages'
_GII_ENV_LIB_DIR        = _GII_ENV_DIR  + '/lib'
_GII_ENV_CONFIG_DIR     = _GII_ENV_DIR  + '/config'

_GII_INFO_FILE          = 'project.json'
_GII_CONFIG_FILE        = 'config.json'
####----------------------------------------------------------------##
_default_config = {
	"excluded_packages" : []
}

##----------------------------------------------------------------##
def _makePath( base, path ):
	if path:
		return base + '/' + path
	else:
		return base

##----------------------------------------------------------------##
def _mkdir( path ):
	if os.path.exists( path ): return
	os.mkdir( path )

##----------------------------------------------------------------##
class ProjectException(Exception):
	pass

##----------------------------------------------------------------##
class Project(object):
	_singleton=None
	@staticmethod
	def get():		
		return Project._singleton

	@staticmethod
	def findProject( path = None ):
		#TODO: return project info dict instead of path?
		path = os.path.abspath( path or '' )
		opath = None
		while path and not ( path in ( '', '/','\\' ) ):
			if   os.path.exists( path + '/' + _GII_ENV_CONFIG_DIR ) \
			and  os.path.exists( path + '/' + _GII_INFO_FILE ) :
				return path
			#go up level
			opath = path
			path = os.path.dirname( path )
			if path == opath: break
		return None

	def __init__(self):
		assert not Project._singleton
		Project._singleton = self

		self.path      = None
		self.cacheManager = CacheManager() 
		self.assetLibrary = AssetLibrary()

		self.info = {
			'name'    : 'Name',
			'author'  : 'author',
			'version' : '1.0.0'
		}

		self.config = {}

	def isLoaded( self ):
		return self.path != None

	def _initPath( self, path ):
		self.path = path

		self.binaryPath        = path + '/' + _GII_BINARY_DIR
		self.gamePath          = path + '/' + _GII_GAME_DIR

		self.envPath           = path + '/' + _GII_ENV_DIR
		self.envPackagePath    = path + '/' + _GII_ENV_PACKAGE_DIR
		self.envConfigPath     = path + '/' + _GII_ENV_CONFIG_DIR
		self.envLibPath        = path + '/' + _GII_ENV_LIB_DIR

		self.assetPath         = path + '/' + _GII_ASSET_DIR

		self.scriptPath        = path + '/' + _GII_SCRIPT_DIR
		self.scriptLibPath     = path + '/' + _GII_SCRIPT_LIB_DIR

		self.hostPath          = path + '/' + _GII_HOST_DIR
		self.hostExtensionPath = path + '/' + _GII_HOST_EXTENSION_DIR

	def _affirmDirectories( self ):
		#mkdir - lv1
		_mkdir( self.binaryPath )

		_mkdir( self.envPath )
		_mkdir( self.envPackagePath )
		_mkdir( self.envLibPath )
		_mkdir( self.envConfigPath )

		_mkdir( self.gamePath )
		_mkdir( self.assetPath )
		_mkdir( self.scriptPath )
		_mkdir( self.scriptLibPath )
		
		_mkdir( self.hostPath )
		_mkdir( self.hostExtensionPath )
		
	def init( self, path ):
		prjPath = Project.findProject( path )
		if prjPath:
			raise ProjectException( 'Gii project already initialized:' + prjPath )

		path = os.path.realpath(path)
		if not os.path.isdir(path):
			raise ProjectException('%s is not a valid path' % path)
		self._initPath( path )
		self._affirmDirectories()

		try:
			self.cacheManager.init( _GII_ENV_CONFIG_DIR, self.envConfigPath )
		except OSError,e:
			raise ProjectException('error creating cache folder:%s' % e)

		self.assetLibrary.load( _GII_ASSET_DIR, self.assetPath, self.path, self.envConfigPath )

		signals.emitNow('project.init', self)
		logging.info( 'project initialized: %s' % path )

		self.save()
		return True	

	def load(self, path):
		path = os.path.realpath(path)
		
		self._initPath( path )
		self._affirmDirectories()
		os.chdir( path )

		sys.path.insert( 0, self.envLibPath )

		self.info   = jsonHelper.tryLoadJSON( self.getBasePath( _GII_INFO_FILE ) ) or {}
		self.config = jsonHelper.tryLoadJSON( self.getConfigPath( _GII_CONFIG_FILE ) ) or {}
		#load cache & assetlib
		self.cacheManager.load( _GII_ENV_CONFIG_DIR, self.envConfigPath )
		self.assetLibrary.load( _GII_ASSET_DIR, self.assetPath, self.path, self.envConfigPath )

		#will trigger other module
		signals.emitNow( 'project.preload', self )
		signals.emitNow( 'project.load', self )

		logging.info( 'project loaded: %s' % path )

		return True

	def save( self ):
		logging.info( 'saving current project' )
		signals.emitNow('project.presave', self)
		#save project info & config
		jsonHelper.trySaveJSON( self.info,   self.getBasePath( _GII_INFO_FILE ), 'project info' )

		#save asset & cache
		self.assetLibrary.save()
		self.cacheManager.clearFreeCacheFiles()
		self.cacheManager.save()

		signals.emitNow( 'project.save', self ) #post save
		logging.info( 'project saved' )
		return True

	def saveConfig( self ):
		jsonHelper.trySaveJSON( self.config, self.getConfigPath( _GII_CONFIG_FILE ), 'project config')

	def getRelativePath( self, path ):
		return os.path.relpath( path, self.path )

	def getPath( self, path = None ):
		return self.getBasePath( path )
		
	def getBasePath( self, path=None ):
		return _makePath( self.path, path)

	def getEnvPath( self, path=None ):
		return _makePath( self.envPath, path)

	def getPackagePath(self, path=None):
		return _makePath( self.envPackagePath, path)

	def getConfigPath(self, path=None):
		return _makePath( self.envConfigPath, path)

	def getBinaryPath(self, path=None):
		return _makePath( self.binaryPath, path)

	def getGamePath(self, path=None):
		return _makePath( self.gamePath, path)

	def getAssetPath(self, path=None):
		return _makePath( self.assetPath, path)

	def getScriptPath(self, path=None):
		return _makePath( self.scriptPath, path)

	def getScriptLibPath(self, path=None):
		return _makePath( self.scriptLibPath, path)

	def isProjectFile(self, path):
		path    = os.path.abspath( path )
		relpath = os.path.relpath( path, self.path )
		return not (relpath.startswith('..') or relpath.startswith('/'))

	def getConfigDict( self ):
		return self.config

	def getConfig( self, key, default = None ):
		return self.config.get( key, default )

	def setConfig( self, key, value ):
		self.config[ key ] = value
		self.saveConfig()

	def getAssetLibrary( self ):
		return self.assetLibrary

	def getCacheManager( self ):
		return self.cacheManager

Project()
