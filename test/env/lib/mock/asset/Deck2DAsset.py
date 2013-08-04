import os.path
from gii.core import *
import json


class Deck2DAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.deck2d'

	def acceptAssetFile(self, filepath):
		if not os.path.isfile( filepath ): return False		
		name, ext = os.path.splitext( filepath )
		if not ext in ( '.deck2d' ): return False
		#validation
		try:
			fp = open( filepath, 'r' )
			text = fp.read()
			fp.close()
			data = json.loads( text )
			return data.get( '_assetType', None ) == 'deck2d'
		except Exception, e:
			pass

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


Deck2DAssetManager().register()
AssetLibrary.get().setAssetIcon( 'deck2d',              'pack' )
AssetLibrary.get().setAssetIcon( 'deck2d.quad',         'deck_quad' )
AssetLibrary.get().setAssetIcon( 'deck2d.tileset',      'deck_tileset' )
AssetLibrary.get().setAssetIcon( 'deck2d.stretchpatch', 'deck_patch' )
AssetLibrary.get().setAssetIcon( 'deck2d.quad_array	',  'deck_quad_array' )
