import sys
import math

from PyQt4 import QtGui, QtCore, QtOpenGL, uic
from PyQt4.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt4.QtCore import QPoint, QRect, QSize
from PyQt4.QtCore import QPointF, QRectF, QSizeF
from PyQt4.QtGui import QColor, QTransform, QStyle, qRgb

##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path



ColorPickerForm,BaseClass = uic.loadUiType( _getModulePath('ColorPicker.ui') )

def clampOne( v ):
	return min( 1.0, max( 0.0, v ) )

def generateHSVImage( w, h, hue, img = None ):
	if not img:
		img = QtGui.QImage( w, h, QtGui.QImage.Format_RGB32 )
	du = 1.0/w
	dv = 1.0/h
	c = QColor()
	for y in range( 0, h ):
		for x in range( 0, w ):
			s = du * x
			v = 1.0 - dv * y
			c.setHsvF( hue, s, v )
			img.setPixel( x, y, c.rgb() )
	return img

#####
class ColorPreviewWidget( QtGui.QWidget ):
	originalColorClicked = pyqtSignal()

	def __init__( self, parent ):
		super( ColorPreviewWidget, self ).__init__( parent )
		self.setFixedSize( parent.width(), parent.height() )
		self.previewColor = Qt.red
		self.originalColor = Qt.black

	def setColor( self, color ):
		self.previewColor = color

	def setOriginalColor( self, color ):
		self.originalColor = color

	def paintEvent( self, event ):
		painter = QtGui.QPainter( self )
		painter.setPen( Qt.NoPen )
		w = self.width()
		h = self.height()
		painter.setBrush( self.originalColor )
		painter.drawRect( 0,   0, w, h/2    )
		cSolid = QColor( self.previewColor )
		cSolid.setAlphaF( 1 )
		#left 1/2 for solid color
		painter.setBrush( cSolid )
		painter.drawRect( 0, h/2, w/2, h/2 + 1 )
		#draw chekerGrid
		x0 = w/2
		y0 = h/2
		w2 = w/2
		h2 = h/2
		painter.setBrush( Qt.white )
		painter.drawRect( x0, y0, w2, h2 )
		painter.setBrush( QColor.fromRgbF( 0.5, 0.5, 0.5 ) )
		for y in range( 4 ):
			for x in range( w2/10 ):
				if (x % 2) == (y % 2):
					painter.drawRect( x0 + x * 10, y0 + y * 10, 10, 10 )

		#right 2/3 for color with alpha
		painter.setBrush( self.previewColor )
		painter.drawRect( x0, y0, w2+1, h2 + 1 )

#####
class ColorPlaneWidget( QtGui.QWidget ):
	valueXChanged = pyqtSignal( float )
	valueYChanged = pyqtSignal( float )
	valueZChanged = pyqtSignal( float )
	valueChanged = pyqtSignal( float, float, float )

	def __init__( self, parent ):
		super( ColorPlaneWidget, self ).__init__( parent )
		self.setFixedSize( parent.width(), parent.height() )
		self.setCursor( Qt.PointingHandCursor )
		self.valueX = 0.0
		self.valueY = 0.0
		self.valueZ = 0.0 #Hue for hsv; 

		self.dragging = False

		self.updateImage()

	def setValue( self, x, y, z ):
		x = clampOne( x )
		y = clampOne( y )
		z = clampOne( z )
		self.valueX = x
		self.valueY = y
		if z != self.valueZ:
			self.valueZ = z
			self.updateImage()
		self.update()
		self.valueChanged.emit( self.valueX, self.valueY, self.valueZ )

	def getValue( self ):
		return ( self.valueX, self.valueY, self.valueZ )

	def setValueZ( self, value ):
		if self.valueZ != value:
			self.setValue( self.valueX, self.valueY, value )

	def setValueXY( self, x, y ):
		return self.setValue( x, y, self.valueZ )

	def getValueXY( self ):
		return ( self.valueX, self.valueY )

	def getValueZ( self ):
		return self.valueZ

	def updateImage( self ):
		self.colorImage = generateHSVImage( 20, 20, self.valueZ )
		self.colorImage = self.colorImage.scaled( 100, 100, Qt.IgnoreAspectRatio, Qt.SmoothTransformation )

	def paintEvent(self, event):
		painter = QtGui.QPainter(self)
		# painter.setRenderHint( QtGui.QPainter.Antialiasing, True )
		painter.setRenderHint( QtGui.QPainter.SmoothPixmapTransform, True )
		painter.drawImage( event.rect(), self.colorImage )
		x = self.valueX * self.width()
		y = self.valueY * self.height()
		painter.setBrush( Qt.NoBrush )
		painter.setPen( Qt.black )
		painter.drawRect( x-4, y-4, 8, 8 )
		painter.setPen( Qt.white )
		painter.drawRect( x-3, y-3, 6, 6 )

	def mousePressEvent( self, event ):
		if event.button() == Qt.LeftButton:
			self.grabMouse()
			vx = float(event.x())/float(self.width())
			vy = float(event.y())/float(self.height())
			self.setValueXY( vx, vy )
			self.dragging = True

	def mouseReleaseEvent( self, event ):
		if event.button() == Qt.LeftButton:
			self.releaseMouse()
			self.dragging = False

	def mouseMoveEvent( self, event ):
		if not self.dragging: return
		vx = float(event.x())/float(self.width())
		vy = float(event.y())/float(self.height())
		self.setValueXY( vx, vy )

