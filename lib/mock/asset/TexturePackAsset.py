import os.path
from gii.core import AssetManager
import json

class TexturePackAssetManager(AssetManager):
	def getName(self):
		return 'asset_manager.texpack'

	def acceptAssetFile(self, filepath):
		if not os.path.isfile(filepath): return False		
		name,ext=os.path.splitext(filepath)
		if not ext in ('.texpack'): return False
		try:
			f=open(filepath,'r')
			data=json.load(f)
			f.close()
			if not data: return False
		except Exception, e:
			return False
		if not (data.has_key('atlases') and data.has_key('items')): return False
		return True

	def importAsset(self, node, option=None):
		node.assetType='texpack'
		try:
			f=open(node.getAbsFilePath(),'r')
			data=json.load(f)
			f.close()
		except Exception, e:
			return False
		lib=AssetLibrary.get()
		atlases=data['atlases']
		items=data['items']
		#import atlas textures, make dependency link
		atlasNodes=[]
		for atlasName in atlases:
			atlasPath=node.getSiblingPath(atlasName)
			anode=lib.importAsset(atlasPath)
			atlasNodes.append(anode)
			node.addDependencyR(anode) #Runtime dependency
		#create subnodes for items
		basePath=node.getPath()
		for item in items:
			node.createChildNode(item['name'], 'sub_texture', 
					manager=self
				)
		return True

	# def reimportAsset(self, node, option=None):
	# 	lib=AssetLibrary.get()
	# 	for n in node.getChildren()[:]:
	# 		lib.unregisterAssetNode(n)
	# 	return self.importAsset(node, option)


	def editAsset(self, node):	
		packer=App.get().getModule('moai.texture_packer')
		if not packer: return
		packer.setFocus()
		if node.getType()=='texpack': 
			packer.edit(node)
		else:
			packer.edit(node.getParent(), node)


TexturePackAssetManager().register()
