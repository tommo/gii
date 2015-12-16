import sys
import math
from gii.qt.controls.FlowLayout import FlowLayout
from gii.qt.controls.ElidedLabel import ElidedLabel
from gii.qt.IconCache               import getIcon

from PyQt4 import QtGui, QtCore, QtOpenGL, uic
from PyQt4.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt4.QtCore import QPoint, QRect, QSize
from PyQt4.QtCore import QPointF, QRectF, QSizeF
from PyQt4.QtGui import QColor, QTransform, QStyle, qRgb

from AssetFilter import *

##----------------------------------------------------------------##
def _getModulePath( path ):
	import os.path
	return os.path.dirname( __file__ ) + '/' + path

TagMatchCiteriaEdit,BaseClass = uic.loadUiType( _getModulePath('TagMatchCiteriaEdit.ui') )

##----------------------------------------------------------------##
class AssetFilterEditWindow( QtGui.QFrame ):
	changed   = pyqtSignal()
	cancelled = pyqtSignal()
	def __init__( self, *args ):
		super( AssetFilterEditWindow, self ).__init__( *args )
		self.ui = TagMatchCiteriaEdit()
		self.ui.setupUi( self )
		self.setWindowFlags( Qt.Dialog )
		self.installEventFilter( self )

		self.ui.buttonCancel.clicked.connect( self.onButtonCancel )
		self.ui.buttonOK.clicked.connect( self.onButtonOK )

		self.targetItem = None
		self.editSubmitted = False

	def eventFilter(self, obj, event):
		e = event.type()		
		if e == QEvent.WindowDeactivate:
			self.close()
		return False

	def setTargetItem( self, item ):
		self.targetItem = item
		self.editSubmitted = False
		self.ui.lineEditAlias.setText( item.getAlias() )
		self.ui.lineEditCiteria.setText( item.getCiteria() )
		self.ui.checkLocked.setCheckState( item.isLocked() and Qt.Checked or Qt.Unchecked )

	def _submit( self ):
		if not self.targetItem: return
		#update item
		locked  = self.ui.checkLocked.checkState() == Qt.Checked
		alias   = self.ui.lineEditAlias.text()
		citeria = self.ui.lineEditCiteria.text()
		self.targetItem.setLocked( locked )
		self.targetItem.setAlias( alias )
		self.targetItem.setCiteria( citeria)
		self.changed.emit()

	def closeEvent( self, ev ):
		super( AssetFilterEditWindow, self ).closeEvent( ev )
		if self.editSubmitted:
			self._submit()
		else:
			self.cancelled.emit()
		self.editSubmitted = False

	def onButtonCancel( self ):
		self.editSubmitted = False
		self.close()

	def onButtonOK( self ):
		self.editSubmitted = True
		self.close()



##----------------------------------------------------------------##
class AssetFilterItemWidget( QtGui.QToolButton ):
	def __init__( self, *args, **kwargs ):
		super( AssetFilterItemWidget, self ).__init__( *args, **kwargs )
		self.setObjectName( 'AssetFilterItemWidget' )
		self.setCheckable( True )
		self.setText( 'Damhill')
		self.setFixedHeight( 20 )
		self.setFocusPolicy( Qt.NoFocus )
		self.setCursor( Qt.PointingHandCursor )
		self.setMouseTracking( True )
		self.locked = False
		self.installEventFilter( self )
		self.filterItem = None

	def setTargetItem( self, item ):
		self.filterItem = item
		self.setText( item.toString() )
		self.setLocked( item.isLocked() )

	def setLocked( self, locked ):
		self.locked = locked
		if locked:
			self.setChecked( True )
		self.setProperty( 'locked', locked )
		self.setEnabled( not locked )

	def eventFilter( self, obj, ev ):
		e = ev.type()
		if e == QtCore.QEvent.MouseButtonPress:
			if ev.button() == Qt.RightButton:
				self.parent().popItemContextMenu( self )
		return False