#####
class AlphaSliderWidget( QtGui.QWidget ):
	valueChanged = pyqtSignal( float )

	def __init__( self, parent ):
		super( AlphaSliderWidget, self ).__init__( parent )
		self.setFixedSize( parent.width(), parent.height() )
		self.setCursor( Qt.PointingHandCursor )
		self.value = 0
		size = 100
		self.colorImage = QtGui.QImage( size, 1, QtGui.QImage.Format_RGB32 )
		c = QColor()
		for x in range( 0, size ):
			k = x/float(size)
			c.setHsvF( 1.0, 0.0, k )
			self.colorImage.setPixel( x, 0, c.rgb() )

	def setValue( self, value ):
		value = clampOne( value )
		if value == self.value: return
		self.value = value
		self.valueChanged.emit( value )
		self.update()

	def paintEvent(self, event):
		painter = QtGui.QPainter(self)
		painter.setRenderHint( QtGui.QPainter.SmoothPixmapTransform, True )
		painter.drawImage( event.rect(), self.colorImage )
		#draw cursor
		h = self.height()
		x = self.value * self.width()
		painter.setBrush( Qt.NoBrush )
		painter.setPen( Qt.black )
		painter.drawRect( x-3, 0, 6, h-1 )
		painter.setPen( Qt.white )
		painter.drawRect( x-2, 0, 4, h-1 )

	def mousePressEvent( self, event ):
		if event.button() == Qt.LeftButton:
			self.grabMouse()
			x = float(event.x())
			k = x/float(self.width())
			self.setValue( k )

	def mouseReleaseEvent( self, event ):
		if event.button() == Qt.LeftButton:
			self.releaseMouse()

	def mouseMoveEvent( self, event ):
		if self.mouseGrabber() != self: return
		x = float(event.x())
		k = x/float(self.width())
		self.setValue( k )


#####
class HueSliderWidget( QtGui.QWidget ):
	valueChanged = pyqtSignal( float )

	def __init__( self, parent ):
		super( HueSliderWidget, self ).__init__( parent )
		self.setFixedSize( parent.width(), parent.height() )
		self.value = 0
		size = 100
		self.colorImage = QtGui.QImage( 1, size, QtGui.QImage.Format_RGB32 )
		c = QColor()
		for y in range( 0, size ):
			k = y/float(size)
			c.setHsvF( k, 1.0, 1.0 )
			self.colorImage.setPixel( 0, y, c.rgb() )
		self.setCursor( Qt.PointingHandCursor )

	def setValue( self, value ):
		value = clampOne( value )
		if value == self.value: return
		self.value = value
		self.valueChanged.emit( value )
		self.update()

	def paintEvent(self, event):
		painter = QtGui.QPainter(self)
		painter.setRenderHint( QtGui.QPainter.SmoothPixmapTransform, True )
		painter.drawImage( event.rect(), self.colorImage )
		#draw cursor
		w = self.width()
		y = self.value * self.height()
		painter.setBrush( Qt.NoBrush )
		painter.setPen( Qt.black )
		painter.drawRect( 0, y-3, w -1, 6 )
		painter.setPen( Qt.white )
		painter.drawRect( 0, y-2, w -1, 4 )

	def mousePressEvent( self, event ):
		if event.button() == Qt.LeftButton:
			self.grabMouse()
			y = float(event.y())
			k = y/float(self.height())
			self.setValue( k )

	def mouseReleaseEvent( self, event ):
		if event.button() == Qt.LeftButton:
			self.releaseMouse()

	def mouseMoveEvent( self, event ):
		if self.mouseGrabber() != self: return
		y = float(event.y())
		k = y/float(self.height())
		self.setValue( k )


