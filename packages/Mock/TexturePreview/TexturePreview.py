from gii.AssetEditor         import AssetPreviewer
from mock.editor import MOCKEditCanvas

def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

class TexturePreviewer(AssetPreviewer):
	def createWidget(self, container):
		self.canvas = MOCKEditCanvas( container )
		self.canvas.loadScript( _getModulePath('TexturePreview.lua') )
		return self.canvas

	def accept(self, assetNode):
		return assetNode.getType() in ('texture','sub_texture','texpack', 'deck_quadlists')

	def onStart(self, assetNode):
		atype = assetNode.getType()
		if   atype == 'texture':
			self.canvas.safeCall( 'showTexture', assetNode.getPath() )

		elif atype == 'texpack':
			self.canvas.safeCall('showAtlas',
				assetNode.getPath()
				)

		elif atype == 'sub_texture':
			atlasNode = assetNode.getParent()
			self.canvas.safeCall('showSubTexture',
				atlasNode.getPath(),
				assetNode.getName()
				)
			
		elif atype == 'deck_quadlists':
			atlasNode = assetNode.getParent()
			self.canvas.safeCall('showQuadLists',
				assetNode.getPath()
				)
		
	def onStop(self):
		self.canvas.safeCall('setTexture',None)

TexturePreviewer().register()
