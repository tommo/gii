from PropertyEditor import FieldEditor,registerFieldEditor

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
		self.setSizePolicy(
			QtGui.QSizePolicy.Fixed,
			QtGui.QSizePolicy.Fixed
			)

		self.title = option.get( 'title', 'Color' )
		self.pen = QtGui.QPen()
		self.brush = QtGui.QBrush()
		self.brush.setStyle( Qt.SolidPattern )

	def sizeHint( self ):
		return QtCore.QSize( 60, 20 )

	def getColor( self ):
		return self.color

	def setColor( self, color ):
		self.color = color
		# self.setStyleSheet('''
		# 	background-color: %s;
		# 	border: 1px solid rgb(179, 179, 179);
		# 	border-radius: 0px;
		# 	margin: 2px 0px 2px 1px;
		# 	padding: 0;
		# 	''' % color.name()
		# 	)
		self.colorChanged.emit( self.color )
		self.update()

	def paintEvent( self, event ):
		painter = QtGui.QPainter()
		painter.begin( self )
		painter.setRenderHint( QtGui.QPainter.Antialiasing )
		pen   = self.pen
		brush = self.brush
		painter.setPen( pen )
		painter.setBrush( brush )
		margin = 1
		x = margin
		y = margin
		w = self.width() - margin * 2
		h = self.height() - margin * 2
		#border
		c = QtGui.QColor( self.color )
		c.setAlpha( 255 )
		painter.setBrush( c )
		painter.setPen( QtGui.QPen( QColorF( .5,.5,.5 ) ) )
		painter.drawRect( x,y,w,h )
		#alpha
		alphaH = 4
		p2 = QtGui.QPen()
		p2.setStyle( Qt.NoPen )
		painter.setPen( p2 )
		painter.setBrush( QtGui.QBrush( QColorF( 0,0,0 ) ) )
		painter.drawRect( x + 1, y + h - alphaH ,w - 2, alphaH )
		
		painter.setBrush( QtGui.QBrush( QColorF( 1,1,1 ) ) )
		painter.drawRect( x + 1, y + h - alphaH ,( w -2 ) * self.color.alphaF(), alphaH  )


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
		if self.getOption( 'readonly', False ):
			self.colorBlock.setEnabled( False )
		return self.colorBlock

registerFieldEditor( 'color',    ColorFieldEditor )
