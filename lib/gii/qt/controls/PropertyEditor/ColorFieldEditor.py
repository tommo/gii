from PropertyEditor import FieldEditor

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

def unpackQColor( c ):
	return ( c.redF(), c.greenF(), c.blueF(), c.alphaF() )

def QColorF( r, g, b, a =1 ):
	return QtGui.QColor( r*255, g*255, b*255, a*255)

def requestColor(prompt, initColor = None, **kwargs):
	dialog = QtGui.QColorDialog( initColor or QtCore.Qt.white )
	dialog.setOption( QtGui.QColorDialog.ShowAlphaChannel, True )
	dialog.move( QtGui.QCursor.pos() )
	dialog.setWindowTitle( prompt )
	onColorChanged = kwargs.get( 'onColorChanged', None )
	if onColorChanged:
		dialog.currentColorChanged.connect( onColorChanged )
	if dialog.exec_() == 1:
		col = dialog.currentColor()
		dialog.destroy()
		if col.isValid(): return col
	return initColor

class ColorBlock( QtGui.QToolButton ):
	colorChanged = QtCore.pyqtSignal( QtGui.QColor )
	def __init__(self, parent, color = None, **option ):
		super(ColorBlock, self).__init__( parent )
		self.setColor( color or QtGui.QColor( 1,1,1,1 ) )
		self.clicked.connect( self.onClicked )
		self.setMinimumSize( 10, 10 )
		self.setSizePolicy(
			QtGui.QSizePolicy.Fixed,
			QtGui.QSizePolicy.Fixed
			)
		self.title = option.get( 'title', 'Color' )

	def getColor( self ):
		return self.color

	def setColor( self, color ):
		self.color = color
		self.setStyleSheet('''
			background-color: %s;
			border: 1px solid rgb(179, 179, 179);
			border-radius: 0px;
			margin: 5px 0px 5px 1px;
			padding: 0;
			''' % color.name()
			)
		self.colorChanged.emit( self.color )

	def onClicked( self ):		
		color = requestColor( self.title, self.color, onColorChanged = self.setColor )
		self.setColor( color )

##----------------------------------------------------------------##
class ColorFieldEditor( FieldEditor ):
	def get( self ):
		return unpackQColor( self.colorBlock.getColor() )

	def set( self, value ):
		self.colorBlock.setColor( QColorF( *value ) )

	def onColorChanged( self, state ):
		return self.notifyChanged( self.get() )

	def initEditor( self, container ):
		self.colorBlock = ColorBlock( container )
		self.colorBlock.colorChanged.connect( self.onColorChanged )
		return self.colorBlock
	