##----------------------------------------------------------------##
class AssetFilterWidget( QtGui.QFrame ):
	def __init__( self, *args, **kwargs ):
		super( AssetFilterWidget, self ).__init__( *args, **kwargs )
		self.currentContextItem = None
		self.currentContextItemWidget = None
		self.currentNewItem = None
		
		self.editWindow = AssetFilterEditWindow( self )
		self.editWindow.hide()
		self.targetFilter = None

		self.setMinimumSize( 50, 20 )
		layout = FlowLayout( self )
		layout.setSpacing( 2 )
		layout.setMargin( 5 )

		self.buttonAdd = QtGui.QToolButton( self )
		self.buttonAdd.setFixedHeight( 20 )
		self.buttonAdd.setText( 'Add' )
		self.buttonAdd.setFocusPolicy( Qt.NoFocus )
		self.buttonAdd.clicked.connect( self.onActionAdd )
		layout.addWidget( self.buttonAdd )

		self.items = []	

		self.itemContextMenu = menu = QtGui.QMenu( 'Filter Item Context' )
		menu.addAction( 'Filter' ).setEnabled( False )
		menu.addSeparator()

		actionAdd = menu.addAction( 'Add' )
		menu.addSeparator()
		actionLock = menu.addAction( 'Toggle Lock' )
		actionEdit = menu.addAction( 'Edit' )
		menu.addSeparator()
		actionDelete = menu.addAction( 'Delete' )
		actionAdd    .triggered .connect( self.onActionAdd )
		actionLock   .triggered .connect( self.onActionLock )
		actionEdit   .triggered .connect( self.onActionEdit )
		actionDelete .triggered .connect( self.onActionDelete )
		self.editWindow.changed.connect( self.onEditChanged )
		self.editWindow.cancelled.connect( self.onEditCancelled )

	def setTargetFilter( self, targetFilter ):
		self.targetFilter = targetFilter
		self.rebuild()

	def _clear( self ):
		layout = self.layout()
		while layout.takeAt( 1 ):
			pass
		self.items = []

	def rebuild( self ):
		self._clear()
		if not self.targetFilter: return
		items = self.targetFilter.getItems()
		#sort
		for item in items:
			self._addItem( item )	

	def _removeItem( self, item ):
		pass

	def _addItem( self, item ):
		itemWidget = AssetFilterItemWidget( self )
		itemWidget.setTargetItem( item )
		self.layout().addWidget( itemWidget )
		self.items.append( item )

	def onActionAdd( self ):
		self.currentContextItem = None
		self.currentNewItem = AssetFilterItem()
		self.editWindow.setTargetItem( self.currentNewItem )
		self.editWindow.show()
		self.editWindow.raise_()
		print( 'showing edit window' )

	def onActionLock( self ):
		self.currentContextItem = None

	def onActionEdit( self ):
		self.currentContextItem = None

	def onActionDelete( self ):
		self.currentContextItem = None

	def onEditChanged( self ):
		editItem = self.editWindow.targetItem
		if self.currentNewItem == editItem:
			self.targetFilter.addItem( self.currentNewItem )
			self.currentNewItem = None
			self.rebuild()

	def onEditCancelled( self ):
		self.rebuild()



	def popItemContextMenu( self, itemWidget ):
		self.currentContextItemWidget = itemWidget
		self.currentContextItem = itemWidget.filterItem
		self.itemContextMenu.exec_( QtGui.QCursor.pos() )

	def getCurrentContextItem( self ):
		return self.currentContextItem

######TEST
if __name__ == '__main__':
	import sys
	app = QtGui.QApplication( sys.argv )
	styleSheetName = 'gii.qss'
	app.setStyleSheet(
			open( '/Users/tommo/prj/gii/data/theme/' + styleSheetName ).read() 
		)

	filter = AssetFilter()
	item   = AssetFilterItem()
	item.setAlias( 'Alias' )
	item.setCiteria( 't:test' )
	# item.setLocked( True )
	filter.addItem( item )
	widget = AssetFilterWidget()
	widget.show()
	widget.setTargetFilter( filter )
	widget.raise_()

	app.exec_()

