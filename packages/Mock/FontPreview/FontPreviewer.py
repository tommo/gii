from gii.core                 import *
from gii.moai.MOAIEditCanvas  import MOAIEditCanvas
from gii.AssetEditor          import AssetPreviewer
from gii.qt.helpers           import addWidgetWithLayout

from PyQt4 import uic
from PyQt4 import QtGui

def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

class FontPreviewer(AssetPreviewer):
	def createWidget(self, container):
		self.container = uic.loadUi( _getModulePath('FontPreview.ui') )

		self.canvas = addWidgetWithLayout(
			MOAIEditCanvas(container),
			self.container.canvasContainer
		)
		self.canvas.loadScript( _getModulePath('FontPreview.lua') )

		self.container.textPreview.textChanged.connect( self.onTextChanged )
		self.container.spinFontSize.valueChanged.connect( self.onSizeChanged )

		return self.container

	def accept(self, assetNode):
		return assetNode.getType() in ('font_ttf','font_bmfont','font_bdf')

	def onStart(self, assetNode):
		atype=assetNode.getType()
		self.canvas.safeCall( 'setFont', assetNode.getPath().encode( 'utf-8' ) )
		self.container.spinFontSize.setValue( 
			self.canvas.getDelegateEnv('currentFontSize') 
			)
		self.container.textPreview.setPlainText( 
			self.canvas.getDelegateEnv('currentText').decode('utf-8')
			)

	def onStop(self):
		self.canvas.safeCall('setFont',None)

	def onTextChanged(self):
		text = self.container.textPreview.toPlainText()
		self.canvas.safeCall( 'setText', text )

	def onSizeChanged(self, size):
		self.canvas.safeCall( 'setFontSize', size )
		

FontPreviewer().register()