class ScreenColorPicker( QtGui.QWidget ):
	def __init__( self, parent = None ):
		super(ScreenColorPicker, self).__init__( parent )
		self.setFixedSize( 5, 5 )
		self.setMouseTracking( True )
		self.setFocusPolicy( Qt.StrongFocus )
		self.setWindowFlags( Qt.Popup )
		
		self.setWindowModality( Qt.ApplicationModal )

		self.timer = QtCore.QTimer( self )
		self.timer.setInterval( 10 )
		self.timer.timeout.connect( self.onTimer )
		self.timer.start()
		self.setCursor( Qt.CrossCursor)

		self.pixmap = QtGui.QPixmap.grabWindow( QtGui.QApplication.desktop().winId() )
		self.image  = self.pixmap.toImage()
		self.owner = False

	def setOwner( self, owner ):
		self.owner = owner

	def onTimer( self ):
		pos = QtGui.QCursor.pos()
		self.move( pos.x()-2, pos.y()-2 )

	def mouseMoveEvent( self, event ):
		pos = event.globalPos()
		rgb = self.image.pixel( pos )
		color = QColor.fromRgb( rgb )
		if self.owner:
			self.owner.setColor( color )

	def mousePressEvent( self, event ):
		self.close()
		self.deleteLater()

	def paintEvent( self, event ):
		painter = QtGui.QPainter( self )
		color = QColor.fromRgbF( 0, 0, 0 )
		# color.setAlphaF( 0.5 )
		painter.setPen( Qt.NoPen )
		painter.setBrush( color )
		painter.drawRect( event.rect() )
		

