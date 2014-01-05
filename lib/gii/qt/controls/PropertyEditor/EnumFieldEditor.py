from gii.core.model import *

from PropertyEditor import FieldEditor, registerFieldEditor
from gii.SearchView import requestSearchView

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

# ##----------------------------------------------------------------##
# class EnumFieldEditor( FieldEditor ):
# 	def get( self ):
# 		index = self.combo.currentIndex()
# 		if index >= 0:
# 			name, value = self.enumItems[ index ]
# 		return value

# 	def set( self, value ):
# 		for i, t in enumerate( self.enumItems ):
# 			itemName, itemValue = t
# 			if value == itemValue:
# 				self.combo.setCurrentIndex( i )
# 				return
# 		self.combo.setCurrentIndex( 0 )

# 	def setTarget( self, parent, field ):
# 		super( EnumFieldEditor, self ).setTarget( parent, field )
# 		enumType = field.getType()
# 		self.enumItems = enumType.itemList[:]

# 	def onIndexChanged( self, index ):
# 		if index >= 0:
# 			name, value = self.enumItems[ index ]
# 			return self.notifyChanged( value )

# 	def initEditor( self, container ):
# 		self.combo = QtGui.QComboBox( container )
# 		self.combo.setMinimumSize( 50, 14 )
# 		for item in self.enumItems:
# 			( name, value ) = item
# 			self.combo.addItem( name, value )
# 		self.combo.currentIndexChanged.connect( self.onIndexChanged )
# 		self.combo.setSizePolicy(
# 			QtGui.QSizePolicy.Expanding,
# 			QtGui.QSizePolicy.Expanding
# 			)
# 		if self.getOption( 'readonly', False ):
# 			self.combo.setEnabled( False )
# 		return self.combo

# registerFieldEditor( EnumType, EnumFieldEditor )

class EnumFieldButton( QtGui.QToolButton ):
	def sizeHint( self ):
		return QtCore.QSize( 20, 20)

##----------------------------------------------------------------##
class EnumFieldEditor( FieldEditor ):
	def setTarget( self, parent, field ):
		super( EnumFieldEditor, self ).setTarget( parent, field )
		enumType = field.getType()
		self.enumItems = enumType.itemList[:]

	def get( self ):
		#TODO
		pass
		
	def set( self, value ):
		self.value = value
		for i, t in enumerate( self.enumItems ):
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

	def onSearch( self, typeId, context ):
		entries = []
		for item in self.enumItems:
			itemName, itemValue = item
			entry = ( itemValue, itemName, '', None )
			entries.append( entry )			
		return entries

	def setFocus( self ):
		self.button.setFocus()

registerFieldEditor( EnumType, EnumFieldEditor )
