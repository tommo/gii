from gii.core import *
from gii.core.model import *

from gii.qt.controls.ColorPickerWidget import ColorPickerWidget
from gii.qt.helpers    import addWidgetWithLayout, restrainWidgetToScreen
from gii.qt.IconCache  import getIcon

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QEventLoop, QEvent, QObject, QPoint
from PyQt4.QtGui import QColor, QTransform, QStyle, qRgb

##----------------------------------------------------------------##
class WindowAutoHideEventFilter(QObject):
	def eventFilter(self, obj, event):
		e = event.type()		
		if e == QEvent.KeyPress and event.key() == Qt.Key_Escape:
			obj.hide()
		elif e == QEvent.WindowDeactivate:
			obj.hide()

		return QObject.eventFilter( self, obj, event )


class ColorPickerDialog( ColorPickerWidget ):
	def __init__( self, *args ):
		self.onCancel  = None
		self.onChange  = None
		self.onChanged = None
		self.cancelled = False

		super(ColorPickerDialog, self).__init__( *args )
		self.installEventFilter( WindowAutoHideEventFilter( self ) )
		self.setWindowTitle( 'Colors' )
	
	def request( self, **option ):
		self.onCancel  = None
		self.onChange  = None
		self.onChanged = None
		original = option.get( 'original_color', None )
		if original:
			self.setColor( QColor( original ) )
			self.setOriginalColor( original )

		self.onCancel  = option.get( 'on_cancel',  None )
		self.onChange  = option.get( 'on_change',  None )
		self.onChanged = option.get( 'on_changed', None )

		pos       = option.get( 'pos', QtGui.QCursor.pos() )
		self.move( pos + QPoint( -50, 0 ) )
		restrainWidgetToScreen( self )
		self.show()
		self.raise_()
		self.cancelled = False

	def onButtonOK( self ):
		if self.onChanged:
			self.onChanged( self.currentColor )
		self.hide()

	def onButtonCancel( self ):
		self.cancelled = True
		self.hide()

	def onColorChange( self, color ):
		if self.onChange:
			self.onChange( color )

	def hideEvent( self, ev ):
		if self.cancelled and self.onCancel:
			self.onCancel()
		self.onCancel  = None
		self.onChange  = None
		self.onChanged = None


##----------------------------------------------------------------##
_colorPickerDialog = None
def requestColorDialog( title = None, **option ):
	global _colorPickerDialog
	if not _colorPickerDialog:
		_colorPickerDialog = ColorPickerDialog( None )
	if title:
		_colorPickerDialog.setWindowTitle( title or 'Color Picker' )
	_colorPickerDialog.request( **option )
	return _colorPickerDialog
