import logging
import sys
import imp
import os
import os.path
import re
import shutil
import sync
import hashlib

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
_GII_SCRIPT_LIB_DIR     = _GII_GAME_DIR + '/lib'

_GII_HOST_EXTENSION_DIR = _GII_HOST_DIR  + '/extension'

_GII_ENV_PACKAGE_DIR    = _GII_ENV_DIR  + '/packages'
_GII_ENV_DATA_DIR       = _GII_ENV_DIR  + '/data'
_GII_ENV_LIB_DIR        = _GII_ENV_DIR  + '/lib'
_GII_ENV_CONFIG_DIR     = _GII_ENV_DIR  + '/config'

_GII_INFO_FILE          = 'project.json'
_GII_CONFIG_FILE        = 'config.json'


####----------------------------------------------------------------##
_default_config = {
	"excluded_packages" : []
}

##----------------------------------------------------------------##
def _fixPath( path ):
		path = path.replace( '\\', '/' ) #for windows
		if path.startswith('./'): path = path[2:]
		return path	

##----------------------------------------------------------------##
def _makePath( base, path ):
	if path:
		return base + '/' + path
	else:
		return base

##----------------------------------------------------------------##
def _affirmPath( path ):
	if os.path.exists( path ): return
	try:
		os.mkdir( path )
	except Exception, e:
		pass

##----------------------------------------------------------------##
def _hashPath( path ):
	name, ext = os.path.splitext( os.path.basename( path ) )
	m = hashlib.md5()
	m.update( path.encode('utf-8') )
	return m.hexdigest()

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
				#get info
				info = jsonHelper.tryLoadJSON( path + '/' + _GII_INFO_FILE )
				info['path'] = path
				return info
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
		self.envDataPath       = path + '/' + _GII_ENV_DATA_DIR
		self.envConfigPath     = path + '/' + _GII_ENV_CONFIG_DIR
		self.envLibPath        = path + '/' + _GII_ENV_LIB_DIR

		self.assetPath         = path + '/' + _GII_ASSET_DIR

		self.scriptLibPath     = path + '/' + _GII_SCRIPT_LIB_DIR

		self.hostPath          = path + '/' + _GII_HOST_DIR
		self.hostExtensionPath = path + '/' + _GII_HOST_EXTENSION_DIR

	def _affirmDirectories( self ):
		#mkdir - lv1
		_affirmPath( self.binaryPath )

		_affirmPath( self.envPath )
		_affirmPath( self.envPackagePath )
		_affirmPath( self.envDataPath )
		_affirmPath( self.envLibPath )
		_affirmPath( self.envConfigPath )

		_affirmPath( self.gamePath )
		_affirmPath( self.assetPath )
		_affirmPath( self.scriptLibPath )
		
		_affirmPath( self.hostPath )
		_affirmPath( self.hostExtensionPath )
		
	def init( self, path, name ):
		info = Project.findProject( path )
		if info:
			raise ProjectException( 'Gii project already initialized:' + info['path'] )
		#
		path = os.path.realpath(path)
		if not os.path.isdir(path):
			raise ProjectException('%s is not a valid path' % path)
		self._initPath( path )
		#
		logging.info( 'copy template contents' )
		from MainModulePath import getMainModulePath
		def ignore( src, names ):
			return ['.DS_Store']
		shutil.copytree( getMainModulePath('template/host'), self.getPath('host'), ignore )
		shutil.copy( getMainModulePath('template/.gitignore'), self.getPath() )
		#
		self._affirmDirectories()

		try:
			self.cacheManager.init( _GII_ENV_CONFIG_DIR, self.envConfigPath )
		except OSError,e:
			raise ProjectException('error creating cache folder:%s' % e)

		self.assetLibrary.load( _GII_ASSET_DIR, self.assetPath, self.path, self.envConfigPath )

		signals.emitNow('project.init', self)
		logging.info( 'project initialized: %s' % path )
		self.info['name'] = name

		self.save()
		return True	

	def load(self, path):
		path = os.path.realpath(path)
		
		self._initPath( path )
		self._affirmDirectories()
		os.chdir( path )

		sys.path.insert( 0, self.envLibPath )
		sys.path.insert( 0, self.getBinaryPath( 'python' ) ) #for python extension modules

		self.info   = jsonHelper.tryLoadJSON( self.getBasePath( _GII_INFO_FILE ) )
		self.config = jsonHelper.tryLoadJSON( self.getConfigPath( _GII_CONFIG_FILE ) )
		if not self.config:
			self.config = {}
			jsonHelper.trySaveJSON( self.config, self.getConfigPath( _GII_CONFIG_FILE ) )

		if not self.info:
			self.info = {
				'name' : 'name',
				'version' : [0,0,1],
			}
			jsonHelper.trySaveJSON( self.info, self.getBasePath( _GII_INFO_FILE ) )
			
		self.cacheManager.load( _GII_ENV_CONFIG_DIR, self.envConfigPath )
		self.assetLibrary.load( _GII_ASSET_DIR, self.assetPath, self.path, self.envConfigPath )

		#will trigger other module
		signals.emitNow( 'project.preload', self )
		signals.emitNow( 'project.load', self )
		
		logging.info( 'project loaded: %s' % path )

		return True

	def loadAssetLibrary( self ):
		#load cache & assetlib
		self.assetLibrary.loadAssetTable()

	def deploy( self, **option ):
		base    = self.getPath( option.get( 'path', 'output' ) )
		context = DeployContext( base )
		context.cleanPath()
		hostResPath = self.getHostPath('resource')
		gameLibPath = self.getGamePath('lib')

		logging.info( 'deploy current project' )
		context.copyFilesInDir( hostResPath )
		context.copyFile( gameLibPath, 'lib' )
		signals.emitNow( 'project.pre_deploy', context )
		#deploy asset library
		objectFiles = []
				
		for node in self.assetLibrary.assetTable.values():
			mgr = node.getManager()
			if not mgr: continue
			mgr.deployAsset( node, context )
		#copy scripts
		#copy static resources
		signals.emitNow( 'project.deploy', context )
		self.assetLibrary.saveAssetTable(
				path    = base + '/asset/asset_index', 
				deploy_context  = context
			)
		context.flushTask()
		signals.emitNow( 'project.post_deploy', context )
		print( 'Deploy building done!' )
		signals.emitNow( 'project.done_deploy', context )

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
		return _fixPath( os.path.relpath( path, self.path ) )

	def getPath( self, path = None ):
		return self.getBasePath( path )
		
	def getBasePath( self, path=None ):
		return _makePath( self.path, path)

	def getEnvPath( self, path=None ):
		return _makePath( self.envPath, path)

	def getEnvDataPath( self, path=None ):
		return _makePath( self.envDataPath, path)

	def getEnvLibPath( self, path = None ):
		return _makePath( self.envLibPath, path)

	def getHostPath( self, path=None ):
		return _makePath( self.hostPath, path)

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

