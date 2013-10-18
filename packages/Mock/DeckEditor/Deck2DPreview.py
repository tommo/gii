from gii.AssetEditor         import AssetPreviewer
from gii.moai.MOAIEditCanvas import MOAIEditCanvas

def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

class Deck2DPreviewer(AssetPreviewer):
	def createWidget(self, container):
		self.canvas = MOAIEditCanvas( container )
		self.canvas.loadScript( _getModulePath('Deck2DPreview.lua') )
		return self.canvas

	def accept(self, assetNode):
		return assetNode.getType() in [ 
			'deck2d.quad',
			'deck2d.stretchpatch',
			'deck2d.tileset',
			'deck2d.polygon'
			]

	def onStart(self, assetNode):
		self.canvas.safeCall( 'show', assetNode.getPath() )		
		
	def onStop(self):
		self.canvas.safeCall('show',None)

Deck2DPreviewer().register()
