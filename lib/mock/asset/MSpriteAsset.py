import os.path
from gii.core import AssetManager, AssetLibrary, getProjectPath, app
from helper.psd2msprite import MSpriteProject
import json

def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path


class MSpriteAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.msprite'

	def acceptAssetFile(self, filepath):
		if not os.path.isdir(filepath): return False		
		if not filepath.endswith( '.msprite' ): return False
		return True

	def importAsset(self, node, reload = False ):
		if node.isVirtual(): return
		node.assetType = 'msprite'
		node.setBundle()

		#atlas
		atlasFile = node.getCacheFile( 'atlas' )
		node.setObjectFile( 'atlas', atlasFile )
		#define
		defFile = node.getCacheFile( 'def' )
		node.setObjectFile( 'def', defFile )

		proj = MSpriteProject()
		#traverse path
		filePath = node.getFilePath()
		nodePath = node.getNodePath()
		for fileName in os.listdir( node.getAbsFilePath() ):
			fullPath = filePath + '/' + fileName
			name, ext = os.path.splitext( fileName )
			if ext == '.psd':
				proj.loadPSD( fullPath )

		#TODO: let texture library handle atlas
		absAtlas, absDef = node.getAbsObjectFile( 'atlas' ), node.getAbsObjectFile( 'def' )
		proj.save( absAtlas, absDef )

		atlasNode = node.affirmChildNode( node.getBaseName()+'_texture', 'texture', manager = 'asset_manager.texture' )
		atlasNode.setMetaData( 'source', atlasFile )
		app.getModule( 'texture_library' ).scheduleImport( atlasNode )
		
		return True

MSpriteAssetManager().register()

AssetLibrary.get().setAssetIcon( 'animclip',   'clip' )
AssetLibrary.get().setAssetIcon( 'quadlists',  'cell' )
AssetLibrary.get().setAssetIcon( 'msprite',    'clip' )
