import os.path
from gii.core import AssetManager, AssetLibrary, getProjectPath, app, jsonHelper
# from helper.psd2deckpack import DeckPackProject

from helper.PSDDeckPackProject import PSDDeckPackProject
import helper.PSDDeckMTileset
import helper.PSDDeckMQuad

import json

def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path


class DeckPSDAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.deckpack_psd'
	
	def getPriority( self ):
		return 1000

	def acceptAssetFile(self, filepath):
		if not os.path.isfile(filepath): return False		
		if not filepath.endswith( '.decks.psd' ): return False
		return True

	def importAsset(self, node, reload = False ):
		if node.isVirtual(): return
		node.assetType = 'deck_pack'
		node.groupType = 'package'
		
		output = node.getCacheFile( 'export', is_dir = True )
		node.setObjectFile( 'export', output )

		proj = PSDDeckPackProject()
		proj.loadPSD( node.getAbsFilePath() )
		proj.save( output+'/', 'decks', (2048,2048) )

		#import
		jsonPath = output+'/decks.json'
		pack = jsonHelper.tryLoadJSON( jsonPath )
		for item in pack[ 'decks' ]:
			name = item['name']
			deckType = item['type']
			node.affirmChildNode( item[ 'name' ], deckType, manager = self )

		return True

DeckPSDAssetManager().register()

AssetLibrary.get().setAssetIcon( 'deck_pack',           'pack' )
AssetLibrary.get().setAssetIcon( 'deck2d.mquad',        'deck_mquad' )
AssetLibrary.get().setAssetIcon( 'deck2d.mtileset',     'deck_mtileset' )
