from gii.core.model import *

from PropertyEditor import FieldEditor, registerFieldEditor

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

##----------------------------------------------------------------##
class EnumFieldEditor( FieldEditor ):
	def get( self ):
		index = self.combo.currentIndex()
		if index >= 0:
			name, value = self.enumItems[ index ]
		return value

	def set( self, value ):
		for i, t in enumerate( self.enumItems ):
			itemName, itemValue = t
			if value == itemValue:
				self.combo.setCurrentIndex( i )
				return
		self.combo.setCurrentIndex( 0 )

	def setTarget( self, parent, field ):
		super( EnumFieldEditor, self ).setTarget( parent, field )
		enumType = field.getType()
		self.enumItems = enumType.itemList[:]

	def onIndexChanged( self, index ):
		if index >= 0:
			name, value = self.enumItems[ index ]
			return self.notifyChanged( value )

	def initEditor( self, container ):
		self.combo = QtGui.QComboBox( container )
		for item in self.enumItems:
			( name, value ) = item
			self.combo.addItem( name, value )
		self.combo.currentIndexChanged.connect( self.onIndexChanged )
		self.combo.setSizePolicy(
			QtGui.QSizePolicy.Expanding,
			QtGui.QSizePolicy.Expanding
			)
		return self.combo

registerFieldEditor( EnumType, EnumFieldEditor )
