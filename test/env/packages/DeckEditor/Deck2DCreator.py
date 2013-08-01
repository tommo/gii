import os.path
import json

from gii.core           import *
from gii.AssetEditor import AssetCreator


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
		
Deck2DCreator().register()