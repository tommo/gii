from gii.core.model import *

from PropertyEditor import FieldEditor, registerFieldEditor
from gii.SearchView import requestSearchView

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

##----------------------------------------------------------------##
class CollectionFieldButton( QtGui.QToolButton ):
	def sizeHint( self ):
		return QtCore.QSize( 20, 20)

##----------------------------------------------------------------##
class CollectionFieldEditor( FieldEditor ):
	def setTarget( self, parent, field ):
		super( CollectionFieldEditor, self ).setTarget( parent, field )
		t = field.getType()
		self.targetType    = t.itemType
		self.targetContext = None  #TODO
		self.value = None

	def get( self ):
		#TODO
		pass
		
	def set( self, value ):
		self.value = value
		
	def setValue( self, value ):		
		self.set( value )
		self.notifyChanged( value )

	def initEditor( self, container ):
		self.button = CollectionFieldButton( container )
		self.button.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Expanding
			)
		self.button.setText( '[...]' )
		if self.getOption( 'readonly', False ):
			self.button.setEnabled( False )
		self.button.clicked.connect( self.openSearchView )
		return self.button

	def openSearchView( self ):
		requestSearchView( 
			context      = 'scene',
			type         = self.targetType,
			multiple_selection = True,
			on_selection = self.onSearchSelection,
			on_cancel    = self.onSearchCancel,
			initial      = self.value
			)

	def onSearchSelection( self, value ):
		self.setValue( value )
		self.setFocus()

	def onSearchCancel( self ):
		self.setFocus()

	def setFocus( self ):
		self.button.setFocus()

registerFieldEditor( CollectionType, CollectionFieldEditor )

