import os
import os.path
import json

from gii.core           import *
from gii.AssetEditor    import AssetCreator

class StyleSheetCreator( AssetCreator ):
	def getAssetType( self ):
		return 'stylesheet'

	def getLabel( self ):
		return 'Style Sheet'

	def createAsset(self, name, contextNode, assetType):
		ext = '.stylesheet'
		filename = name + ext

		if contextNode.isType( 'folder' ):
			nodepath = contextNode.getChildPath(filename)
			print nodepath
		else:
			nodepath = contextNode.getSiblingPath(filename)

		fullpath = AssetLibrary.get().getAbsPath( nodepath )
		data={
			'_assetType':'stylesheet', #checksum
			'styles':[]
		}
		print fullpath
		if os.path.exists( fullpath ):
			raise Exception( 'File already exist: %s' % fullpath )
		fp = open( fullpath, 'w' )
		json.dump(data, fp, sort_keys=True,indent=2)
		fp.close()
		return nodepath


StyleSheetCreator().register()