import json
import re
import os
import logging
import os.path
import weakref

from abc import ABCMeta, abstractmethod

import jsonHelper
import signals
import AssetUtils

from cache import CacheManager

GII_ASSET_INDEX_PATH = 'asset_table.json'
GII_ASSET_META_DIR   = '.assetmeta'



##----------------------------------------------------------------##
class AssetException(Exception):
	pass

##----------------------------------------------------------------##
class AssetNode(object):
	def __init__(self, nodePath, assetType='file', **kwargs):	
		if isinstance( nodePath, str ):
			nodePath = nodePath.decode('utf-8')
		
		self.nodePath   = nodePath
		self.assetType  = assetType
		self.parentNode = None

		self.metadata   = None

		self.name = os.path.basename( nodePath )
		
		self.children = []
		self.dependency     = {}     #runtime level dependency
		self.depBy   = {}     #runtime level dependency

		self.cacheFiles  = {}
		self.objectFiles = {}

		self.deployState = None
		self.modifyState = 'new'		

		self.filePath = kwargs.get( 'filePath', nodePath )
		self.fileTime = kwargs.get( 'fileTime', 0 )
		manager = kwargs.get( 'manager', None )
		if isinstance( manager, AssetManager ):
			self.managerName = manager.getName()
		else:
			self.managerName = manager

		self.properties={}		

	def __repr__(self):	
		return u'<{0}>{1}'.format( self.getType(), self.getNodePath() ).encode('utf-8')		

	def getType(self):
		return self.assetType

	def isType(self, *typeNames ):
		return self.assetType in list( typeNames )

	def getManager(self):
		return AssetLibrary.get().getAssetManager( self.managerName, True )

	def getName(self):
		return self.name

	def getBaseName(self):
		name, ext = os.path.splitext(self.name)
		return name

	def getPathDepth(self):
		return self.nodePath.count('/')

	def getPath(self):
		return self.nodePath	

	def getDir(self):
		return os.path.dirname( self.getNodePath() )

	def getFileDir( self ):
		return os.path.dirname( self.getFilePath() )

	def isRegistered( self ):
		return AssetLibrary.get().hasAssetNode( self.nodePath )

	def getSiblingPath(self,name):
		if self.getDir():
			return self.getDir() + '/' + name
		else:
			return name

	def getSiblingFilePath( self, name ):
		if self.getFileDir():
			return self.getFileDir() + '/' + name
		else:
			return name

	def getChildPath(self, name):
		path = self.getPath()
		if path:
			return path + '/' + name
		else:
			return name

	def getNodePath(self):
		return self.nodePath

	def isVirtual(self):
		if self.filePath: return False
		return True

	def getSibling(self, name):
		return self.parentNode.getChild(name)

	def getChild(self, name):
		for n in self.children:
			if n.getName() == name:
				return n
		return None

	def hasChild(self):
		return len(self.children)>0

	def getParent(self):
		return self.parentNode

	def addChild(self, node):
		self.children.append(node)
		node.parentNode = self
		return node

	def affirmChildNode( self, name, assetType, **kwargs ):
		node = self.getChild( name )
		if not node:
			return self.createChildNode( name, assetType, **kwargs )
		node.modifyState = False
		return node

	def createChildNode(self, name, assetType, **kwargs):
		path = self.nodePath + '/' + name
		if not kwargs.has_key('filePath'): kwargs['filePath'] = False
		node = AssetNode(path, assetType, **kwargs)
		self.addChild( node )

		if self.isRegistered():
			AssetLibrary.get().registerAssetNode( node )
		else:
			#will be registered along with parent node
			pass
		return node

	def setBundle( self, isBundle = True ):
		self.setProperty( 'is_bundle', isBundle )
		if isBundle:
			pass

	def isBundle( self ):
		return self.getProperty( 'is_bundle', False )

	def setManager(self, assetManager, forceReimport=False):
		prevManager = self.getManager()
		if prevManager != assetManager:
			prevManager.forgetAsset( self )
			self.managerName = assetManager.getName()
		#TODO: validation? reimport?

	def removeChild(self, node):
		idx=self.children.index(node)
		self.children.pop(idx)
		node.parentNode=None

	def addDependency( self, key, depNode ):
		self.dependency[ key ] = depNode.getNodePath()
		depNode.depBy[ self.getNodePath() ] = True

	def removeDependency( self, key ):
		depPath = self.dependency.get( key, None )
		if not depPath: return
		lib  = AssetLibrary.get()
		dep = lib.getAssetNode( depPath )
		if dep:
			del dep.depBy[ self.getNodePath() ]
		del self.dependency[ key ]

	def clearDependency( self ):
		lib  = AssetLibrary.get()
		path = self.getNodePath()
		for key, depPath in self.dependency.items():
			dep = lib.getAssetNode( depPath )
			if dep:
				del dep.depBy[ path ]
		self.dependency.clear()

	def getDependency( self, key ):
		return self.dependency.get( key, None )
		
	def getDependencyNode( self, key ):
		path = self.dependency.get( key, None )
		return path and AssetLibrary.get().getAssetNode( path )

	def findDependencyKey( self, node ):
		path = node.getNodePath()
		for k, v in self.dependency.items():
			if v==path: return k
		return None

	def getDeployState(self):
		if self.deployState == False:
			return False
		if self.deployState == True:
			return True
		if not self.parentNode: return None		#root
		pstate = self.parentNode.getDeployState()
		if pstate == False: return False
		if pstate: return 'parent'
		lib = AssetLibrary.get()
		for nodePath in self.depBy:
			node = lib.getAssetNode( nodePath )
			if node and node.getDeployState():
				return 'dependency'
		return None

	def setDeployState(self, state):
		if self.deployState == state: return
		self.deployState = state
		signals.emit('asset.deploy.changed', self)

	def markModified( self ):
		if self.modifyState == 'new': return
		logging.info( 'mark modified: %s', repr(self) )
		manager = self.getManager()
		if manager:
			manager.markModified( self )
		else:
			self.modifyState = 'modified'

	def touch( self ):
		fname = self.getAbsFilePath()
		if fname:
			if os.path.isfile( fname ):
				with file(fname, 'a'):
					os.utime(fname, None)

	def getFilePath(self):
		return self.filePath

	def getAbsDir(self):
		return os.path.dirname( self.getAbsFilePath() )

	def getAbsFilePath(self):
		if self.filePath:
			return AssetLibrary.get().getAbsProjectPath( self.filePath )
		else:
			return ''

	def getFileTime(self):
		return self.fileTime

	def getChildren(self):
		return self.children

	def getChildrenCount(self):
		return len(self.children)

	#TODO: add metadata support for virtual node ?
	def getMetaDataTable( self, createIfEmpty = True ):
		if self.isVirtual(): return None
		if self.metadata: return self.metadata
		dirname  = self.getAbsDir()
		metaDir  = dirname + '/' +GII_ASSET_META_DIR
		metaPath = metaDir + '/' + self.getName() + '.meta'
		if os.path.exists( metaPath ):
			data = jsonHelper.tryLoadJSON( metaPath )
			self.metadata = data or {}			
			return self.metadata
		elif  createIfEmpty:
			self.metadata = {}
			return self.metadata
		return None

	def saveMetaDataTable( self ):
		if not self.metadata: return False
		dirname  = self.getAbsDir()
		metaDir  = dirname + '/' + GII_ASSET_META_DIR
		metaPath = metaDir + '/' + self.getName() + '.meta'
		if not os.path.exists( metaDir ):
			os.mkdir( metaDir )
		text = json.dumps( self.metadata, indent = 2, sort_keys = True )
		fp = open( metaPath, 'w' )
		fp.write( text )
		fp.close()
		return True

	def findNonVirtualParent( self ):
		node = self.getParent()
		while node:
			if not node.isVirtual(): return node
			node = node.getParent()
		return None

	def getMetaData( self, key, defaultValue = None ):
		if self.isVirtual():
			p = self.findNonVirtualParent()
			if p:
				profix = os.path.relpath( self.getNodePath(), p.getNodePath() )
				subkey = '%s@%s' % ( key, profix )
				return p.getMetaData( subkey, defaultValue )
		else:
			t = self.getMetaDataTable( False )
			if not isinstance( t, dict ): return defaultValue
			return t.get( key, defaultValue )

	def setMetaData( self, key, value, **option ):
		if self.isVirtual():
			p = self.findNonVirtualParent()
			if p:
				profix = os.path.relpath( self.getNodePath(), p.getNodePath() )
				subkey = '%s@%s' % ( key, profix )
				return p.setMetaData( subkey, value, **option )
		else:
			t = self.getMetaDataTable()
			if not isinstance( t, dict ): return
			if option.get( 'no_overwrite', False ) and t.has_key( key ):
				return
			v0 = t.get( key, None )
			if v0 != value:
				t[ key ] = value
				if option.get( 'save', False ): self.saveMetaDataTable()
				if option.get( 'mark_modify', True ): self.markModified()

	def setNewMetaData( self, key, value, **option ):
		option[ 'no_overwrite' ] = True
		return self.setMetaData( key, value, **option )

	def getCacheFile( self, name, **option ):
		cacheFile = self.cacheFiles.get( name, None )
		if cacheFile: return cacheFile
		cacheFile = CacheManager.get().getCacheFile( self.getPath(), name, **option )
		self.cacheFiles[ name ] = cacheFile
		return cacheFile

	def getAbsCacheFile( self, name, **option ):
		path = self.getCacheFile( name, **option )
		if not path: return None
		return AssetLibrary.get().getAbsProjectPath( path )

	def clearCacheFiles( self ):
		self.cacheFiles = {}

	def checkCacheFiles( self ):
		for id, path in self.cacheFiles.items():
			fullpath = AssetLibrary.get().getAbsProjectPath( path )
			if not os.path.exists( fullpath ): return False
		return True

	def getObjectFile(self, name):
		return self.objectFiles.get( name, None )

	def setObjectFile(self, name, path):
		if not path:
			if self.objectFiles.has_key( name ):
				del self.objectFiles[ name ]
		else:
			self.objectFiles[ name ] = path		

	def getAbsObjectFile( self, name ):
		path = self.getObjectFile( name )
		if not path: return None
		return AssetLibrary.get().getAbsProjectPath( path )

	def clearObjectFiles( self ):
		self.objectFiles = {}
		
	def edit(self):
		self.getManager().editAsset(self)

	def getProperty(self, name, defaultValue=None ):
		return self.properties.get(name, defaultValue)

	def setProperty(self, name, value):
		self.properties[ name ] = value

	def showInBrowser(self):
		path = self.getAbsFilePath()
		if path:
			AssetUtils.showFileInBrowser(path)

	def openInSystem(self):
		path = self.getAbsFilePath()
		if path:
			AssetUtils.openFileInOS(path)

	def _updateFileTime( self, mtime = None ):
		if self.isVirtual(): return
		self.fileTime = mtime or os.path.getmtime( self.getAbsFilePath() )

	#just a shortcut for configuration type asset
	def loadAsJson(self):
		if self.isVirtual(): return None
		filepath = self.getAbsFilePath()

		fp = open(filepath , 'r')
		text = fp.read()
		fp.close()
		data = json.loads(text)

		return data

	def saveAsJson(self, data):
		if self.isVirtual(): return False
		filepath = self.getAbsFilePath()

		text = json.dumps( data, indent = 2, sort_keys = True )
		fp = open(filepath , 'w')
		fp.write(text)
		fp.close()

		self.markModified()
		return True


