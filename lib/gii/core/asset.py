import json
import re
import os
import logging
import os.path
import weakref

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
		self.manager = kwargs.get('manager',None)
		if isinstance(nodePath, str):
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

		self.filePath = kwargs.get( 'filePath', nodePath )
		self.fileTime = kwargs.get( 'fileTime', 0 )

		self.accessPriority=0

		self.properties={}		

	def __repr__(self):	
		return '<%s>%s'%(self.getType(),self.getNodePath().encode('utf-8'))

	def getType(self):
		return self.assetType

	def isType(self, typeName):
		if isinstance(typeName,(list, tuple)):
			return self.assetType in typeName
		else:
			return self.assetType == typeName

	def getManager(sefl):
		return self.manager

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
		path=self.getPath()
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
		self.manager=assetManager
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
	def getMetaData( self ):
		if self.isVirtual(): return None
		if self.metadata: return self.metadata
		dirname = self.getAbsDir()
		metaDir = dirname + '/' +GII_ASSET_META_DIR
		metaPath = metaDir + '/' + self.getName() + '.meta'
		if os.path.exists( metaPath ):
			fp = open( metaPath, 'r' )
			text = fp.read()
			fp.close()
			data = json.loads( text )
			self.metadata = data
		else:
			self.metadata = {}
		return self.metadata

	def saveMetaData( self ):
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

	def getCacheFile(self, name):
		cacheFile = self.cacheFiles.get( name, None )
		if cacheFile: return cacheFile
		cacheFile = CacheManager.get().getCacheFile( self.getPath(), name )
		self.cacheFiles[ name ] = cacheFile
		return cacheFile

	def getObjectFile(self, name):
		return self.objectFiles.get( name, None )

	def setObjectFile(self, name, path):
		self.objectFiles[ name ] = path

	def edit(self):
		self.manager.editAsset(self)

	def getProperty(self, name, defaultValue=None ):
		return self.properties.get(name, defaultValue)

	def setProperty(self, name, value):
		self.properties[ name ] = value

	def forceReimport(self):
		self.manager.reimportAsset(self)
		signals.emitNow('asset.modified', self)
		self.saveMetaData()

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
		return self.importAsset(assetNode, option)

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
		self.rootNode       = AssetNode( self.rootPath, 'folder' )
		self.loadAssetTable()		

	def save( self ):
		self.saveAssetTable()

	def getRootNode(self):
		return self.rootNode

	def getAbsPath( self, path ):
		return self.rootAbsPath + '/' + path

	def getRelPath( self, path ):
		path = os.path.abspath( path )
		return os.path.relpath( path, self.rootAbsPath )

	def registerAssetManager(self, manager):
		logging.info( 'registering asset manager:'+manager.getName() )
		for p in self.assetManagers:
			if p==manager:
				raise AssetException('Duplicated AssetManager %s'%manager.getName())

			if p.getPriority()<=manager.getPriority():
				idx=self.assetManagers.index(p)
				self.assetManagers.insert(idx, manager)
				return manager

		self.assetManagers.append(manager)
		return manager

	def getAssetManager(self, name):
		for mgr in self.assetManagers:
			if mgr.getName()==name:
				return mgr
		return None

	def registerAssetNode(self, node):		
		path=node.getNodePath()
		logging.info( 'register: %s' % repr(node) )
		if self.assetTable.has_key(path):
			print( path, self.assetTable[path] )
			raise Exception('unclean path')
		self.assetTable[path]=node

		signals.emitNow('asset.register', node)

		for child in node.getChildren():
			self.registerAssetNode(child)

		return node

	def unregisterAssetNode(self, oldnode):
		assert oldnode
		logging.info( 'unregister: %s' % repr(oldnode) )
		for child in oldnode.getChildren()[:]:
			self.unregisterAssetNode(child)
		signals.emitNow('asset.unregister', oldnode)

		if oldnode.parentNode: 
			oldnode.parentNode.removeChild(oldnode)
			oldnode.parentNode=None
		path=oldnode.getNodePath()
		del self.assetTable[path]
		assert not self.assetTable.has_key(path)

	def importAsset(self, path, option=None ,**kwarg):
		'''find an asset manager capable of processing given file'''
		path = path.replace( '\\', '/' ) #for windows
		if path.startswith('./'): path=path[2:]
		fullpath = os.path.abspath( self.rootAbsPath + '/' + path )
		oldnode  = self.getAssetNode(path)

		if oldnode and \
				os.path.getmtime(fullpath) <= oldnode.getFileTime() and \
				(not kwarg.get('forced', False)):
			return oldnode

		ppath      = os.path.dirname(path)
		parentNode = self.getAssetNode(ppath)			

		if not os.path.exists( fullpath ):
			raise AssetException( 'file not exist: %s' % fullpath )
		
		node = oldnode

		if not node: 
			node = AssetNode(
					path, 
					os.path.isfile(fullpath) and 'file' or 'folder' , 
					fileTime = os.path.getmtime(fullpath),
					filePath = self.rootPath + '/' + path
				)
			parentNode.addChild(node)	

		for manager in self.assetManagers:
			if manager.acceptAssetFile(fullpath):
				if oldnode: #reimport
					manager.reimportAsset(node, option)
				else:
					manager.importAsset(node, option)
				node.manager = manager
				break

		if not node.manager:
			node.manager = self.rawAssetManager
		
		if not oldnode:
			self.registerAssetNode(node)

		if oldnode:
			oldnode.fileTime = os.path.getmtime(fullpath)
			signals.emitNow('asset.modified', node)
			logging.info( 'reimport: %s' % repr(node) )
		else:
			signals.emitNow('asset.added', node)

		node.saveMetaData()
		
		return node

	def hasAssetNode(self, nodePath):
		if not nodePath: return False
		return not self.getAssetNode( nodePath ) is None

	def getAssetNode(self, nodePath):
		if not nodePath: return self.rootNode
		return self.assetTable.get(nodePath, None)

	def enumerateAsset( self, assetTypes, **options ):
		allowVirtualNode = options.get('allowVirtualNode', True)
		result = []
		if isinstance( assetTypes, str ): assetTypes = ( assetTypes )
		for path, node in self.assetTable.items():
			if node.getType() in assetTypes and \
				not ( not allowVirtualNode and node.isVirtual() ):
				result.append(node)
		return result

	def checkFileIgnorable(self, name):
		for pattern in self.ignoreFilePattern:
			if re.match(pattern, name):
				return True
		return False

	def reimportAll(self):
		#TODO:should this be done by a asset index rebuilding (by restarting editor)?
		pass


	def scanProjectPath(self): #scan 
		logging.info('** scan project')
		path=self.rootPath
		
		#scan meta files first ( will be used in asset importing )
		#TODO

		#check missing asset
		for assetPath, node in self.assetTable.copy().items():
			if not self.assetTable.has_key(assetPath): #already removed(as child of removed node)
				# print('skip:',assetPath)
				continue
			#check parentnode
			if not node.getParent():
				self.unregisterAssetNode(node)
				continue

			if node.isVirtual(): #don't check virtual node's file
				continue

			filePath=self.getAbsPath(node.getFilePath())
			#file deleted
			if not os.path.exists(filePath):
				self.unregisterAssetNode(node)
				continue
			#file become ignored
			if self.checkFileIgnorable(filePath):
				self.unregisterAssetNode(node)
				continue

			
		#check new asset
		for currentDir, dirs, files in os.walk(unicode(path)):
			relDir=os.path.relpath(currentDir, self.rootPath)

			for filename in files:
				if self.checkFileIgnorable(filename):
					continue
				fullpath=relDir+'/'+filename				
				self.importAsset(fullpath, forced=False)

			dirs2=dirs[:]
			for dirname in dirs2:
				if self.checkFileIgnorable(dirname):
					dirs.pop(dirs.index(dirname)) #skip walk this
					continue
				fullpath=relDir+'/'+dirname
				node=self.importAsset(fullpath, forced=False)

		self.saveAssetTable()

	def loadAssetTable(self):
		logging.info( 'loading asset table' )
		
		if not os.path.exists( self.assetIndexPath ): return
		dataTable = jsonHelper.tryLoadJSON( self.assetIndexPath )

		if not dataTable: return False
		
		assetTable={}

		for path,data in dataTable.items():
			node=AssetNode(path, data.get('type').encode('utf-8'), 
					filePath=data.get('filePath',path),
					fileTime=data.get('fileTime',0),
				)
			node.deployState  = data.get('deploy', None)
			node.properties   = data.get('properties', {})
			node.cacheFiles   = data.get('cacheFiles', {})
			node.objectFiles  = data.get('objectFiles', {})
			node.properties   = data.get('properties', {})
			
			assetTable[path]=node
			mgrName=data.get('manager')
			if mgrName=='raw':
				node.manager=self.rawAssetManager
			else:
				node.manager=self.getAssetManager(mgrName) or self.rawAssetManager

		#relink parent/dependency
		for path,node in assetTable.items():
			ppath=os.path.dirname(path)
			if not ppath:
				pnode=self.rootNode
			else:
				pnode=assetTable.get(ppath,None)
			if not pnode:
				continue
			pnode.addChild(node)
			data=dataTable[path]

			for dpath in data.get('rDep',[]):
				dnode=assetTable[dpath]
				assert dnode
				node.addDependencyR(dnode)

			for dpath in data.get('pDep',[]):
				dnode=assetTable[dpath]
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
				'manager'     : node.manager.getName(),
				'deploy'      : node.deployState,
				'pDep'        : [ dnode.getNodePath() for dnode in node.pDep ],
				'rDep'        : [ dnode.getNodePath() for dnode in node.rDep ],
				'objectFiles' :  node.objectFiles,
				'cacheFiles'  :  node.cacheFiles,
				'properties'  : node.properties,
				# 'parent':node.getParent().getPath()
			}				
			table[path]=item
			#mark cache files
			for name, cacheFile in node.cacheFiles.items():
				CacheManager.get().touchCacheFile( cacheFile )
			if node.metadata:
				node.saveMetaData()

		if not jsonHelper.trySaveJSON( table, self.assetIndexPath ):
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


	def compileAssetTable(self):
		for path, node in self.assetTable.items():
			pass

	def getAssetIcon( self, assetType ):
		return self.assetIconMap.get( assetType, assetType )

	def setAssetIcon( self, assetType, iconName ):
		self.assetIconMap[ assetType ] = iconName

