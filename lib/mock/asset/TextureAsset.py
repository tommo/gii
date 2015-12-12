import os.path
import logging
import subprocess
import shutil
import json

from gii.core import *
from mock import _MOCK
from TextureProcessor import applyTextureProcessor

import ImageHelpers 
from PIL import Image

##----------------------------------------------------------------##
signals.register( 'texture.add' )
signals.register( 'texture.remove' )
signals.register( 'texture.rebuild' )

##----------------------------------------------------------------##
_TEXTURE_LIBRARY_DATA_FILE = 'texture_library.json'
_ATLAS_JSON_NAME = 'atlas.json'

##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

##----------------------------------------------------------------##
def groupToJson( group ):
	return {
				'name'               : group.name,
				'filter'             : group.filter,
				'mipmap'             : group.mipmap,
				'wrap'               : group.wrap ,
				'atlas_mode'         : group.atlasMode ,
				'cache'              : group.cache
			}

def _fixPath( path ):
		path = path.replace( '\\', '/' ) #for windows
		if path.startswith('./'): path = path[2:]
		return path	
		

##----------------------------------------------------------------##
def _convertAtlas( inputfile,  srcToAssetDict ):
	f = open( inputfile, 'r' )
	items      = []
	atlasNames = []
	atlasInfos = []
	readingMode = 'sprite'

	for line in f.readlines():
		if line.startswith( '[atlas]' ):
			readingMode = 'atlas'
			continue
		if line.startswith( '[sprite]' ):
			readingMode = 'sprite'
			continue
		if readingMode == 'atlas':
			parts       = line.split('\t')
			name        = parts[ 0 ]
			atlasNames.append( name )
			atlasInfos.append( {
					'name': os.path.basename(name),
					'size':[ int(parts[1]), int(parts[2]) ]
				} )
		else:
			parts       = line.split('\t')
			sourcePath  = _fixPath( parts[1] )
			if sourcePath.startswith('\"'):
				sourcePath = sourcePath[1:-1]		
			# name = os.path.basename( sourcePath )
			assetPath, index, subId = srcToAssetDict[ sourcePath ]
			atlasName = parts[0]		
			atlasId = atlasNames.index( atlasName )
			data = {
				'atlas'  : atlasId,
				'name'   : assetPath,
				'index'  : index,
				'subId'  : subId,
				'source' : sourcePath,
				'rect'   : [ int(x) for x in parts[2:] ]
			}
			items.append(data)

	output = {
		'atlases' : atlasInfos,
		'items'   : items,
	}

	return output


##----------------------------------------------------------------##
class TextureAssetManager( AssetManager ):
	def getName(self):
		return 'asset_manager.texture'

	def acceptAssetFile(self, filepath):
		name,ext = os.path.splitext(filepath)
		if os.path.isfile(filepath):
			return ext in [ '.png', '.psd', '.jpg', '.bmp', '.jpeg' ]
		else:
			return ext in ['.texstrip' ]

	def importAsset(self, node, reload = False ):
		node.assetType = 'texture'
		group = node.getMetaData( 'group' )
		if not group:
			group = 'default'
			node.setNewMetaData( 'group', group )
		if os.path.isdir( node.getAbsFilePath() ):
			node.setBundle()
		TextureLibrary.get().scheduleImport( node ) #let texture library handle real import
		return True

	def deployAsset( self, node, context ):
		super( TextureAssetManager, self ).deployAsset( node, context )
		pixmapPath = node.getObjectFile( 'pixmap' )
		if pixmapPath:
			mappedPath = context.getAbsFile( pixmapPath )
			# if context.isNewFile( mappedPath ):
				# print( node.getNodePath(), mappedPath )
				# ImageHelpers.convertToWebP( mappedPath )
				
	def requestAssetThumbnail( self, assetNode, size ):
		return self.buildAssetThumbnail( assetNode, size )

	def onBuildAssetThumbnail( self, assetNode, targetPath, size ):
		srcPath = assetNode.getAbsFilePath()
		ImageHelpers.buildThumbnail( srcPath, targetPath, size )
		return True

##----------------------------------------------------------------##
class PrebuiltAtlasAssetManager( AssetManager ):
	def getName(self):
		return 'asset_manager.prebuilt_atlas'

	def importAsset(self, node, reload = False ):
		TextureLibrary.get().scheduleImport( node ) #let texture library handle real import
		return True

	def deployAsset( self, node, context ):
		super( PrebuiltAtlasAssetManager, self ).deployAsset( node, context )
		for key, value in node.objectFiles.items():
			if not key.startswith( 'pixmap' ): continue
			pixmapPath = value
			mappedPath = context.getAbsFile( pixmapPath )
			if context.isNewFile( mappedPath ):
				# print( node.getNodePath(), mappedPath )
				ImageHelpers.convertToWebP( mappedPath )