##----------------------------------------------------------------##
class AssetManager(object):	
	def getName(self):
		return 'asset_manager'

	def __lt__(self, other):
		return other.getPriority() < self.getPriority()

	def register( self ):
		AssetLibrary.get().registerAssetManager( self )

	def getPriority(self):
		return 0

	def acceptAsset( self, assetNode ):
		if assetNode.isVirtual():
			return self.acceptVirtualAsset( assetNode )
		else:
			return self.acceptAssetFile( assetNode.getAbsFilePath() )

	def acceptVirtualAsset( self, assetNode ):
		if assetNode.getManager() == self: return True
		return False

	def acceptAssetFile(self, filepath):
		return False

	def importAsset(self, assetNode, reload = False):
		return None
	
	def forgetAsset( self, assetNode ):
		pass

	def removeAsset( self, assetNode ):
		pass

	def cloneAsset( self, assetNode ):
		pass

	#Process asset for deployment. eg.  Filepath replace, Extern file collection
	def deployAsset( self, assetNode, context ):
		for k, path in assetNode.objectFiles.items():
			if path:
				context.addFile( path )

	def editAsset(self, assetNode):
		assetNode.openInSystem()

	def buildThumbnail( self, assetNode ):
		return None

	def markModified( self, assetNode ):
		assetNode.modifyState = 'modified'
		for child in assetNode.getChildren():
			child.markModified()

	def getDependency( self, assetNode ):
		pass

	def onRegister( self ):
		pass

	def getMetaType( self ):
		return None

