import os
import os.path
import logging
import hashlib
import jsonHelper
import shutil

from tmpfile import TempDir

_GII_CACHE_PATH       =  'cache'
_GII_CACHE_INDEX_PATH =  'cache_index.json'


##----------------------------------------------------------------##
def _makeMangledFilePath( path ):
	name, ext = os.path.splitext( os.path.basename( path ) )
	m = hashlib.md5()
	m.update( path.encode('utf-8') )
	return name + '_' + m.hexdigest()

##----------------------------------------------------------------##
class CacheManager(object):
	_singleton = None
	
	@staticmethod
	def get():
		return CacheManager._singleton

	def __init__( self ):
		assert not CacheManager._singleton
		CacheManager._singleton = self

		super(CacheManager, self).__init__()
		self.cachePath      = None
		self.cacheAbsPath   = None
		self.cacheIndexPath = None
		self.cacheFileTable = {} 

	def init( self, basePath, absBasePath ):
		self.cachePath      = basePath + '/' + _GII_CACHE_PATH
		self.cacheAbsPath   = absBasePath + '/' + _GII_CACHE_PATH
		self.cacheIndexPath = absBasePath + '/' + _GII_CACHE_INDEX_PATH
		if not os.path.exists( self.cacheAbsPath ):
			os.mkdir( self.cacheAbsPath )
		return True
		
	def load( self, basePath, absBasePath ):
		self.cachePath      = basePath + '/' + _GII_CACHE_PATH
		self.cacheAbsPath   = absBasePath + '/' + _GII_CACHE_PATH
		self.cacheIndexPath = absBasePath + '/' + _GII_CACHE_INDEX_PATH
		#check and create cache path exists ( for safety )
		if not os.path.exists( self.cacheAbsPath ):
			os.mkdir( self.cacheAbsPath )
		#load cache file index
		self.cacheFileTable = jsonHelper.tryLoadJSON( self.cacheIndexPath ) or {}
		for path, node in self.cacheFileTable.items():
			node[ 'touched' ] = False

		return True

	def save( self ):
		#save cache index
		jsonHelper.trySaveJSON( self.cacheFileTable, self.cacheIndexPath, 'cache index' )		

	def touchCacheFile( self, cacheFile ):
		logging.debug( 'touch cache file:'+ cacheFile )
		node = self.cacheFileTable.get( cacheFile, None )
		# assert node
		if not node: 
			logging.warn( 'no cache found:' + cacheFile )
			return
		node['touched'] = True


	def getCacheFile( self, srcPath, name = None, **option ):
		#make a name for cachefile { hash of srcPath }	
		baseName    = srcPath
		if name: baseName += '@' + name
		mangledName = _makeMangledFilePath( baseName )
		relPath     = self.cachePath + '/' + mangledName
		filePath    = self.cacheAbsPath + '/' + mangledName
		isDir       = option.get( 'is_dir',  False )

		#make an new cache file
		self.cacheFileTable[ relPath ] = {
				'src'     : srcPath,
				'name'    : name,
				'file'    : mangledName,
				'touched' : True,
				'is_dir'  : isDir
			}

		if isDir:
			if os.path.isfile( filePath ):
				os.remove( filePath )
			if not os.path.exists(filePath):
				os.mkdir( filePath )
		else:
			#create empty placeholder if not ready
			if os.path.isdir( filePath ):
				shutil.rmtree( filePath )
			if not os.path.exists(filePath):
				fp = open( filePath, 'w' ) 
				fp.close()

		return relPath

	def getCacheDir( self, srcPath, name = None ):
		return self.getCacheFile( srcPath, name, is_dir = True )

	def clearFreeCacheFiles( self ):
		#check if the src file exists, if not , remove the cache file
		logging.info( 'removing free cache file/dir' )
		toRemove = []
		for path, cacheFile in self.cacheFileTable.items():
			if not cacheFile['touched']:
				toRemove.append( path )
				logging.info( 'remove cache file/dir:' + path )
				if cacheFile.get( 'is_dir', False ):
					try:
						shutil.rmtree( path )
					except Exception, e:
						logging.error( 'failed removing cache directory:' + path )
				else:
					try:
						os.remove( path )
					except Exception, e:
						logging.error( 'failed removing cache file:' + path )

		for path in toRemove:
			del self.cacheFileTable[path]

	def getTempDir( self ):
		return TempDir()
