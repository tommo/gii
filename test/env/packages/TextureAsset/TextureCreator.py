import os.path
import json

from gii.AssetBrowser import AssetCreator

class TexpackCreator( AssetCreator ):
	def createAsset(self, name, contextNode, assetType):
		ext      = '.texpack'
		filename = name + ext
		if contextNode.isType('folder'):
			nodepath = contextNode.getChildPath(filename)
		else:
			nodepath = contextNode.getSiblingPath(filename)

		fullpath = AssetLibrary.get().getAbsPath(nodepath)
		data={
			'_assetType' : 'texpack',
			'atlases'    : [],
			'items'      : [],
			'settings'   : {}
		}
		if os.path.exists(fullpath):
			raise Exception('File already exist:%s'%fullpath)

		fp = open(fullpath,'w')
		json.dump(data, fp, sort_keys=True,indent=2)
		fp.close()
		return nodepath

TexpackCreator().register()

