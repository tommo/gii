from gii.core                 import *
from gii.moai.MOAIEditCanvas  import MOAIEditCanvas
from gii.AssetBrowser         import AssetPreviewer
from gii.qt.helpers           import addWidgetWithLayout

from PyQt4 import uic
from PyQt4 import QtGui

##----------------------------------------------------------------##
if app.getModule('asset_browser'): 

	from gii.AssetBrowser import AssetPreviewer
	from PyQt4 import QtGui, QtCore
	
	class ImagePreviewer( AssetPreviewer ):
		def createWidget(self, container):
			self.scale = 1.0
			self.container = uic.loadUi( app.getPath( 'data/ui/ImagePreview.ui' ) )			
			self.container.scrollArea.setStyleSheet('''
				background-color: rgb( 30, 30, 30 );
				'''
			)
			self.container.labelImage.setBackgroundRole( QtGui.QPalette.Base )
			self.container.labelImage.setSizePolicy( QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored )
			self.container.labelImage.setScaledContents( True )
			self.container.scrollArea.resizeEvent = self.onContainerResize

			return self.container

		def accept(self, assetNode):
			return assetNode.getType() in ('image')

		def onStart(self, assetNode):
			filepath = assetNode.getAbsFilePath()
			image = QtGui.QImage( filepath )
			if image.isNull():
				return
			self.container.labelImage.setPixmap( QtGui.QPixmap.fromImage(image) )
			self.image = image
			self.state = 'fit'
			self.fitSize()

		def onStop(self):
			pass

		def fitSize( self ):
			areaSize = self.container.scrollArea.size()
			aw = areaSize.width()
			ah = areaSize.height()
			imgSize = self.image.size()
			iw = imgSize.width()
			ih = imgSize.height()
			
			if ah * iw/ih < aw:
				w = ah * iw/ih
				h = ah
			else:
				w = aw	
				h = aw * ih/iw

			self.container.labelImage.setGeometry( (aw - w)/2, (ah - h)/2,  w, h )
			self.state = 'fit'
			self.scale = w/iw

		def actualSize( self ):
			areaSize = self.container.scrollArea.size()
			aw = areaSize.width()
			ah = areaSize.height()
			imgSize = self.image.size()
			iw = imgSize.width()
			ih = imgSize.height()
			w = iw
			h = ih
			self.container.labelImage.setGeometry( (aw - w)/2, (ah - h)/2,  w, h )
			self.scale = 1.0
			self.state = 'actual'

		def onContainerResize( self, size ):
			self.fitSize()


	ImagePreviewer().register()
