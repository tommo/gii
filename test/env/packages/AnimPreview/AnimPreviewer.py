from gii.core                 import *
from gii.moai.MOAIEditCanvas  import MOAIEditCanvas
from gii.AssetEditor          import AssetPreviewer
from gii.qt.helpers           import addWidgetWithLayout

from PyQt4 import uic
from PyQt4 import QtGui

def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path


class AnimPreviewer(AssetPreviewer):
	def createWidget(self, container):
		self.container=uic.loadUi( _getModulePath('AnimPreview.ui') )
		self.canvas=addWidgetWithLayout(
			MOAIEditCanvas(container),
			self.container.canvasContainer
		)

		self.listAnim = self.container.listAnim
		self.listAnim.setSortingEnabled(True)
		self.listAnim.itemSelectionChanged.connect( self.onItemSelectionChanged )

		self.container.topToolBar.hide() #not in use currently

		self.canvas.loadScript( _getModulePath('AnimPreview.lua') )
		return self.container

	def accept(self, assetNode):
		return assetNode.getType() in ('aurora_sprite')

	def onStart(self, assetNode):
		atype = assetNode.getType()
		self.listAnim.clear()
		if atype=='aurora_sprite':
			self.canvas.safeCall( 'showAuroraSprite', assetNode.getPath() )
			self.canvas.startUpdateTimer( 60 )
			animNames = self.canvas.getDelegateEnv( 'animClipNames' ) 
			if animNames:
				for i, name in animNames.items():
					self.listAnim.addItem( name )
				firstItem = self.listAnim.item( 0 )
				if firstItem: firstItem.setSelected(True)

		
	def onStop(self):
		self.canvas.stopUpdateTimer()


	def onItemSelectionChanged(self):
		for item in self.listAnim.selectedItems():
			name = item.text()
			self.canvas.safeCall( 'setAnimClip', name )

AnimPreviewer().register()

