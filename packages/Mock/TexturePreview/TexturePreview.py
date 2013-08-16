from gii.AssetEditor         import AssetPreviewer
from gii.moai.MOAIEditCanvas import MOAIEditCanvas

def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

class TexturePreviewer(AssetPreviewer):
	def createWidget(self, container):
		self.canvas = MOAIEditCanvas( container )
		self.canvas.loadScript( _getModulePath('TexturePreview2.lua') )
		return self.canvas

	def accept(self, assetNode):
		return assetNode.getType() in ('texture')

	def onStart(self, assetNode):
		self.canvas.safeCall( 'show', assetNode.getPath() )		
		
	def onStop(self):
		self.canvas.safeCall('show',None)

TexturePreviewer().register()