##----------------------------------------------------------------##
class DeployContext():

	_ignoreFilePattern = [
		'\.git',
		'\.assetmeta',
		'^\..*',
	]

	def __init__( self, path ):
		self.taskQueue   = []
		self.path        = path
		self.assetPath   = path + '/asset'
		self.fileMapping = {}
		self.meta        = {}
	
	def cleanPath( self ):
		logging.info( 'removing output path: %s' %  self.path )
		# if os.path.isdir( self.path ):
		# 	shutil.rmtree( self.path )
		_affirmPath( self.path )
		_affirmPath( self.assetPath )

	def ignorePattern( self ):
		return DeployContext._ignoreFilePattern

	def getAssetPath( self, path = None ):
		return _makePath( self.assetPath, path )

	def getPath( self, path = None ):
		return _makePath( self.path, path )

	# def getAbsPath( self, path = None):
	def addTask( self, stage, func, *args ):
		task = ( func, args )
		self.taskQueue.append( task )

	def copyFile( self, srcPath, dstPath = None, **option ):
		if not dstPath:
			dstPath = os.path.basename( srcPath )
		absDstPath = self.getPath( dstPath )
		sync.updateFile( srcPath, absDstPath )

	def copyFilesInDir( self, srcDir, dstDir = None ):
		if not os.path.isdir( srcDir ):
			raise Exception( 'Directory expected' )
		for fname in os.listdir( srcDir ):
			if self.checkFileIgnorable( fname ): continue
			fpath = srcDir + '/' + fname
			self.copyFile( fpath )

	def addFile( self, srcPath, dstPath = None, **option ):
		newPath = self.fileMapping.get( srcPath, None )
		if newPath:
			if dstPath and dstPath != newPath: 
				logging.warn( 'attempt to deploy a file with different names' )
			if not option.get( 'force', False ): return newPath
		#mapping
		if not dstPath:
			dstPath = 'asset/' + _hashPath( srcPath )
		self.fileMapping[ srcPath ] = dstPath
		#copy
		self.copyFile( srcPath, dstPath )
		return dstPath

	def getFile( self, srcPath ):
		return self.fileMapping.get( srcPath, None )

	def getAbsFile( self, srcPath ):
		return self.getPath( self.getFile( srcPath ) )

	def replaceInFile( self, srcFile, strFrom, strTo ):
		try:
			fp = open( srcFile, 'r' )
			data = fp.read()
			fp.close()
			data = data.replace( strFrom, strTo )
			fp = open( srcFile, 'w' )
			fp.write( data )
			fp.close()
		except Exception, e:
			logging.exception( e )			
		
	def flushTask( self ):
		q = self.taskQueue
		self.taskQueue = []
		for t in q:
			func, args = t
			func( *args )

	def checkFileIgnorable(self, name):
		for pattern in DeployContext._ignoreFilePattern:
			if re.match(pattern, name):
				return True
		return False
