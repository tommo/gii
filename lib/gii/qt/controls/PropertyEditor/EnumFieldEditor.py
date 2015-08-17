from gii.core.model import *

from PropertyEditor import FieldEditor, FieldEditorFactory, registerSimpleFieldEditorFactory
from gii.SearchView import requestSearchView

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

class EnumFieldButton( QtGui.QToolButton ):
	def sizeHint( self ):
		return QtCore.QSize( 20, 20)

##----------------------------------------------------------------##
class EnumFieldEditor( FieldEditor ):
	def setTarget( self, parent, field ):
		super( EnumFieldEditor, self ).setTarget( parent, field )
		self.enumType = field.getType()

	def getEnumItems( self ):
		return self.enumType.getItemList( self.getTarget() )

	def get( self ):
		#TODO
		pass
		
	def set( self, value ):
		self.value = value
		for i, t in enumerate( self.getEnumItems() ):
			itemName, itemValue = t
			if value == itemValue:
				self.button.setText( itemName )
				return
		self.button.setText('')

	def setValue( self, value ):		
		self.set( value )
		self.notifyChanged( value )

	def initEditor( self, container ):
		self.button = EnumFieldButton( container )
		self.button.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Expanding
			)
		self.button.setText( '[]' )
		if self.getOption( 'readonly', False ):
			self.button.setEnabled( False )
		self.button.clicked.connect( self.openSearchView )
		return self.button

	def openSearchView( self ):
		requestSearchView( 
			context      = 'scene',
			type         = None,
			multiple_selection = False,
			on_selection = self.onSearchSelection,
			on_cancel    = self.onSearchCancel,
			on_search    = self.onSearch,
			initial      = self.value
			)

	def onSearchSelection( self, value ):
		self.setValue( value )
		self.setFocus()

	def onSearchCancel( self ):
		self.setFocus()

	def onSearch( self, typeId, context, option ):
		entries = []
		for item in self.getEnumItems():
			itemName, itemValue = item
			entry = ( itemValue, itemName, '', None )
			entries.append( entry )
		return entries

	def setFocus( self ):
		self.button.setFocus()

registerSimpleFieldEditorFactory( EnumType, EnumFieldEditor )
