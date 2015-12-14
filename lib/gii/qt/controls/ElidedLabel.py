from PyQt4            import QtCore, QtGui, uic
from PyQt4.QtCore     import Qt

class ElidedLabel( QtGui.QLabel ):
	def paintEvent( self, event ):
		painter = QtGui.QPainter( self )
		metrics = QtGui.QFontMetrics( self.font() )
		elided  = metrics.elidedText( self.text(), Qt.ElideLeft, self.width() )
		painter.drawText( self.rect(), self.alignment(), elided )

	def minimumSizeHint( self ):
		return QtGui.QWidget.minimumSizeHint( self )
