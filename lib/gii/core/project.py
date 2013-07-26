import logging
import sys
import imp
import os
import os.path
import signals

import jsonHelper
from cache import CacheManager

##----------------------------------------------------------------##
_GII_INTERNAL_PATH = '_gii'
_GII_META_PATH     = 'meta'
_GII_TOOLS_PATH    = 'tools'
_GII_INFO_PATH     = 'gii_project_info.json'
_GII_CONFIG_PATH   = 'gii_project_config.json'
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
		while path and not ( path in ( '', '/','\\' ) ):
			internalPath = path + '/' + _GII_INTERNAL_PATH
			if os.path.exists( internalPath ):
				metaPath = internalPath + '/' + _GII_META_PATH
				if os.path.exists( metaPath ):
					infoPath = metaPath + '/' + _GII_INFO_PATH
					if os.path.exists( infoPath ):
						return ( path, internalPath, metaPath )
			path = os.path.dirname( path )
		return ( None, None, None )

	def __init__(self):
		assert not Project._singleton
		Project._singleton = self

		self.path      = None
		self.toolPath  = None
		self.metaPath  = None

		self.cacheManager = CacheManager() 

		self.info = {
			'name'    : 'Name',
			'author'  : 'author',
			'version' : '1.0.0'
		}

		self.config = {}

	def _initPath( self, path ):
		self.path         = path
		self.internalPath = path + '/' + _GII_INTERNAL_PATH
		self.toolPath     = self.internalPath + '/' + _GII_TOOLS_PATH
		self.metaPath     = self.internalPath + '/' + _GII_META_PATH		

	def init( self, path ):
		prjPath, prjInternalPath, prjMetaPath = Project.findProject( path )
		if prjPath:
			raise ProjectException( 'Gii project already initialized:' + prjPath )

		path = os.path.realpath(path)
		if not os.path.isdir(path):
			raise ProjectException('%s is not a valid path' % path)
		self._initPath( path )

		#mkdir
		_mkdir( self.internalPath )
		_mkdir( self.metaPath )
		_mkdir( self.toolPath )

		try:
			self.cacheManager.init( self.metaPath )
		except OSError,e:
			raise ProjectException('error creating cache folder:%s' % e)

		signals.emitNow('project.init', self)
		logging.info( 'project initialized: %s' % path )

		self.save()
		return True	

	def load(self, path):
		path = os.path.realpath(path)
		self._initPath( path )		
		
		self.cacheManager.load( self.metaPath )

		#will trigger other module
		signals.emitNow('project.preload', self)
		signals.emitNow('project.load', self)
		logging.info( 'project loaded: %s' % path )

		return True

	def save( self ):
		signals.emitNow('project.presave', self)
		#save project info & config
		jsonHelper.trySaveJSON( self.info,   self.getMetaPath( _GII_INFO_PATH ) )
		jsonHelper.trySaveJSON( self.config, self.getMetaPath( _GII_CONFIG_PATH ) )

		self.cacheManager.clearFreeCacheFiles()
		self.cacheManager.save()
		signals.emitNow( 'project.save', self ) #post save
		logging.info( 'project saved' )
		return True

	def getRelativePath(self, path):
		return os.path.relpath(path,self.path)

	def getPath(self, path=None):
		if path:
			return os.path.abspath(self.path+'/'+path)
		else:
			return self.path

	def getInternalPath( self, path=None ):
		if path:
			return os.path.abspath(self.internalPath+'/'+path)
		else:
			return self.internalPath

	def getToolPath(self, path=None):
		if path:
			return os.path.abspath(self.toolPath+'/'+path)
		else:
			return self.toolPath

	def getMetaPath(self, path=None):
		if path:
			return os.path.abspath(self.metaPath+'/'+path)
		else:
			return self.metaPath	

	def isProjectFile(self, path):
		path = os.path.abspath( path )
		relpath = os.path.relpath( path, self.path )
		return not (relpath.startswith('..') or relpath.startswith('/'))

	def getConfigDict( self ):
		return self.config

	def getConfig( self, key, default = None ):
		return self.config.get( key, default )

	def setConfig( self, key, value ):
		self.config[ key ] = value

Project()