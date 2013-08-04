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
		self.rDep     = {}     #runtime level dependency
		self.pDep     = {}		 #project level dependency
		self.rDepBy   = {}     #runtime level dependency
		self.pDepBy   = {}		 #project level dependency

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

		self.accessPriority = 0

		self.properties={}		

	def __repr__(self):	
		return u'<{0}>{1}'.format( self.getType(), self.getNodePath() ).encode('utf-8')
		# p = self.getNodePath()
		# t = self.getType()
		# if isinstance( p, unicode ):
		# 	p = p.encode('utf-8')
		# if isinstance( t, unicode ):
		# 	t = t.encode('utf-8')
		# return '<%s>%s'%( t, p )

	def getType(self):
		return self.assetType

	def isType(self, typeName):
		if isinstance(typeName,(list, tuple)):
			return self.assetType in typeName
		else:
			return self.assetType == typeName

	def getManager(self):
		return AssetLibrary.get().getAssetManager( self.managerName, True )

	def getName(self):
		return self.name

	def getBaseName(self):
		name, ext = os.path.splitext(self.name)
		return name

	def getPath(self):
		return self.nodePath	

	def getDir(self):
		return os.path.dirname(self.getNodePath())

	def isRegistered( self ):
		return AssetLibrary.get().hasAssetNode( self.nodePath )

	def getSiblingPath(self,name):
		if self.getDir():
			return self.getDir() + '/' + name
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

	def addDependencyP(self, depNode):
		self.pDep[depNode]=True
		depNode.pDepBy[self]=True

	def addDependencyR(self, depNode):
		self.rDep[depNode]=True
		depNode.rDepBy[self]=True

	def hasDependency(self, depNode):
		return self.pDep.has_key(depNode) or self.rDep.has_key(depNode)

	def getDeployState(self):
		if self.deployState == False:
			return False
		if self.deployState == True:
			return True
		if not self.parentNode: return None		#root
		pstate = self.parentNode.getDeployState()
		if pstate == False: return False
		if pstate: return 'parent'
		for node in self.rDepBy:
			s = node.getDeployState()
			if s:
				return 'dep'
		return None

	def setDeployState(self, state):
		if self.deployState == state: return
		self.deployState = state
		signals.emit('asset.deploy.changed', self)

	def markModified( self ):
		self.modifyState = 'modified'

	def getFilePath(self):
		return self.filePath

	def getAbsDir(self):
		return os.path.dirname( self.getAbsFilePath() )

	def getAbsFilePath(self):
		if self.filePath:
			return AssetLibrary.get().projectAbsPath + '/' + self.filePath
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
			fp = open( metaPath, 'r' )
			text = fp.read()
			fp.close()
			data = json.loads( text )
			self.metadata = data
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

	def getMetaData( self, key, defaultValue = None ):
		t = self.getMetaDataTable( False )
		if not isinstance( t, dict ): return defaultValue
		return t.get( key, defaultValue )

	def setMetaData( self, key, value, **option ):
		t = self.getMetaDataTable()
		if not isinstance( t, dict ): return
		if option.get( 'no_overwrite', False ) and t.has_key( key ):
			return
		t[ key ] = value
		if option.get( 'save', False ): self.saveMetaDataTable()
		if option.get( 'mark_modify', True ): self.markModified()

	def setNewMetaData( self, key, value, **option ):
		option[ 'no_overwrite' ] = True
		return self.setMetaData( key, value, **option )
		

	def getCacheFile( self, name ):
		cacheFile = self.cacheFiles.get( name, None )
		if cacheFile: return cacheFile
		cacheFile = CacheManager.get().getCacheFile( self.getPath(), name )
		self.cacheFiles[ name ] = cacheFile
		return cacheFile

	def clearCacheFiles( self ):
		self.cacheFiles = {}

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

	def edit(self):
		self.getManager().editAsset(self)

	def getProperty(self, name, defaultValue=None ):
		return self.properties.get(name, defaultValue)

	def setProperty(self, name, value):
		self.properties[ name ] = value

	def forceReimport(self):
		self.getManager().reimportAsset(self) 
		signals.emitNow( 'asset.modified' ,  self )
		self.saveMetaDataTable()

	def showInBrowser(self):
		path = self.getAbsFilePath()
		if path:
			AssetUtils.showFileInBrowser(path)

	def openInSystem(self):
		path = self.getAbsFilePath()
		if path:
			AssetUtils.openFileInOS(path)

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

	def acceptAssetFile(self, filepath):
		return False

	def importAsset(self, assetNode, option = None):
		return None

	def reimportAsset(self, assetNode, option = None):
		lib = AssetLibrary.get()
		for n in assetNode.getChildren()[:]:
			lib.unregisterAssetNode(n)
		result = self.importAsset(assetNode, option)
		if result: 
			assetNode.modifyState  =  False
			return True
		else:
			return False

	def forgetAsset( self, assetNode ):
		pass

	#Process asset for deployment. eg.  Filepath replace, Extern file collection
	def deployAsset( self, assetNode ):
		#TODO:!!!!
		pass

	def editAsset(self, assetNode):
		assetNode.openInSystem()


