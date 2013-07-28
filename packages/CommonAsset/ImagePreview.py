from gii.core                 import *

##----------------------------------------------------------------##
if app.getModule('asset_browser'): 
	from gii.moai.MOAIEditCanvas  import MOAIEditCanvas
	from gii.qt.helpers           import addWidgetWithLayout

	from PyQt4 import uic
	from PyQt4 import QtGui


	from gii.AssetEditor import AssetPreviewer
	from PyQt4 import QtGui, QtCore
	
	class ImagePreviewer( AssetPreviewer ):
		def createWidget(self, container):
			self.image = None
			self.scale = 1.0
			self.state = 'fit'

			self.container = uic.loadUi( app.getPath( 'data/ui/ImagePreview.ui' ) )			
			self.container.scrollArea.setStyleSheet('''
				background-color: rgb( 30, 30, 30 );
				'''
			)
			self.container.labelImage.setBackgroundRole( QtGui.QPalette.Base )
			self.container.labelImage.setSizePolicy( QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored )
			self.container.labelImage.setScaledContents( True )
			self.container.scrollArea.resizeEvent = self.onContainerResize			

			self.container.buttonFit.clicked.connect( self.fitSize )
			self.container.buttonActual.clicked.connect( self.actualSize )


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
			
			self.fitSize()

		def onStop(self):
			pass

		def fitSize( self ):
			if not self.image: return

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
			x = (aw - w)/2
			y = (ah - h)/2
			self.container.scrollInner.resize( x+w, y+h )
			self.container.labelImage.setGeometry( x, y,  w, h )
			self.state = 'fit'
			self.scale = w/iw

		def actualSize( self ):
			if not self.image: return
			
			areaSize = self.container.scrollArea.size()
			aw = areaSize.width()
			ah = areaSize.height()
			imgSize = self.image.size()
			iw = imgSize.width()
			ih = imgSize.height()
			w = iw
			h = ih
			if iw > aw:
				x = 0
			else:
				x = (aw - w)/2

			if ih > ah:
				y = 0
			else:
				y = (ah - h)/2

			self.container.labelImage.setGeometry( x, y,  w, h )
			self.container.scrollInner.resize( x + w, y + h )

			self.scale = 1.0
			self.state = 'actual'

		def onContainerResize( self, size ):
			if self.state=='actual':
				self.actualSize()
			else:
				self.fitSize()


	ImagePreviewer().register()
