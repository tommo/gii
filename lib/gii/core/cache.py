import os
import os.path
import logging
import hashlib
import jsonHelper

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
		return True

	def save( self ):
		#save cache index
		jsonHelper.trySaveJSON( self.cacheFileTable, self.cacheIndexPath, 'cache index' )		

	def touchCacheFile( self, cacheFile ):
		node = self.cacheFileTable.get( cacheFile, None )
		# assert node
		if not node: return
		node['touched'] = True

	def getCacheFile( self, srcPath, name = None ):
		#make a name for cachefile { hash of srcPath }	
		baseName    = name and ( srcPath + '@' + name ) or srcPath
		mangledName = _makeMangledFilePath( baseName )
		relPath     = self.cachePath + '/' + mangledName
		filePath    = self.cacheAbsPath + '/' + mangledName

		#make an new cache file
		self.cacheFileTable[ relPath ] = {
				'src'    :srcPath,
				'name'   :name,
				'file'   :mangledName,
				'touched':True
			}

		#create empty placeholder if not ready
		if not os.path.exists(filePath):
			fp = open( filePath, 'w' ) 
			fp.close()
		return relPath

	def clearFreeCacheFiles( self ):
		#check if the src file exists, if not , remove the cache file
		toRemove = []
		for path, cacheFile in self.cacheFileTable.items():
			if not cacheFile['touched']:
				toRemove.append( path )
				try:
					logging.info( 'remove cache file:' + path )
					os.remove( path )
				except Exception, e:
					pass

		for path in toRemove:
			del self.cacheFileTable[path]
