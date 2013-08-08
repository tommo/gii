import os.path
from gii.core import *
import json

##----------------------------------------------------------------##
class Deck2DAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.deck2d'

	def acceptAssetFile(self, filePath):
		if not os.path.isfile( filePath ): return False		
		name, ext = os.path.splitext( filePath )
		if not ext in [ '.deck2d' ]: return False
		#validation
		data = jsonHelper.tryLoadJSON( filePath )
		return data and data.get( '_assetType', None ) == 'deck2d'		

	def importAsset(self, node, option=None):
		node.assetType = 'deck2d'
		data = jsonHelper.tryLoadJSON( node.getAbsFilePath() )
		if data:
			for item in data.get( 'items', [] ):
				deckType = 'deck2d.' + item['type']
				name  =  item['name']
				node.createChildNode( name ,  deckType, manager = self )
		return True


	def editAsset(self, node):	
		editor = app.getModule( 'deck2d_editor' )
		if not editor: 
			return alertMessage( 'Editor not load', 'Style Editor not found!' )
		
		editor.startEdit( node )

##----------------------------------------------------------------##
class Deck2DCreator(AssetCreator):
	def getAssetType( self ):
		return 'deck2d'

	def getLabel( self ):
		return 'Deck2D Pack'

	def createAsset( self, name, contextNode, assetType ):
		ext = '.deck2d'
		filename = name + ext
		if contextNode.isType('folder'):
			nodepath = contextNode.getChildPath( filename )
		else:
			nodepath = contextNode.getSiblingPath( filename )

		fullpath = AssetLibrary.get().getAbsPath( nodepath )
		data={
			'_assetType' : 'deck2d', #checksum
			'items':[]
		}
		if os.path.exists(fullpath):
			raise Exception('File already exist:%s'%fullpath)
		fp = open(fullpath,'w')
		json.dump( data, fp, sort_keys=True, indent=2 )
		fp.close()
		return nodepath
		
##----------------------------------------------------------------##
Deck2DAssetManager().register()
Deck2DCreator().register()

AssetLibrary.get().setAssetIcon( 'deck2d',              'pack' )
AssetLibrary.get().setAssetIcon( 'deck2d.quad',         'deck_quad' )
AssetLibrary.get().setAssetIcon( 'deck2d.tileset',      'deck_tileset' )
AssetLibrary.get().setAssetIcon( 'deck2d.stretchpatch', 'deck_patch' )
AssetLibrary.get().setAssetIcon( 'deck2d.quad_array	',  'deck_quad_array' )