##----------------------------------------------------------------##
class RawAssetManager(AssetManager):	
	def getName(self):
		return 'raw'

	def getPriority( self ):
		return -1

	def acceptAssetFile(self, filepath):
		return True

	def importAsset(self, assetNode, reload = False ):
		path = os.path.realpath( assetNode.getAbsFilePath() )
		if os.path.isfile( path ): 
			assetNode.assetType = 'file'
		elif os.path.isdir( path ):
			assetNode.assetType = 'folder'
		return True

	def markNotified(self, assetNode ):
		pass #do nothing

##----------------------------------------------------------------##
class AssetCreator(object):
	__metaclass__ = ABCMeta

	@abstractmethod
	def getAssetType( self ):
		return 'name'

	@abstractmethod
	def getLabel( self ):
		return 'Label'

	def register( self ):
		return AssetLibrary.get().registerAssetCreator( self )

	def createAsset(self, name, contextNode, assetType):
		return False


##----------------------------------------------------------------##
class AssetLibrary(object):
	"""docstring for AssetLibrary"""
	_singleton=None

	@staticmethod
	def get():
		return AssetLibrary._singleton

	def __init__(self):
		assert not AssetLibrary._singleton
		AssetLibrary._singleton=self
		self.projectScanScheduled = False
		self.cacheScanned    = False

		self.assetTable      = {}
		self.assetManagers   = []
		self.assetCreators   = []

		self.rawAssetManager = RawAssetManager()
		
		self.rootPath        = None

		self.assetIconMap    = {}

		self.ignoreFilePattern = [
			'\.git',
			'\.assetmeta',
			'^\..*',
			'.*\.pyo$',
			'.*\.pyc$'
		]

	def load( self, rootPath, rootAbsPath, projectAbsPath, configPath ):
		#load asset
		self.rootPath       = rootPath
		self.rootAbsPath    = rootAbsPath
		self.projectAbsPath = projectAbsPath
		self.assetIndexPath = configPath + '/' +GII_ASSET_INDEX_PATH
		self.rootNode       = AssetNode( '', 'folder', filePath = self.rootPath )
		# self.loadAssetTable()		

	def save( self ):
		self.saveAssetTable()

	def reset( self ):
		signals.emit( 'asset.reset' )
		self.unregisterAssetNode( self.rootNode )
		self.scanProject()

	def getRootNode(self):
		return self.rootNode

	#Path
	def getAbsPath( self, path ):
		return self.rootAbsPath + '/' + path

	def getAbsProjectPath( self, path ):
		return self.projectAbsPath + '/' + path

	def getRelPath( self, path ):
		path = os.path.abspath( path )
		return os.path.relpath( path, self.rootAbsPath )

	#access
	def hasAssetNode(self, nodePath):
		if not nodePath: return False
		return not self.getAssetNode( nodePath ) is None

	def getAssetNode(self, nodePath):
		if not nodePath: return self.rootNode
		return self.assetTable.get(nodePath, None)

	def findAssetNode( self, nodePathPattern ):
		pass

	def enumerateAsset( self, patterns, **options ):
		noVirtualNode = options.get( 'no_virtual', False )
		result = []
		#all
		if not patterns:
			for path, node in self.assetTable.items():
				if ( noVirtualNode and node.isVirtual() ) : continue
				result.append( node )
			return result
		#match patterns
		if isinstance( patterns, ( str, unicode ) ):
			patterns = patterns.split(';')
		matchPatterns = []
		for p in patterns:
			pattern = re.compile( p )
			matchPatterns.append( pattern )
		for path, node in self.assetTable.items():
			if ( noVirtualNode and node.isVirtual() ) : continue
			for matchPattern in matchPatterns:
				mo = matchPattern.match( node.getType() )
				if not mo: continue
				if mo.end() < len( node.getType() ) - 1 : continue
				result.append(node)
				break
		return result

	#tools
	def checkFileIgnorable(self, name):
		for pattern in self.ignoreFilePattern:
			if re.match(pattern, name):
				return True
		return False

	def fixPath( self, path ):
		path = path.replace( '\\', '/' ) #for windows
		if path.startswith('./'): path = path[2:]
		return path

	#Assetmanagers
	def registerAssetManager(self, manager):
		logging.info( 'registering asset manager:'+manager.getName() )
		for p in self.assetManagers:
			if p == manager:
				raise AssetException('Duplicated AssetManager %s'%manager.getName())

			if p.getPriority() <= manager.getPriority():
				idx = self.assetManagers.index(p)
				self.assetManagers.insert(idx, manager)
				return manager

		self.assetManagers.append(manager)
		manager.onRegister()
		return manager

	def registerAssetCreator(self, creator):
		self.assetCreators.append( creator )

	def getAssetManager(self, name, allowRawManager = False ):
		for mgr in self.assetManagers:
			if mgr.getName()==name:
				return mgr
		return allowRawManager and self.rawAssetManager or None

	def getAssetIcon( self, assetType ):
		return self.assetIconMap.get( assetType, assetType )

	def setAssetIcon( self, assetType, iconName ):
		self.assetIconMap[ assetType ] = iconName

	def registerAssetNode( self, node ):
		path = node.getNodePath()
		logging.info( 'register: %s' % repr(node) )
		if self.assetTable.has_key(path):
			raise Exception( 'unclean path: %s', path)
		self.assetTable[path]=node

		signals.emit( 'asset.register', node )

		for child in node.getChildren():
			self.registerAssetNode(child)

		return node

	def unregisterAssetNode(self, oldnode):
		assert oldnode
		logging.info( 'unregister: %s' % repr(oldnode) )
		
		for child in oldnode.getChildren()[:]:
			self.unregisterAssetNode(child)

		if oldnode != self.rootNode:
			oldnode.getManager().forgetAsset( oldnode )
			signals.emitNow('asset.unregister', oldnode)
			if oldnode.parentNode: 
				oldnode.parentNode.removeChild(oldnode)
				oldnode.parentNode = None
			path = oldnode.getNodePath()
			del self.assetTable[path]
			assert not self.assetTable.has_key(path)	

	def initAssetNode( self, path, option = None, **kwargs ):
		#fix path
		absFilePath = os.path.abspath( self.rootAbsPath + '/' + path )
		fileTime = os.path.getmtime(absFilePath)
		filePath = self.rootPath + '/' + path
		
		#if inside bundle, skip
		if self._getParentBundle( path ): return None

		assert not self.getAssetNode( path )
		#create a common asset node first
		parentNode = self.getAssetNode( os.path.dirname( path ) )

		node = AssetNode( 
			path,
			os.path.isfile(absFilePath) and 'file' or 'folder', 
			fileTime = fileTime,
			filePath = filePath,
			**kwargs )
		node.setManager( self.rawAssetManager )
		self.registerAssetNode( node )
		parentNode.addChild(node)	
		node.markModified()

		return node

	def reimportAll(self):
		#TODO:should this be done by a asset index rebuilding (by restarting editor)?
		pass

	def importModifiedAssets( self ):
		def _ignoreBundleChildrenNode( node ):
			for child in node.getChildren()[:]:
				if not child.isVirtual():
					_ignoreBundleChildrenNode( child )
					child.modifyState = 'ignored'
					self.unregisterAssetNode( child )

		def _markVirtualChildrenRemoving( node, removingAssets ):			
			for child in node.getChildren()[:]:
				if child.isVirtual():
					_markVirtualChildrenRemoving( child, removingAssets )
					child.modifyState = 'removing'
					removingAssets[ child ] = True

		#collect modified state
		removingAssets = {}
		modifiedAssetList = []
		for node in self.assetTable.values():
			if node.modifyState and not node.isVirtual():
				modifiedAssetList.append( node )
				logging.info( u'asset modified: {0}'.format( node.getNodePath() ) )
		modifiedAssetList = sorted( modifiedAssetList, key = lambda node: node.getPathDepth() )
		#try importing with each asset manager, in priority order
		for manager in self.assetManagers:
			if not modifiedAssetList: break
			done = []
			rest = []
			for node in modifiedAssetList:
				if node.modifyState in ( 'removed', 'ignored' ) :
					done.append( node )
					continue
				if not node.modifyState: #might get imported as a sub asset 
					done.append( node )
					continue
				if not manager.acceptAsset( node ):
					rest.append( node )
					continue
				
				isNew = node.modifyState == 'new'
				if not isNew:
					_markVirtualChildrenRemoving( node, removingAssets )

				if node.getManager() != manager: node.setManager( manager )
				if manager.importAsset( node, reload = not isNew ) != False:
					logging.info( u'assets imported: {0}'.format( node.getNodePath() ) )
					node.modifyState  =  False
					done.append( node )
				else:
					rest.append( node )

				if not isNew:
					signals.emitNow( 'asset.modified',  node )
					# if node.isBundle():
					for child in node.children:
						signals.emitNow( 'asset.modified', child )

				if node.isBundle():
					_ignoreBundleChildrenNode( node )
					
			for node in done:				
				if node.modifyState == 'ignored': continue
				if node.isBundle():
					node._updateFileTime( self._getBundleMTime( node.getAbsFilePath() ) )					
				else:
					node._updateFileTime()
			modifiedAssetList = rest
			rest = []

		for node in modifiedAssetList: #nodes without manager
			if node.isBundle():
				node._updateFileTime( self._getBundleMTime( node.getAbsFilePath() ) )					
			else:
				node._updateFileTime()

		for node in removingAssets.keys():
			if node.modifyState == 'removing':
				self.unregisterAssetNode( node )
				node.modifyState = 'removed'

		#end of for
		signals.emitNow( 'asset.post_import_all' )
		logging.info( 'modified assets imported' )

	def scheduleScanProject( self ):
		self.projectScanScheduled = True
		pass

	def tryScanProject( self ):
		if self.projectScanScheduled:
			self.scanProject()
			
	#Library
	def scanProject(self): #scan 
		self.projectScanScheduled = False
		logging.info('scan project in:' + self.rootAbsPath )
		#scan meta files first ( will be used in asset importing )
		#TODO
		#check missing asset
		for assetPath, node in self.assetTable.copy().items():
			if not self.assetTable.has_key( assetPath ): #already removed(as child of removed node)
				continue
			#check parentnode
			if not node.getParent():
				self.unregisterAssetNode( node )
				continue

			if node.isVirtual(): #don't check virtual node's file
				continue

			filePath = node.getAbsFilePath()
			#file deleted
			if not os.path.exists( filePath ):
				node.modifyState = 'removed'
				self.unregisterAssetNode( node )
				continue
			#file become ignored
			if self.checkFileIgnorable( filePath ):
				node.modifyState = 'ignored'
				self.unregisterAssetNode( node )
				continue

		#check new asset
		for currentDir, dirs, files in os.walk( unicode(self.rootAbsPath) ):
			relDir = os.path.relpath( currentDir, self.rootAbsPath )

			for filename in files:
				if self.checkFileIgnorable(filename):
					continue
				
				nodePath = self.fixPath( relDir + '/' + filename )
				absPath  = self.getAbsPath( nodePath )
				mtime    = os.path.getmtime( absPath )
				bundle   = self._getParentBundle( nodePath )

				if bundle:
					if mtime > bundle.getFileTime():
						bundle.markModified()
					if not bundle.checkCacheFiles():
						bundle.markModified()
				else:
					if not self.getAssetNode( nodePath ): #new
						self.initAssetNode( nodePath )
					else:
						node = self.getAssetNode( nodePath ) #modified
						if mtime > node.getFileTime():
							node.markModified()
						if not node.checkCacheFiles():
							node.markModified()

			dirs2 = dirs[:]
			for dirname in dirs2:
				if self.checkFileIgnorable(dirname):
					dirs.pop(dirs.index(dirname)) #skip walk this
					continue
				nodePath = self.fixPath( relDir + '/' + dirname )
				if not self.getAssetNode( nodePath ):
					self.initAssetNode( nodePath )	

		self.importModifiedAssets()
		self.saveAssetTable()
		CacheManager.get().save()
	
	def buildProject( self ):
		pass

	def loadAssetTable(self):

		logging.info( 'loading asset table from:' + self.assetIndexPath )
		
		if not os.path.exists( self.assetIndexPath ): return
		dataTable = jsonHelper.tryLoadJSON( self.assetIndexPath )

		if not dataTable: return False
		
		assetTable={}

		for path,data in dataTable.items():
			node = AssetNode(path, data.get('type').encode('utf-8'), 
					filePath = data.get( 'filePath', path ),
					fileTime = data.get( 'fileTime', 0 )
				)
			node.deployState  = data.get('deploy', None)
			node.cacheFiles   = data.get('cacheFiles', {})
			node.objectFiles  = data.get('objectFiles', {})
			node.properties   = data.get('properties', {}) 
			node.modifyState  =	data.get('modifyState' ,  False )
			
			assetTable[path]  = node
			node.managerName  = data.get('manager')
			
		#relink parent/dependency
		for path, node in assetTable.items():
			ppath = os.path.dirname(path)
			if not ppath:
				pnode = self.rootNode
			else:
				pnode = assetTable.get(ppath,None)
			if not pnode:
				continue
			pnode.addChild(node)
			data = dataTable[path]

			for key, dpath in data.get( 'dependency', {} ).items() :
				dnode = assetTable[dpath]
				if not dnode:
					logging.warn('missing dependency asset node', dpath )
					node.markModified()
				else:
					node.addDependency( key, dnode )

		self.assetTable=assetTable
		logging.info("asset library loaded")

	def saveAssetTable( self, **option ):
		outputPath = option.get( 'path', self.assetIndexPath )		
		deployContext  = option.get( 'deploy_context',  False )
		mapping = deployContext and deployContext.fileMapping
		table={}
		for path, node in self.assetTable.items():
			item={}
			table[ path ]=item
			#common
			item['type']        = node.getType()
			item['filePath']    = node.getFilePath() or False
			#oebjectfiles
			if mapping:
				mapped = {}
				for key, path in node.objectFiles.items():
					mapped[ key ] = mapping.get( path, path )
				item['objectFiles'] = mapped
			else:
				item['objectFiles'] = node.objectFiles

			item['dependency']  = node.dependency
			item['fileTime']    = node.getFileTime()
			#non deploy information
			if not deployContext:
				item['manager']     = node.managerName
				item['deploy']      = node.deployState
				item['cacheFiles']  = node.cacheFiles
				item['properties']  = node.properties
		 		item['modifyState'] = node.modifyState
				#mark cache files
				for name, cacheFile in node.cacheFiles.items():
					CacheManager.get().touchCacheFile( cacheFile )
				node.saveMetaDataTable()	

		if not jsonHelper.trySaveJSON( table, outputPath, 'asset index' ):
			return False
		logging.info( 'asset table saved' )
		return True	

	def clearFreeMetaData( self ):
		#check new asset
		for currentDir, dirs, files in os.walk( unicode(self.rootPath) ):
			dirs2=dirs[:]
			for dirname in dirs2:
				if self.checkFileIgnorable(dirname):
					dirs.pop(dirs.index(dirname)) #skip ignored files
					continue

			relDir  = os.path.relpath(currentDir, self.rootPath)
			metaDir = currentDir + '/' + GII_ASSET_META_DIR

			if os.path.exists( metaDir ):
				for filename in os.listdir( metaDir ):
					if not filename.endswith('.meta'): continue
					assetName = filename [:-5] #remove '.meta'
					assetPath = currentDir + '/' +assetName
					if not os.path.exists( assetPath ):
						metaPath = metaDir + '/' +filename
						logging.info( 'remove metadata: %s' % metaPath )
						os.remove( metaPath )
				#TODO: remove meta folder if it's empty

	def _getParentBundle ( self, path ):
		while True:
			path1 = os.path.dirname(path)
			if not path1 or path1 == path: return None
			path  = path1
			pnode = self.getAssetNode( path )
			if pnode and pnode.isBundle(): return pnode

	def _getBundleMTime( self, path ):
		mtime = 0
		for currentDir, dirs, files in os.walk( path ):
			for filename in files:
				if self.checkFileIgnorable(filename):
					continue
				mtime1 = os.path.getmtime( currentDir + '/' + filename )
				if mtime1 > mtime:
					mtime = mtime1
			dirs2 = dirs[:]
			for dirname in dirs2:
				if self.checkFileIgnorable(dirname):
					dirs.pop(dirs.index(dirname)) #skip walk this
					continue
				mtime1 = os.path.getmtime( currentDir + '/' + dirname )
				if mtime1 > mtime:
					mtime = mtime1
		return mtime