#####
class ColorPickerWidget( QtGui.QWidget ):
	def __init__( self, *args ):
		super(ColorPickerWidget, self).__init__( *args )
		self.updating = False
		self.updatingAlpha = False
		self.ui = ColorPickerForm()
		self.ui.setupUi( self )

		self.setWindowFlags( Qt.Popup )

		self.preview     = ColorPreviewWidget( self.ui.containerPreview )
		self.hueSlider   = HueSliderWidget( self.ui.containerHueSlider )
		self.alphaSlider = AlphaSliderWidget( self.ui.containerAlphaSlider )

		self.colorPlane  = ColorPlaneWidget( self.ui.containerColorPlane )

		self.hueSlider   .valueChanged .connect( self.onHueChanged )
		self.alphaSlider .valueChanged .connect( self.onAlphaSliderChanged )
		self.colorPlane  .valueChanged .connect( self.onColorBaseChanged )

		self.ui.buttonOK      .clicked .connect( self.onButtonOK )
		self.ui.buttonCancel  .clicked .connect( self.onButtonCancel )
		self.ui.buttonCopyHEX .clicked .connect( self.onButtonCopyHEX )
		self.ui.buttonCopyRGB .clicked .connect( self.onButtonCopyRGBA )
		self.ui.buttonCopyHSV .clicked .connect( self.onButtonCopyHSV )

		self.ui.buttonScreenPick.clicked.connect( self.onButtonScreenPick )

		self.ui.numR.valueChanged.connect( self.onTextRGBChanged )
		self.ui.numG.valueChanged.connect( self.onTextRGBChanged )
		self.ui.numB.valueChanged.connect( self.onTextRGBChanged )

		self.ui.numH.valueChanged.connect( self.onTextHSVChanged )
		self.ui.numS.valueChanged.connect( self.onTextHSVChanged )
		self.ui.numV.valueChanged.connect( self.onTextHSVChanged )

		self.ui.numA.valueChanged.connect( self.onAlphaSliderChanged )

		self.originalColor = QColor.fromRgbF( 0.0, 0.0, 0.0 )
		self.currentColor  = QColor.fromRgbF( 1.0, 1.0, 0.0 )

		self.preview.setColor( self.currentColor )
		self.preview.setOriginalColor( self.originalColor )

		self.updateAlphaWidgets()
		self.updateTextWidgets()
		self.updateColorPlane()

		# self.screenPicker.grabMouse()

	def setColor( self, color ):
		self.currentColor = color
		self.updateTextWidgets()
		self.updateColorPlane()
		self.updateAlphaWidgets()
		self.onColorChange( color )

	def setOriginalColor( self, color ):
		self.originalColor = QColor( color )
		self.preview.setOriginalColor( self.originalColor )

	def setAlpha( self, alpha ):
		self.currentColor.setAlphaF( alpha )
		self.updateAlphaWidgets()
		self.onColorChange( self.currentColor )

	def updateAlphaWidgets( self ):
		if self.updatingAlpha: return
		self.updatingAlpha = True
		alpha = self.currentColor.alphaF()
		self.ui.numA.setValue( alpha )
		self.alphaSlider.setValue( alpha )
		self.preview.update()
		self.updatingAlpha = False

	def updateColorPlane( self ):
		if self.updating: return
		self.updating = True
		color = self.currentColor
		s = color.saturationF()
		v = color.valueF()
		h = color.hueF()
		self.colorPlane.setValue( s, 1.0 - v, h )
		self.hueSlider.setValue( h )
		self.updating = False

	def updateTextWidgets( self ):
		if self.updating: return
		self.updating = True

		color = self.currentColor

		self.preview.setColor( color )
		self.preview.update()
		#update fields
		self.ui.numR.setValue( color.redF() )
		self.ui.numG.setValue( color.greenF() )
		self.ui.numB.setValue( color.blueF() )

		self.ui.numH.setValue( color.hueF() * 360 )
		self.ui.numS.setValue( color.saturationF() )
		self.ui.numV.setValue( color.valueF() )

		self.ui.textHex.setText( color.name() )

		self.updating = False

	def onButtonOK( self ):
		pass

	def onButtonCancel( self ):
		pass

	def onColorChange( self, color ):
		pass

	def onButtonCopyHEX( self ):
		print 'copy hex'

	def onButtonCopyRGBA( self ):
		print 'copy rgba'

	def onButtonCopyHSV( self ):
		print 'copy hsv'

	def onButtonScreenPick( self ):
		self.screenPicker = ScreenColorPicker( None )
		self.screenPicker.setOwner( self )
		self.screenPicker.show()
		self.screenPicker.raise_()

	def onHueChanged( self, value ):
		if self.updating: return
		self.colorPlane.setValueZ( value )

	def onAlphaSliderChanged( self, value ):
		self.setAlpha( value )

	def onColorBaseChanged( self, x,y,z ):
		if self.updating: return
		hue, s, v = z, x, 1.0 - y
		color = QColor.fromHsvF( hue, s, v )
		color.setAlphaF( self.currentColor.alphaF() )
		self.setColor( color )

	def onTextRGBChanged( self, value ):
		if self.updating: return
		r = self.ui.numR.value()
		g = self.ui.numG.value()
		b = self.ui.numB.value()
		color = QColor.fromRgbF( r,g,b )
		color.setAlphaF( self.currentColor.alphaF() )
		self.setColor( color )
		self.updateColorPlane()

	def onTextHSVChanged( self, value ):
		if self.updating: return
		h = float( self.ui.numH.value() ) / 360.0
		s = self.ui.numS.value()
		v = self.ui.numV.value()
		color = QColor.fromHsvF( h, s, v )
		color.setAlphaF( self.currentColor.alphaF() )
		self.setColor( color )
		self.updateColorPlane()


######TEST
if __name__ == '__main__':
	import sys
	app = QtGui.QApplication( sys.argv )
	styleSheetName = 'gii.qss'
	app.setStyleSheet(
			open( '/Users/tommo/prj/gii/data/theme/' + styleSheetName ).read() 
		)

	widget = ColorPickerWidget()
	widget.show()
	widget.raise_()

	app.exec_()