##----------------------------------------------------------------##
class TextureLibrary( EditorModule ):
	_singleton = None
	@staticmethod
	def get():
		return TextureLibrary._singleton

	def __init__( self ):
		assert not TextureLibrary._singleton
		TextureLibrary._singleton = self
		self.lib = None
		self.pendingImportGroups = {}
		self.pendingImportTextures = {}

	def getName( self ):
		return 'texture_library'

	def getDependency( self ):
		return ['mock']

	def onLoad( self ):
		self.dataPath  = self.getProject().getConfigPath( _TEXTURE_LIBRARY_DATA_FILE )		
		self.delegate  = app.getModule('moai').loadLuaDelegate( _getModulePath('TextureLibrary.lua') )

		signals.connect( 'asset.post_import_all', self.postAssetImportAll )
		signals.connect( 'asset.unregister',      self.onAssetUnregister )

		signals.connect( 'project.deploy', self.onDeploy )
		signals.connect( 'project.save', self.onSaveProject )

	def onStart( self ):
		self.lib = _MOCK.getTextureLibrary()
		print 'texture libray start'
		if not os.path.exists( self.dataPath ):
			self.saveIndex()
		for group in self.lib.groups.values():
			if group.atlasCachePath:
				CacheManager.get().touchCacheFile( group.atlasCachePath )
		# self.forceRebuildAllTextures()
		# self.saveIndex()

	def onAppReady( self ):
		pass
		
	def getLibrary( self ):
		return self.lib
			
	def saveIndex( self ):
		logging.info( 'saving texture library index' )
		self.lib.save( self.lib, self.dataPath )

	def findTextureNode( self, assetNode ):
		lib = self.lib
		t = lib.findTexture( lib, assetNode.getNodePath() )
		return t

	def scheduleImport( self, node ):
		lib = self.lib
		t = lib.findTexture( lib, node.getNodePath() )
		if not t:
			t = lib.addTexture( lib, node.getNodePath() )
			assert t
			signals.emit( 'texture.add', t )

		self.pendingImportTextures[ node ] = t		
		
	def doPendingImports( self ):
		pendingImportTextures = self.pendingImportTextures
		self.pendingImportTextures = {}
		lib = self.lib
		pendingAtlasGroups = set()
		for node, t in pendingImportTextures.items():			
			group = t.parent
			self.processTextureNode( t, node )			
			if group.isAtlas( group ):
				pendingAtlasGroups.add( group )
			else:
				self.buildSingleTexture( t, node )

		for group in pendingAtlasGroups:
			self.buildAtlas( group )	
			
		self.saveIndex()

	def processTextureNode( self, texture, assetNode ):
		logging.info( 'processing texture: %s' % assetNode.getNodePath() )

		if assetNode.isType( 'texture' ):
			assetNode.clearCacheFiles()
			if assetNode.isVirtual():
				src = assetNode.getMetaData( 'source', None )
				if not src:
					raise Exception( 'virtual texture node has no source metadata given' )
				src = AssetLibrary.get().getAbsProjectPath( src )
			else:
				src = assetNode.getAbsFilePath()
			dst = assetNode.getAbsCacheFile( 'pixmap' ) 
			self._processTexture( src, dst, texture )

		elif assetNode.isType( 'prebuilt_atlas' ):
			atlasSourcePath = assetNode.getCacheFile( 'atlas_source' )
			atlas = self.delegate.call( 'loadPrebuiltAtlas', atlasSourcePath )
			pageId = 0
			for page in atlas.pages.values():
				pageId += 1
				src = self.getAssetLibrary().getAbsProjectPath( page.source )
				dst = assetNode.getCacheFile( 'pixmap_%d' % pageId )
				assetNode.setObjectFile( 'pixmap_%d' % pageId, dst )
				self._processTexture( src, dst, texture )
				if page.w < 0:
					w, h = ImageHelpers.getImageSize( dst )
					page.w = w
					page.h = h
			assetNode.setMetaData( 'page_count', pageId )			
			atlasOutputPath = assetNode.getCacheFile( 'atlas' )
			assetNode.setObjectFile( 'atlas', atlasOutputPath )
			texture.prebuiltAtlasPath = atlasOutputPath
			atlas.save( atlas, atlasOutputPath )

		else:
			raise Exception( 'unknown texture node type!!' )


	def _processTexture( self, src, dst, texture ):
		#convert single image
		result = ImageHelpers.convertToPNG( src, dst )		
		#apply processor on dst file
		group = texture.parent
		if group:
			groupProcessor = group.processor
			if groupProcessor:
				applyTextureProcessor( groupProcessor, dst )
			nodeProcessor = texture.processor
			if nodeProcessor:
				applyTextureProcessor( nodeProcessor, dst )				

	##----------------------------------------------------------------##
	def _explodePrebuiltAtlas( self, node, srcToAssetDict, sourceList, outputDir, prefix, scale ):
		atlasSourcePath = node.getCacheFile( 'atlas_source' )
		atlas = self.delegate.call( 'loadPrebuiltAtlas', atlasSourcePath )
		nodePath = node.getNodePath()
		pageId = 0		
		for page in atlas.pages.values():
			pageId += 1
			imagePath = node.getCacheFile( 'pixmap_%d' % pageId )
			img = Image.open( imagePath )
			itemId = 0
			for item in page.getItems( page ).values():
				itemId += 1
				if item.rotated:
					box  = ( item.x, item.y, item.x + item.h, item.y + item.w )
				else:
					box  = ( item.x, item.y, item.x + item.w, item.y + item.h )
				part = img.crop( box )
				partName = '%s_%d_%d.png' % ( prefix, pageId, itemId )
				partPath = outputDir( partName )
				if scale != 1:
					w, h = part.size
					newSize = ( max( 1, int(w*scale) ),  max( 1, int(h*scale) ) )
					part = part.resize( newSize, Image.BILINEAR )
				part.save( partPath )
				srcToAssetDict[ partPath ] = ( nodePath, pageId , item.name )
				sourceList.append( partPath )

	def buildAtlas( self, group ):
		logging.info( '' )
		logging.info( 'building atlas texture:' + group.name )

		#packing atlas
		assetLib = self.getAssetLibrary()
		nodes = {}
		for t in group.textures.values():
			node = assetLib.getAssetNode( t.path )
			if node:
				nodes[ node ] = t				
			else:
				logging.warn( 'node not found: %s' % t.path )

		sourceList     = []
		srcToAssetDict = {}
		prebuiltAtlases = []
		for node in nodes:
			if node.isType( 'texture' ):
				path = node.getAbsCacheFile( 'pixmap' )
				srcToAssetDict[ path ] = ( node.getNodePath(), 0, False )
				tex = nodes[ node ]
				scale = tex.getScale( tex )
				if scale != 1 :
					img = Image.open( path )
					w, h = img.size
					w1   = int( max( w*scale, 1 ) )
					h1   = int( max( h*scale, 1 ) )
					img.resize( (w1,h1), Image.BILINEAR )
					img.save( path )
				sourceList.append( path )
			elif node.isType( 'prebuilt_atlas' ):
				prebuiltAtlases.append( node )

		explodedAtlasDir = None
		if group.repackPrebuiltAtlas:
			explodedAtlasDir = CacheManager.get().getTempDir()		
			atlasId = 0
			for node in prebuiltAtlases:
				atlasId += 1
				texture = group.findTexture( group, node.getNodePath() )				
				scale  = texture.getScale( texture )
				prefix = 'atlas%d' % atlasId
				self._explodePrebuiltAtlas(
					node, srcToAssetDict, sourceList, explodedAtlasDir, prefix, scale
				)
		else:
			for node in prebuiltAtlases:
				nodePath = node.getNodePath()
				pageCount = node.getMetaData( 'page_count' )
				for i in range( pageCount ):
					path = node.getAbsCacheFile( 'pixmap_%d' % ( i + 1 ) )
					srcToAssetDict[ path ] = ( nodePath, i + 1, False )
					sourceList.append( path )

		#use external packer
		atlasName = 'atlas_' + group.name

		tmpDir = CacheManager.get().getTempDir()
		prefix = tmpDir( atlasName )

		outputDir = CacheManager.get().getCacheDir( '<texture_group>/' + group.name  )
		for name in os.listdir( outputDir ): #clear target path
			try:
				os.remove( outputDir + '/' + name )
			except Exception, e:
				pass

		arglist = [ 'python', _getModulePath('tools/AtlasGenerator.py'), '--prefix', prefix ]
		arglist += [ str( group.maxAtlasWidth ) , str( group.maxAtlasHeight ) ]
		arglist += sourceList
		try:
			ex = subprocess.call( arglist ) #run packer
			#conversion
			srcFile = prefix + '.txt'
			data    = _convertAtlas( srcFile,  srcToAssetDict )
			dstPath = outputDir
			#copy generated atlas
			for i, entry in enumerate( data['atlases'] ):
				src = entry['name']
				dstName = 'tex_%d' % i
				# dst = '%s/%s%d' % ( dstPath, atlasName, i )
				entry['name'] = dstName
				shutil.copy( tmpDir( src ), dstPath +'/' + dstName )
			#update texpack
			data[ 'sources' ] = sourceList
			cfgPath = outputDir + '/' + _ATLAS_JSON_NAME
			fp = open( cfgPath, 'w' )
			json.dump( data, fp, sort_keys=True, indent=2 )
			fp.close()

		except Exception,e:
			logging.exception( e )
			return False

		self.delegate.call( 'fillAtlasTextureGroup', group, outputDir, group.repackPrebuiltAtlas )
		self.delegate.call( 'releaseTexPack', outputDir )

		#redirect asset node to sub_textures
		for node in nodes:
			self.buildSubTexture( group, node )
		group.unloadAtlas( group )
		return True

	def buildSingleTexture( self, tex, node ):
		group = tex.parent
		logging.info( 'building single texture: %s<%s>' % ( node.getPath(), group.name ) )
		if node.isType( 'texture' ):
			node.clearObjectFiles()
			dst = node.getCacheFile( 'pixmap' )
			node.setObjectFile( 'pixmap', dst )
			img = Image.open( dst )
			w, h = img.size
			self.delegate.call( 'fillSingleTexture', tex, dst, w, h )
			scale = tex.getScale( tex )
			if scale != 1:
				newSize = ( int(w*scale), int(h*scale) )
				img = img.resize( newSize, Image.BILINEAR )
				img.save( dst, 'PNG' )

		elif node.isType( 'prebuilt_atlas' ):
			count = node.getMetaData( 'page_count' )
			scale = tex.getScale( tex )
			if scale != 1:
				atlasOutputPath = node.getCacheFile( 'atlas' )
				atlas = self.delegate.call( 'loadPrebuiltAtlas', atlasOutputPath )
				atlas.rescale( atlas, scale )
				for i in range( count ):
					dst = node.getCacheFile( 'pixmap_%d' % ( i + 1 ) )
					img  = Image.open( dst )
					w, h = img.size
					w1   = max( int(w*scale), 1 )
					h1   = max( int(h*scale), 1 )
					img  = img.resize( ( w1, h1 ), Image.BILINEAR )
					img.save( dst, 'PNG' )
				atlas.save( atlas, atlasOutputPath )

		signals.emit( 'texture.rebuild', node )

	def buildSubTexture( self, group, node ):
		logging.info( 'building sub texture: %s<%s>' % ( node.getPath(), group.name ) )
		if node.isType( 'texture' ):
			node.clearObjectFiles()
			node.setObjectFile( 'pixmap', None ) #remove single texture if any
			node.setObjectFile( 'config', node.getCacheFile( 'config' ) )
			jsonHelper.trySaveJSON( groupToJson( group ), node.getAbsObjectFile( 'config' ) )
		elif node.isType( 'prebuilt_atlas' ):
			pass
		signals.emit( 'texture.rebuild', node )	
		
	def postAssetImportAll( self ):
		self.doPendingImports()

	def onAssetUnregister( self, node ):
		t = self.lib.removeTexture( self.lib, node.getNodePath() )
		if t:
			signals.emit( 'texture.remove', t )

	def forceRebuildAllTextures( self ):
		for node in self.getAssetLibrary().enumerateAsset( 'texture' ):
			self.scheduleImport( node )
		self.doPendingImports()

	def forceRebuildTexture( assetNode ):
		self.scheduleImport( assetNode )
		self.doPendingImports()

	def _convertTextureFormat( self, fullPath, format, outputPath = None ):
		if format == 'auto':
			format = 'webp'
		else:
			format = 'png'
		
		print 'converting texture', fullPath, format

		if format == 'webp':
			ImageHelpers.convertToWebP( fullPath )
		elif format == 'png':
			pass
		elif format == 'PVR-2':
			ImageHelpers.convertToPVR( fullPath, outputPath, bbp = 2 )
		elif format == 'PVR-4':
			ImageHelpers.convertToPVR( fullPath, outputPath, bbp = 4 )

	def onDeploy( self, context ):
		self.saveIndex()
		context.addFile( self.dataPath, 'asset/texture_index' )
		context.meta['mock_texture_library'] = 'asset/texture_index'
		#process atlas
		for group in self.lib.groups.values():
			if group.isAtlas( group ) and group.atlasCachePath:
				oldPath = group.atlasCachePath
				newPath = context.addFile( oldPath )
				absNewPath = context.getPath( newPath )
				for f in os.listdir( absNewPath ):
					if not f.startswith( 'tex' ): continue
					fullPath = absNewPath + '/' + f
					if context.isNewFile( fullPath ):
						self._convertTextureFormat( fullPath, group.format )
				#replace in index file
				context.replaceInFile( context.getPath( 'asset/texture_index' ), oldPath, newPath )
		
	def onSaveProject( self, prj ):
		self.saveIndex()

##----------------------------------------------------------------##
TextureAssetManager().register()
PrebuiltAtlasAssetManager().register()

TextureLibrary().register()

AssetLibrary.get().setAssetIcon( 'prebuilt_atlas', 'cell' )