##----------------------------------------------------------------##
class RawAssetManager(AssetManager):	
	def getName(self):
		return 'raw'

	def getPriority( self ):
		return -1

	def acceptAssetFile(self, filepath):
		return True

	def importAsset(self, assetNode, option = None):
		path = os.path.realpath( assetNode.getAbsFilePath() )
		if os.path.isfile( path ): 
			assetNode.assetType = 'file'
		elif os.path.isdir( path ):
			assetNode.assetType = 'folder'
		return True

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
		self.loadAssetTable()		

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

	def enumerateAsset( self, assetTypes, **options ):
		noVirtualNode = options.get( 'no_virtual', False )
		result = []
		if isinstance( assetTypes, str ): assetTypes = ( assetTypes )
		for path, node in self.assetTable.items():
			if node.getType() in assetTypes and \
				not ( noVirtualNode and node.isVirtual() ):
				result.append(node)
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
			signals.emitNow('asset.unregister', oldnode)
			if oldnode.parentNode: 
				oldnode.parentNode.removeChild(oldnode)
				oldnode.parentNode=None
			path = oldnode.getNodePath()
			del self.assetTable[path]
			assert not self.assetTable.has_key(path)	

	def initAssetNode( self, path, option = None, **kwargs ):
		#fix path
		absFilePath = os.path.abspath( self.rootAbsPath + '/' + path )
		fileTime = os.path.getmtime(absFilePath),
		filePath = self.rootPath + '/' + path

		node = self.getAssetNode(path)
		assert not node
		#create a common asset node first
		if not node:
			ppath      = os.path.dirname(path)
			parentNode = self.getAssetNode(ppath)			

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

	def importModifiedAssets(  self ):
		#collect 'modifyState' 	 asset
		modifiedAssets = {}
		for node in self.assetTable.values():
			if node.modifyState:   #TODO: virtual node?
				modifiedAssets[ node ] = True
		#try importing with each asset manager, in priority order
		for manager in self.assetManagers:
			if not modifiedAssets: break
			done = []
			for node in modifiedAssets:
				if not node.modifyState: #might get imported as a sub asset 
					done.append( node )
					continue
				if not manager.acceptAssetFile( node.getAbsFilePath() ):
					continue
				if node.modifyState != 'new':					
					for n in node.getChildren()[:]:
						self.unregisterAssetNode(n)
						#TODO: add failed state to node				
				if node.getManager() != manager: node.setManager( manager )
				if manager.importAsset( node ):
						node.modifyState  =  False
						done.append( node )
			for node in done:
				del modifiedAssets[ node ]			
		signals.emitNow( 'asset.post_import_all' )

	def scheduleScanProject( self ):
		self.projectScanScheduled = True
		pass

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
				self.unregisterAssetNode( node )
				continue
			#file become ignored
			if self.checkFileIgnorable( filePath ):
				self.unregisterAssetNode( node )
				continue

		#check new asset
		for currentDir, dirs, files in os.walk(unicode(self.rootAbsPath)):
			relDir = os.path.relpath( currentDir, self.rootAbsPath )

			for filename in files:
				if self.checkFileIgnorable(filename):
					continue
				nodePath = self.fixPath( relDir + '/' + filename )
				if not self.getAssetNode( nodePath ): #new
					self.initAssetNode( nodePath )
				else:
					node = self.getAssetNode( nodePath )
					absPath = self.getAbsPath( nodePath )
					if os.path.getmtime( absPath ) >= node.getFileTime():
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

	def loadAssetTable(self):

		logging.info( 'loading asset table from:' + self.assetIndexPath )
		
		if not os.path.exists( self.assetIndexPath ): return
		dataTable = jsonHelper.tryLoadJSON( self.assetIndexPath )

		if not dataTable: return False
		
		assetTable={}

		for path,data in dataTable.items():
			node=AssetNode(path, data.get('type').encode('utf-8'), 
					filePath = data.get( 'filePath', path ),
					fileTime = data.get( 'fileTime', 0 ),
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

			for dpath in data.get('rDep',[]):
				dnode = assetTable[dpath]
				assert dnode
				node.addDependencyR(dnode)

			for dpath in data.get('pDep',[]):
				dnode = assetTable[dpath]
				assert dnode
				node.addDependencyP(dnode)

		self.assetTable=assetTable
		logging.info("asset library loaded")

	def saveAssetTable(self):
		table={}
		for path, node in self.assetTable.items():
			item={
				'type'        : node.getType(),
				'filePath'    : node.getFilePath() or False,
				'fileTime'    : node.getFileTime(),
				'manager'     : node.managerName,
				'deploy'      : node.deployState,
				'pDep'        : [ dnode.getNodePath() for dnode in node.pDep ],
				'rDep'        : [ dnode.getNodePath() for dnode in node.rDep ],
				'objectFiles' : node.objectFiles,
				'cacheFiles'  : node.cacheFiles,
				'properties'  :  node.properties,
	 			'modifyState' : node.modifyState
 	 			# 'parent':node.getParent().getPath()
			}				
			table[path]=item
			#mark cache files
			for name, cacheFile in node.cacheFiles.items():
				CacheManager.get().touchCacheFile( cacheFile )
				
			node.saveMetaDataTable()	

		if not jsonHelper.trySaveJSON( table, self.assetIndexPath, 'asset index' ):
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
